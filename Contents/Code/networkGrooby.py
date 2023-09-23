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

            dateNode = detailsPageElements.xpath('//div[@class="setdesc"]//b[contains(., "Added")]//following-sibling::text()')
            if dateNode:
                date = dateNode[0].split('-', 1)[-1].strip()
                if date:
                    releaseDate = parse(date).strftime('%Y-%m-%d')

            if searchData.date and releaseDate:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    title = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//h3 | //div[@class="trailer_toptitle_left"]')[0].text_content().strip()
    metadata.title = PAutils.parseTitle(title, siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p | //div[@class="trailerpage_info"]/p[not(@class)]')[-1].text_content()

    # Studio
    metadata.studio = 'Grooby'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    dateNode = detailsPageElements.xpath('//div[@class="setdesc"]/*[contains(., "Added")]//following-sibling::text() | //div[@class="trailer_videoinfo"]/*[contains(., "Added")]//following-sibling::text()')
    if dateNode:
        date = dateNode[0].split('-', 1)[-1].strip()

        if date:
            date_object = parse(date)
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p[contains(., "Featuring")]//a | //div[@class="setdesc"]//a[contains(@href, "/models/")]'):
        actorName = actorLink.text_content().strip()

        actorURL = actorLink.get('href')
        if actorURL.startswith('//'):
            actorURL = 'http:' + actorURL
        elif not actorURL.startswith('http'):
            actorURL = PAsearchSites.getSearchBaseURL(siteNum) + actorURL

        req = PAutils.HTTPRequest(actorURL)
        actorPageElements = HTML.ElementFromString(req.text)

        actorPhotoURL = ''
        photoNode = actorPageElements.xpath('//div[@class="model_photo"]//img[@id]/@src0_1x | //div[@class="model_photo"]/img/@src')
        if photoNode:
            actorPhotoURL = photoNode[0]

            if not actorPhotoURL.startswith('http'):
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@class="trailerpage_photoblock_fullsize"]//a/@href',
        '//div[@class="trailerposter"]//img/@src0_4x',
        '//div[@class="player-thumb"]//img/@src0_4x',
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            if not poster.startswith('http'):
                poster = PAsearchSites.getSearchBaseURL(siteNum) + poster

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
