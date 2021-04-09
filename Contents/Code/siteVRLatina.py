import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    maybeDirectURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.title.replace(' ', '-').lower() + '.html'

    searchResults = [maybeDirectURL]
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if ('/video/' in sceneURL and sceneURL not in searchResults):
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        if req.status_code == 200:
            detailsPageElements = HTML.ElementFromString(req.text)

            if detailsPageElements:
                curID = PAutils.Encode(sceneURL)
                titleNoFormatting = detailsPageElements.xpath('//meta[@property="og:title"]/@content')[0]

                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//meta[@property="og:title"]/@content')[0]

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[(contains(@class, "content-desc"))]')[0].text_content().strip()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="content-base-info"]//div[@class="info-elem -length"]/span')[
        0].text_content().strip()
    if date:
        date_object = datetime.strptime(date, '%b %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//meta[@property="keywords"]/@content'):
        genreName = genreLink.split(",")

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//div[(contains(@class, "content-links -models"))]/a'):
        actorName = actorLink.get("title")

        actorPageURL = actorLink.get('href')

        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        actorPhotoURL = actorPage.xpath('//div[(contains(@class, "model-avatar"))]/div/img/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters/Background
    art = []
    xpaths = [
        '//div//a[@class="video-gallery-item"]/@href',
        '//meta[@property="og:image"]/@content'
    ]

    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            if poster.startswith("//"):
                poster = poster[2:]

            art.append(poster)

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
                if width > 100 and idx > 1:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
