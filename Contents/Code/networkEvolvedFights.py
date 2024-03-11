import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    directURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.title.replace(' ', '-').lower() + '.html'

    searchResults = [directURL]
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if ('/updates/' in sceneURL and sceneURL not in searchResults):
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        if detailsPageElements:
            curID = PAutils.Encode(sceneURL)
            titleNoFormatting = detailsPageElements.xpath('//title')[0].text_content().strip()
            date = detailsPageElements.xpath('//span[(contains(@class, "update_date"))]')[0].text_content().strip()
            releaseDate = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//title')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//span[(contains(@class, "latest_update_description"))]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Evolved Fights Network'

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Genres
    for genreLink in detailsPageElements.xpath('//span[(contains(@class, "tour_update_tags"))]/a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[(contains(@class, "update_block_info model_update_block_info"))]/span[(contains(@class, "tour_update_models"))]/a'):
        actorName = actorLink.text_content().strip()
        actorPageURL = actorLink.get('href')

        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPage.xpath('//img[(contains(@class, "model_bio_thumb stdimage thumbs target"))]/@src0_3x')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Release Date
    date = detailsPageElements.xpath('//span[@class="update_date"]')[0].text_content().strip()
    date_object = datetime.strptime(date, '%m/%d/%Y')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Posters/Background
    poster = PAsearchSites.getSearchBaseURL(siteNum) + '/' + detailsPageElements.xpath('//span[(contains(@class, "model_update_thumb"))]/img/@src0_4x')[0]
    art.append(poster)

    poster2 = poster.replace('0-4x', '1-4x')
    art.append(poster2)

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
