import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchResultsURLs = []
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)

    if searchData.title.count(' ') > 1:
        directSearch = searchData.title.replace(' ', '-').lower()
    else:
        directSearch = searchData.title.replace(' ', '')

    searchResultsURLs.append('%s/models/%s.html' % (PAsearchSites.getSearchBaseURL(siteNum), directSearch))

    for searchResultURL in googleResults:
        if searchResultURL not in searchResultsURLs:
            if '/models/' in searchResultURL:
                searchResultsURLs.append(searchResultURL)

    for modelURL in searchResultsURLs:
        req = PAutils.HTTPRequest(modelURL)
        pageElements = HTML.ElementFromString(req.text)
        for sceneResult in pageElements.xpath('//div[contains(@class, "latest-updates")]//div[@data-setid]'):
            titleNoFormatting = PAutils.parseTitle(sceneResult.text_content().split(':', 1)[-1].strip(), siteNum)
            sceneLink = sceneResult.xpath('.//a[@class="updateimg"]/@href')[0]
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
    metadata.collections.clear()
    for seriesName in [metadata.studio, PAsearchSites.getSearchSiteName(siteNum)]:
        metadata.collections.add(seriesName)

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
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[contains(@class, "video-info")]//a[contains(@href, "/categories/")]/text()'):
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
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
