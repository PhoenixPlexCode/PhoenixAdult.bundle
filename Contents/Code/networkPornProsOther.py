import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    directURL = '%s%s' % (PAsearchSites.getSearchSearchURL(siteNum), slugify(searchData.title).lower())

    searchResults = [directURL]
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if ('/feed/' not in sceneURL and 'tag' not in sceneURL and not sceneURL == PAsearchSites.getSearchSearchURL(siteNum) and sceneURL not in searchResults):
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        if detailsPageElements and not req.url == PAsearchSites.getSearchBaseURL(siteNum):
            curID = PAutils.Encode(sceneURL)
            titleNoFormatting = detailsPageElements.xpath('//h2')[0].text_content().strip()
            date = detailsPageElements.xpath('//span[./img[@id="time-single"]]')

            if date:
                parseDate = date[0].text_content().strip()
                parseDate = re.sub(r'(st|nd|rd|th)', '', parseDate)
                releaseDate = datetime.strptime(parseDate, '%B %d, %Y').strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''

            displayDate = releaseDate if date else ''

            if searchData.date and displayDate:
                score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h2')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[@class="more"]')[0].text_content().split('Description:')[-1].strip()

    # Studio
    metadata.studio = 'PornPros'

    # Studio/Tagline/Collection
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//div[@id="title-single"]/a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Release Date
    date = detailsPageElements.xpath('//span[./img[@id="time-single"]]')
    if date:
        parseDate = date[0].text_content().strip()
        parseDate = re.sub(r'(st|nd|rd|th)', '', parseDate)
        date_object = parse(parseDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Posters
    xpaths = [
        '//video/@poster'
    ]

    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
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
