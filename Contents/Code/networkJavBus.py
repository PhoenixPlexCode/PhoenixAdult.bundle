import PAsearchSites
import PAutils

cookies = {
    'existmag': 'all',
}


def search(results, lang, siteNum, searchData):
    searchJAVID = None
    splitSearchTitle = searchData.title.split()
    if len(splitSearchTitle) > 1:
        if unicode(splitSearchTitle[1], 'UTF-8').isdigit():
            searchJAVID = '%s%%2B%s' % (splitSearchTitle[0], splitSearchTitle[1])
            directJAVID = '%s-%s' % (splitSearchTitle[0], splitSearchTitle[1])

    if searchJAVID:
        searchData.encoded = searchJAVID

    searchTypes = [
        'Censored',
        'Uncensored',
    ]

    for searchType in searchTypes:
        if searchType == 'Uncensored':
            sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + 'uncensored/search/' + searchData.encoded
        elif searchType == 'Censored':
            sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + 'search/' + searchData.encoded

        req = PAutils.HTTPRequest(sceneURL, cookies=cookies)
        searchResults = HTML.ElementFromString(req.text)
        for searchResult in searchResults.xpath('//a[@class="movie-box"]'):
            titleNoFormatting = searchResult.xpath('.//span[1]')[0].text_content().replace('\t', '').replace('\r\n', '').strip()
            JAVID = searchResult.xpath('.//date[1]')[0].text_content().strip()

            sceneURL = searchResult.xpath('./@href')[0]
            curID = PAutils.Encode(sceneURL)

            if searchJAVID:
                score = 100 - Util.LevenshteinDistance(searchJAVID.lower(), JAVID.lower())
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='[%s][%s] %s' % (searchType, JAVID, titleNoFormatting), score=score, lang=lang))

    if directJAVID:
        sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + directJAVID
        req = PAutils.HTTPRequest(sceneURL, cookies=cookies)
        searchResult = HTML.ElementFromString(req.text)
        javTitle = searchResult.xpath('//head/title')[0].text_content().strip().replace(' - JavBus', '')
        if directJAVID.replace('-', '').replace('_', '').replace(' ', '').isdigit():
            javTitle = javStudio + ' ' + javTitle
        curID = PAutils.Encode(sceneURL)
        score = 100
        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='[Direct][%s] %s' % (directJAVID, javTitle), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL, cookies=cookies)
    detailsPageElements = HTML.ElementFromString(req.text)
    JAVID = sceneURL.rsplit('/', 1)[1]

    # Title
    javStudio = detailsPageElements.xpath('//p/a[contains(@href, "/studio/")]')[0].text_content().strip()
    javTitle = detailsPageElements.xpath('//head/title')[0].text_content().strip().replace(' - JavBus', '')
    if JAVID.replace('-', '').replace('_', '').replace(' ', '').isdigit():
        javTitle = javStudio + ' ' + javTitle
    metadata.title = javTitle

    # Studio
    metadata.studio = javStudio

    # Director
    director = metadata.directors.new()
    directorName = detailsPageElements.xpath('//p/a[contains(@href, "/director/")]')
    if directorName:
        director.name = directorName[0].text_content().strip()

    #  Tagline and Collection(s)
    metadata.collections.clear()
    data = {}

    label = detailsPageElements.xpath('//p/a[contains(@href, "/label/")]')
    if label:
        data['Label'] = label[0].text_content().strip()

    series = detailsPageElements.xpath('//p/a[contains(@href, "/series/")]')
    if series:
        data['Series'] = series[0].text_content().strip()

    metadata.tagline = ', '.join(['%s: %s' % (key, value) for key, value in data.items()])
    if label:
        metadata.tagline = label[0].text_content().strip()
        metadata.collections.add(metadata.tagline)
    else:
        metadata.collections.add(metadata.studio)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="col-md-3 info"]/p[2]')[0].text_content().strip().replace('Release Date: ', '')
    if date != '0000-00-00':
        date_object = datetime.strptime(date, '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//span[@class="genre"]//a[contains(@href, "/genre/")]'):
        genreName = genreLink.text_content().lower().strip()
        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//a[@class="avatar-box"]'):
        fullActorName = actorLink.xpath('./div/img/@title')[0]
        actorPhotoURL = detailsPageElements.xpath('//a[@class="avatar-box"]/div[@class="photo-frame"]/img[contains(@title, "%s")]/@src' % (fullActorName))[0]
        if not actorPhotoURL.startswith('http'):
            actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

        if actorPhotoURL.rsplit('/', 1)[1] == 'nowprinting.gif':
            actorPhotoURL = ''

        movieActors.addActor(fullActorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//a[contains(@href, "/cover/")]/@href',
        '//a[@class="sample-box"]/@href',
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            if not poster.startswith('http'):
                poster = PAsearchSites.getSearchBaseURL(siteNum) + poster

            art.append(poster)

    coverImage = detailsPageElements.xpath('//a[contains(@href, "/cover/")]/@href')
    coverImageCode = coverImage[0].rsplit('/', 1)[1].split('.')[0].split('_')[0]
    imageHost = coverImage[0].rsplit('/', 2)[0]
    coverImage = imageHost + '/thumb/' + coverImageCode + '.jpg'
    if coverImage.count('/images.') == 1:
        coverImage = coverImage.replace('thumb', 'thumbs')

    if not coverImage.startswith('http'):
        coverImage = PAsearchSites.getSearchBaseURL(siteNum) + coverImage

    art.append(coverImage)

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                im = StringIO(image.content)
                images.append(image)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                    posterExists = True
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    if not posterExists:
        for idx, image in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[art[idx - 1]] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
