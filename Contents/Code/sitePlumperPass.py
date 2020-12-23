import PAsearchSites
import PAgenres
import PAactors
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):
    searchResults = []

    url = PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle + '&sid=587'
    req = PAutils.HTTPRequest(url)
    siteSearchResults = HTML.ElementFromString(req.text)
    for searchResult in siteSearchResults.xpath('//div[@class="itemm"]'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + '/tour/%s' % searchResult.xpath('.//@href')[0]

        searchResults.append(sceneURL)

    googleResults = PAutils.getFromGoogleSearch(searchTitle, siteNum)
    for result in googleResults:
        pattern = re.compile(r'(?<=\dpp\/).*(?=\/)')
        if pattern.match(result):
            sceneID = pattern.search(result).group(0)
            sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/refstat.php?lid=%s&sid=584' % sceneID

            if ('content' in result) and sceneURL not in searchResults:
                searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        try:
            titleNoFormatting = detailsPageElements.xpath('//h1[@id="mve"]/span')[0].text_content().strip()
            curID = PAutils.Encode(sceneURL)
            date = detailsPageElements.xpath('//div[@class="movie-date"]')[0].text_content().strip()

            if date:
                releaseDate = parse(date).strftime('%Y-%m-%d')
            else:
                releaseDate = parse(searchDate).strftime('%Y-%m-%d') if searchDate else ''
            displayDate = releaseDate if date else ''

            if searchDate and displayDate:
                score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))
        except:
            pass

    return results


def update(metadata, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@id="mve"]/span')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="movie-desc"]')[0].text_content().strip()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = metadata.studio
    metadata.collections.add(metadata.studio)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[@class="movie-tags"]//a[@href]'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[@id="pornstar-img"]')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.xpath('.//@alt')[0].strip()
            actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/%s' % actorLink.xpath('.//@src')[0].strip()

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []
    xpaths = [
        '//div[@class="movie-trailer"]//@src',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if 'http' not in img:
                img = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/%s' % img

            art.append(img)

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.google.com'})
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
