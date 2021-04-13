import PAutils
import PAsearchSites


def search(results, lang, siteNum, searchData):
    searchResults = []

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        sceneURL = sceneURL.split('?', 1)[0]
        if '/trailers/' in sceneURL and sceneURL not in searchResults:
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        if req.ok:
            detailsPageElements = HTML.ElementFromString(req.text)

            curID = PAutils.Encode(sceneURL)
            titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//h3 | //div[@class="trailer_toptitle_left"]')[0].text_content().strip(), siteNum)
            releaseDate = ''

            dateNode = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p[contains(., "Added")] | //div[@class="setdesc"]')
            if dateNode:
                date = None
                try:
                    date = dateNode[0].text_content().split('-')[-1].strip()
                except:
                    pass

                if date:
                    releaseDate = parse(date).strftime('%Y-%m-%d')

            if searchData.date and releaseDate:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//h3 | //div[@class="trailer_toptitle_left"]')[0].text_content().strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p | //div[@class="trailerpage_info"]/p[not(@class)]')[-1].text_content()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p[contains(., "Added")] | //div[@class="setdesc"]')[0].text_content().split('-')[-1].strip()
    if date:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p[contains(., "Featuring")]//a | //div[@class="setdesc"]//a'):
        actorName = actorLink.text_content().strip()

        actorURL = actorLink.get('href')
        if not actorURL.startswith('http'):
            actorURL = PAsearchSites.getSearchBaseURL(siteNum) + actorURL

        req = PAutils.HTTPRequest(actorURL)
        actorPageElements = HTML.ElementFromString(req.text)
        actorPhotoURL = actorPageElements.xpath('(//div[@class="model_photo"]//img[@id]/@src0_1x | //div[@class="model_photo"]/img/@src)')[0]
        if not actorPhotoURL.startswith('http'):
            actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []
    xpaths = [
        '//div[@class="trailerpage_photoblock_fullsize"]//a/@href'
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            if not poster.startswith('http'):
                poster = PAsearchSites.getSearchBaseURL(siteNum) + '/tour/' + poster

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
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
