import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.lower().replace(' ', '-')
    directURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded + '.html'

    searchResults = [directURL]
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if '/trailers/' in sceneURL and sceneURL not in searchResults:
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        if not req.text == 'Page not found':
            detailsPageElements = HTML.ElementFromString(req.text)
            titleNoFormatting = detailsPageElements.xpath('//meta[@name="twitter:title"]/@content')[0].strip()
            curID = PAutils.Encode(sceneURL)

            date = detailsPageElements.xpath('//div[@class="trailer topSpace"]/div[2]/p')[0].text_content().split('\\')[1].strip()
            releaseDate = parse(date).strftime('%Y-%m-%d')

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title, titleNoFormatting)

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [GirlsOutWest] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//meta[@name="twitter:title"]')[0].get('content').strip()

    # Studio
    metadata.studio = 'GirlsOutWest'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="trailer topSpace"]/div[2]/p')[0].text_content().split('\\')[1].strip()
    if date:
        date_object = datetime.strptime(date, '%m/%d/%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.addGenre('Amateur')
    movieGenres.addGenre('Australian')

    # Actor(s)
    actors = detailsPageElements.xpath('//div[@class="trailer topSpace"]/div[2]/p/a')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content().strip()

            actorPageURL = actorLink.get('href')
            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPage.xpath('//div[@class="profilePic"]/img/@src0_3x')[0]

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@class="videoplayer"]/img/@src0_3x'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(PAsearchSites.getSearchBaseURL(siteNum) + img)

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
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
