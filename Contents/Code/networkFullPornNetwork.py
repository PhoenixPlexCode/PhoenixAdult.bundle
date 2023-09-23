import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    modelResultsURLs = []
    searchResultsURLs = []
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)

    if searchData.title.count(' ') > 1:
        directSearch = searchData.title.replace(' ', '-').lower()
    else:
        directSearch = searchData.title.replace(' ', '')

    modelResultsURLs.append('%s/models/%s.html' % (PAsearchSites.getSearchBaseURL(siteNum), directSearch))

    for modelResultsURL in googleResults:
        if modelResultsURL not in modelResultsURLs:
            if '/models/' in modelResultsURL and 'models_' not in modelResultsURL and 'join' not in modelResultsURL:
                modelResultsURLs.append(modelResultsURL)

    for searchResultURL in googleResults:
        if searchResultURL not in searchResultsURLs:
            if '/trailers/' in searchResultURL:
                searchResultsURLs.append(searchResultURL)

    for sceneLink in searchResultsURLs:
        req = PAutils.HTTPRequest(sceneLink)
        detailsPageElements = HTML.ElementFromString(req.text)

        if req.ok:
            titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1[contains(@class, "title_bar")]')[0].text_content().split(':', 1)[-1].strip(), siteNum)
            curID = PAutils.Encode(sceneLink)

            date = detailsPageElements.xpath('//div[@class="video-info"]//p')
            if date:
                releaseDate = parse(date[0].text_content().strip()).strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''

            displayDate = releaseDate if date else ''

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [FPN/%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    for modelURL in modelResultsURLs:
        req = PAutils.HTTPRequest(modelURL)
        modelPageElements = HTML.ElementFromString(req.text)

        if modelPageElements.xpath('//a[contains(@class, "pagenav")]'):
            pages = 3
        else:
            pages = 2

        for idx in range(1, pages):
            if idx == 2:
                nextPage = modelPageElements.xpath('//a[contains(@class, "pagenav")]/@href')[0]
                req = PAutils.HTTPRequest(nextPage)
                modelPageElements = HTML.ElementFromString(req.text)

            for sceneResult in modelPageElements.xpath('//div[contains(@class, "latest-updates")]//div[@data-setid]'):
                sceneLink = sceneResult.xpath('.//a[@class="updateimg"]/@href')[0]

                if sceneLink not in searchResultsURLs:
                    titleNoFormatting = PAutils.parseTitle(sceneResult.text_content().split(':', 1)[-1].strip(), siteNum)
                    curID = PAutils.Encode(sceneLink)

                    releaseDate = searchData.dateFormat() if searchData.date else ''

                    score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                    results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [FPN/%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    sceneDate = metadata_id[2]

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1[contains(@class, "title_bar")]')[0].text_content().split(':', 1)[-1].strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "video-description")]/p[@class="description-text"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Full Porn Network'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="video-info"]//p')
    if date:
        date_object = datetime.strptime(date[0].text_content().strip(), '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//div[contains(@class, "video-info")]//a[contains(@href, "/categories/")]/text()'):
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[contains(@class, "video-info")]//a[contains(@href, "/models/")]'):
        actorName = actorLink.text_content().strip()
        actorLink = actorLink.xpath('./@href')[0].strip()

        req = PAutils.HTTPRequest(actorLink)
        actorPageElements = HTML.ElementFromString(req.text)
        actorPhotoURL = actorPageElements.xpath('//img[@alt="model"]/@src0_3x')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//video/@poster'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if 'http' not in img:
                img = PAsearchSites.getSearchBaseURL(siteNum) + img

            art.append(img.replace('-1x.jpg', '-3x.jpg'))

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
