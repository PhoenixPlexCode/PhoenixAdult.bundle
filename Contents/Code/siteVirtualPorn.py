import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchResults = []
    urlRegEx = re.compile(r'/video[0-9]+/')

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if urlRegEx.search(sceneURL):
            searchResults.append(sceneURL)

    searchResults = list(dict.fromkeys([sceneURL.replace('www.', '', 1) for sceneURL in searchResults]))

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        if 'signup.' not in req.url:
            detailsPageElements = HTML.ElementFromString(req.text)
            titleNoFormatting = detailsPageElements.xpath('//h3[@class="player__info__title"]')[0].text_content().strip()
            curID = PAutils.Encode(sceneURL)

            releaseDate = ''
            date = detailsPageElements.xpath('//p[contains(text(), "Released:")]')
            if date:
                date_object = parse(date[0].text_content().split(':')[1].strip())
                releaseDate = date_object.strftime('%Y-%m-%d')

            if searchData.date and releaseDate:
                score = 100 - Util.LevenshteinDistance(searchData.dateFormat(), releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

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
    metadata.title = detailsPageElements.xpath('//h3[@class="player__info__title"]')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[@class="player__description hide--tablet"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Bang Bros'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    genres = detailsPageElements.xpath('//meta[@name="keywords"]/@content')[0]
    for genreLink in genres.split(','):
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//p[@class="player__stats__cast"]/a'):
        actorName = actorLink.text_content().strip()
        actorPageSlug = actorLink.get('href')
        req = PAutils.HTTPRequest(PAsearchSites.getSearchBaseURL(siteNum) + actorPageSlug)
        actorPage = HTML.ElementFromString(req.text)
        actorPhotoURL = actorPage.xpath('//img[@class="model__img"]/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//dl8-video/@poster',
        '//img[@class="player__thumbs__img"]/@src',
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
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
