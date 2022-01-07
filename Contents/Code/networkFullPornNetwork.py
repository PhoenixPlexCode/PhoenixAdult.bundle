import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchResultsURLs = []
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)

    for searchResultURL in googleResults:
        if searchResultURL not in searchResultsURLs:
            if '/models/' in searchResultURL:
               searchResultsURLs.append(searchResultURL)

    for modelURL in searchResultsURLs:
        req = PAutils.HTTPRequest(modelURL)
        pageElements = HTML.ElementFromString(req.text)
        for sceneResult in pageElements.xpath('//div[contains(@class, "latest-updates")]//div[@data-setid]'):
            sceneLink = sceneResult.xpath('.//div[contains(@class, "text-info")]//a[contains(@class, "text-sm")]')[0]
            curID = PAutils.Encode(sceneLink.xpath('./@href')[0])
            titleNoFormatting = sceneLink.text_content().strip()
            poster = PAutils.Encode(sceneResult.xpath('.//a[@class="updateimg"]//img/@src0_3x')[0])
            releaseDate = sceneResult.xpath('.//div[contains(@class, "video-data")]/span[2]')[0].text_content()

            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s|%s' % (curID, siteNum, releaseDate, poster), name='%s [FPN/%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    sceneDate = metadata_id[2]
    scenePoster = PAutils.Decode(metadata_id[3]) if len(metadata_id) > 3 else None
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[contains(@class, "title_bar")]')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "video-description")]/p[@class="description-text"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Full Porn Network'

    # Tagline and Collection(s)
    metadata.collections.clear()
    for seriesName in [metadata.studio, PAsearchSites.getSearchSiteName(siteNum)]:
        metadata.collections.add(seriesName)

    # Release Date
    if sceneDate:
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
    for actorLink in detailsPageElements.xpath('//div[contains(@class, "video-info")]//a[contains(@href, "/models/")]/@href'):
        Log('actorLink: %s' % actorLink)
        req = PAutils.HTTPRequest(actorLink)
        actorPage = HTML.ElementFromString(req.text)
        actorName = actorPage.xpath('//h1')[0].text_content().strip()
        actorPhotoURL = actorPage.xpath('//img[@alt="model"]/@src0_3x')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []
    if scenePoster:
        art.append(scenePoster)

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
