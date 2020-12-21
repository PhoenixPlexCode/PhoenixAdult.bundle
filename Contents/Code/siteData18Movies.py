import PAsearchSites
import PAgenres
import PAactors
import PAextras
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):
    searchResults = []
    siteResults = []
    temp = []
    count = 0

    sceneID = None
    splited = searchTitle.split(' ')
    if unicode(splited[0], 'UTF-8').isdigit():
        sceneID = splited[0]
        searchTitle = searchTitle.replace(sceneID, '', 1).strip()
        movieURL = '%s/movies/%s' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID)
        searchResults.append(movieURL)

    encodedTitle = searchTitle.replace(' ', '+')
    searchURL = '%s%s' % (PAsearchSites.getSearchSearchURL(siteNum), encodedTitle)
    req = PAutils.HTTPRequest(searchURL, headers={'Referer': 'http://www.data18.com'})
    searchPageElements = HTML.ElementFromString(req.text)

    for searchResult in searchPageElements.xpath('//a[contains(@href, "movies")]//parent::div[contains(@style, "float: left; padding")]'):
        movieURL = searchResult.xpath('.//*[img]/@href')[0]
        urlID = re.sub(r'.*/', '', movieURL)

        if movieURL not in searchResults:
            req = PAutils.HTTPRequest(movieURL, headers={'Referer': 'http://www.data18.com'})
            detailsPageElements = HTML.ElementFromString(req.text)

            try:
                siteName = detailsPageElements.xpath('//i[contains(., "Studio")]//preceding-sibling::a[1]')[0].text_content().strip()
            except:
                siteName = ''

            titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//*[contains(@href, "movies")]')[1].text_content(), siteNum)
            curID = PAutils.Encode(movieURL)
            siteResults.append(movieURL)

            date = searchResult.text

            if date and not date == 'unknown':
                releaseDate = datetime.strptime(date, '%Y%m%d').strftime('%Y-%m-%d')
            else:
                releaseDate = parse(searchDate).strftime('%Y-%m-%d') if searchDate else ''
            displayDate = releaseDate if date else ''

            if sceneID == urlID:
                score = 100
            elif searchDate and displayDate:
                score = 80 - Util.LevenshteinDistance(searchDate, releaseDate)
            else:
                score = 80 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

            if score == 80:
                count += 1
                temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, siteName, displayDate), score=score, lang=lang))
            else:
                results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, siteName, displayDate), score=score, lang=lang))

    googleResults = PAutils.getFromGoogleSearch(searchTitle, siteNum)
    for movieURL in googleResults:
        if ('/movies/' in movieURL and '.html' not in movieURL and movieURL not in searchResults and movieURL not in siteResults):
            searchResults.append(movieURL)

    for movieURL in searchResults:
        req = PAutils.HTTPRequest(movieURL)
        detailsPageElements = HTML.ElementFromString(req.text)
        urlID = re.sub(r'.*/', '', movieURL)

        try:
            siteName = detailsPageElements.xpath('//i[contains(., "Studio")]//preceding-sibling::a[1]')[0].text_content().strip()
        except:
            siteName = ''

        titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)
        curID = PAutils.Encode(movieURL)

        try:
            date = detailsPageElements.xpath('//p[contains(., "Release")]')[0].text_content().text_content().split(':')[2].strip()
        except:
            date = ''

        if date and not date == 'unknown':
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = parse(searchDate).strftime('%Y-%m-%d') if searchDate else ''
        displayDate = releaseDate if date else ''

        if sceneID == urlID:
            score = 100
        elif searchDate and displayDate:
            score = 80 - Util.LevenshteinDistance(searchDate, releaseDate)
        else:
            score = 80 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

        if score == 80:
            count += 1
            temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, siteName, displayDate), score=score, lang=lang))
        else:
            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, siteName, displayDate), score=score, lang=lang))

    for result in temp:
        if count > 1 and result.score == 80:
            results.Append(MetadataSearchResult(id=result.id, name=result.name, score=79, lang=lang))
        else:
            results.Append(MetadataSearchResult(id=result.id, name=result.name, score=result.score, lang=lang))

    return results


def update(metadata, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="gen12"]/p[contains(., "Description")]')[0].text_content().split(':', 1)[1].strip()

    # Studio
    try:
        studio = detailsPageElements.xpath('//i[contains(., "Studio")]//preceding-sibling::a[1]')[0].text_content().strip()
    except:
        studio = ''

    metadata.studio = studio

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//a[./b[contains(., "Categories")]]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[./p[span[@class="gen11"]]]//a')
    if actors:
        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            if actorName:
                actorPhotoURL = ''

                movieActors.addActor(actorName, actorPhotoURL)

    # Director
    director = metadata.directors.new()
    try:
        directorName = detailsPageElements.xpath('//p[./b[contains(., "Director")]]')[0].text_content().split(':')[2]
        if not directorName == 'unknown':
            director.name = directorName
    except:
        pass

    # Posters
    art = []
    xpaths = [
        '//a[@data-featherlight="image"]/@href',
        '//img[contains(@src, "th5")]/@src',
    ]

    try:
        for xpath in xpaths:
            for img in detailsPageElements.xpath(xpath):
                art.append(img.replace('/th5', ''))
    except:
        pass

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.data18.com'})
                images.append(image)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    posterExists = True
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
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
