import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.replace(' ', '-')
    searchResultsURLs = []
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if sceneURL not in searchResultsURLs:
            if ('/updates/' in sceneURL and '/tour_hwxxx/' in sceneURL) and sceneURL not in searchResultsURLs:
                searchResultsURLs.append(sceneURL)

    for sceneURL in searchResultsURLs:
        req = PAutils.HTTPRequest(sceneURL)
        if req.ok:
            try:
                searchResult = HTML.ElementFromString(req.text)

                titleNoFormatting = \
                searchResult.xpath('//div[@class="trailerInfo"]/h2')[
                    0].text_content().strip()
                releaseDate = parse(searchResult.xpath('//div[@class="trailerInfo"]/div[@class="released2 trailerStarr"]')[
                    0].text_content().strip().split(",")[0]).strftime('%Y-%m-%d')
                curID = PAutils.Encode(sceneURL)

                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())
                if releaseDate == searchData.date:
                    score = 100

                results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum),
                                                    name='%s [HotwifeXXX] %s' % (titleNoFormatting, releaseDate), score=score,
                                                    lang=lang))
            except:
                pass

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'HotwifeXXX'

    actors = []

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="trailerInfo"]/h2')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="dvdDescription"]/p')[0].text_content().replace('description: ', '').strip()

    # Tagline and Collection(s)
    metadata.collections.add(PAsearchSites.getSearchSiteName(siteNum))

    # No genres for scenes

    # Release Date
    date = detailsPageElements.xpath('//div[@class="trailerInfo"]/div[@class="released2 trailerStarr"]')[
                    0].text_content().strip().split(",")[0]
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Actors
    actors = detailsPageElements.xpath('//div[@class="trailerMInfo"]//span[@class="tour_update_models"]/a')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

    # Posters
    try:
        art.append(detailsPageElements.xpath('//span[@id="trailer_thumb"]//img/@src')[0].strip())
    except:
        pass

    for actorLink in actors:
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        try:
            actorPageURL = actorLink.get('href')
            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            actorPhotoURL = actorPage.xpath('//div[@class="modelBioPic"]/img/@src0_3x')[0]
        except:
            pass

        movieActors.addActor(actorName, actorPhotoURL)

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
