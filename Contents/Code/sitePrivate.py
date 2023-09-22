import PAsearchSites
import PAutils

supported_lang = ['en', 'de', 'fr', 'es', 'nl']


def search(results, lang, siteNum, searchData):
    url = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded

    headers = {}
    if lang in supported_lang:
        headers['Accept-Language'] = lang

    req = PAutils.HTTPRequest(url, headers=headers)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//ul[@id="search_results"]//li[@class="card"]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//h3/a')[0].text_content().strip(), siteNum)
        curID = PAutils.Encode(searchResult.xpath('.//h3/a/@href')[0])

        date = searchResult.xpath('.//span[@class="scene-date"]')
        if date:
            releaseDate = parse(date[0].text_content().strip()).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if searchData.date and displayDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Private] %s' % (titleNoFormatting, displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieCastCrew, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL

    headers = {}
    if lang in supported_lang:
        headers['Accept-Language'] = lang

    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL, headers=headers)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//meta[@itemprop="description"]/@content')[0]

    # Studio
    metadata.studio = 'Private'

    # Tagline and Collection(s)
    try:
        tagline = detailsPageElements.xpath('//li[@class="tag-sites"]//a')[0].text_content()
    except:
        tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//li[@class="tag-tags"]//a'):
        genreName = genreLink.text_content().lower()

        movieGenres.addGenre(genreName)

    # Release Date
    date_object = None

    date = detailsPageElements.xpath('//meta[@itemprop="uploadDate"]/@content')
    if date:
        date_object = parse(date[0])
    elif sceneDate:
        date_object = parse(sceneDate)

    if date_object:
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actor(s)
    movieCastCrew.clearActors()
    for actorPage in detailsPageElements.xpath('//li[@class="tag-models"]//a'):
        actorName = actorPage.text_content()

        modelURL = actorPage.xpath('./@href')[0]
        req = PAutils.HTTPRequest(modelURL)
        modelPageElements = HTML.ElementFromString(req.text)

        actorPhotoURL = modelPageElements.xpath('//img/@srcset')[0].split(',')[-1].split(' ')[1].strip()

        movieCastCrew.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//meta[@itemprop="thumbnailUrl"]/@content',
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            art.append(poster)

    sceneId = sceneURL.split('/')[-1]
    galleryPageUrl = 'https://www.private.com/gallery.php?type=highres&id=' + sceneId + '&langx=en'
    galleryReq = PAutils.HTTPRequest(galleryPageUrl, headers=headers)
    galleryPageElements = HTML.ElementFromString(galleryReq.text)
    for poster in galleryPageElements.xpath('//a/@href'):
        art.append(poster)

    backgrounds = detailsPageElements.xpath('//meta[@itemprop="contentURL"]/@content')[0]
    j = backgrounds.rfind('upload/')
    k = backgrounds.rfind('trailers/')
    sceneID = backgrounds[j + 7:k - 1].split('/')[-1]
    backgrounds = backgrounds[:k] + 'Fullwatermarked/'
    for i in range(1, 10):
        img = backgrounds + sceneID.lower() + '_' + '{0:0=3d}'.format(i * 5) + '.jpg'
        img = img.replace('pcoms', 'pcom')

        art.append(img)

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
