import PAsearchSites
import PAutils


def getDataFromAPI(url, req_type, query):
    headers = {
        'Authorization': 'Basic YmFuZy1yZWFkOktqVDN0RzJacmQ1TFNRazI=',
        'Content-Type': 'application/json'
    }
    params = json.dumps({'query': {'bool': {'must': [{'match': {req_type: query}}], 'must_not': [{'match': {'type': 'trailer'}}]}}, 'size': '25'})
    data = PAutils.HTTPRequest(url, headers=headers, params=params).json()

    return data


def search(results, lang, siteNum, searchData):
    searchResults = getDataFromAPI(PAsearchSites.getSearchSearchURL(siteNum), 'name', searchData.title)['hits']['hits']
    for searchResult in searchResults:
        searchResult = searchResult['_source']
        titleNoFormatting = PAutils.parseTitle(searchResult['name'], siteNum)
        studioScene = PAutils.parseTitle(searchResult['studio']['name'], siteNum)
        seriesScene = PAutils.parseTitle(searchResult['series']['name'], siteNum)
        curID = searchResult['identifier']
        releaseDate = parse(searchResult['releaseDate']).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='[%s] %s' % (seriesScene if seriesScene else studioScene, titleNoFormatting), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneID = metadata_id[0]

    detailsPageElements = getDataFromAPI(PAsearchSites.getSearchSearchURL(siteNum), 'identifier', sceneID)['hits']['hits'][0]['_source']

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['name'], siteNum)

    # Summary
    metadata.summary = detailsPageElements['description']

    # Studio
    metadata.studio = re.sub(r'bang(?=(\s|$))(?!\!)', 'Bang!', PAutils.parseTitle(detailsPageElements['studio']['name'], siteNum), flags=re.IGNORECASE)

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = re.sub(r'bang(?=(\s|$))(?!\!)', 'Bang!', PAutils.parseTitle(detailsPageElements['series']['name'], siteNum), flags=re.IGNORECASE)
    if tagline:
        metadata.tagline = tagline
        metadata.collections.add(tagline)
    else:
        metadata.collections.add(metadata.studio)

    # Release Date
    date = detailsPageElements['releaseDate']
    date_object = datetime.strptime(date, '%Y-%m-%d')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements['actors']:
        actorName = actorLink['name']
        actorPhotoURL = 'https://i.bang.com/pornstars/%d.jpg' % actorLink['id']

        if actorName:
            movieActors.addActor(actorName, actorPhotoURL)

    # Manually Add Actors
    actors = []
    for key, value in actorsDB.items():
        if key == sceneID:
            movieActors.clearActors()
            actors = value
            break

    for actorLink in actors:
        actorName = actorLink[0]
        actorPhotoURL = 'https://i.bang.com/pornstars/%d.jpg' % int(actorLink[1])

        movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements['genres']:
        genreName = genreLink['name']

        movieGenres.addGenre(genreName)

    # Posters
    dvdID = detailsPageElements['dvd']['id'] if 'dvd' in detailsPageElements else detailsPageElements['identifier']
    art.append('https://i.bang.com/covers/%d/front.jpg' % dvdID)

    if 'screenshots' in detailsPageElements:
        for img in detailsPageElements['screenshots']:
            art.append('https://i.bang.com/screenshots/%d/movie/1/%d.jpg' % (dvdID, int(img['screenId'])))

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                im = StringIO(image.content)
                images.append(image)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                    posterExists = True
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    if not posterExists:
        for idx, image in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[art[idx - 1]] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


actorsDB = {
    '173946': [('La Sirena 69', '38477')],
}
