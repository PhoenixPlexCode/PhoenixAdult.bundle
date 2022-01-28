import PAsearchSites
import PAutils


def getGraphQL(queryType, variable, query):
    params = json.dumps({'query': queryType, 'variables': {variable: query}})
    headers = {
        'argonath-api-key': '0e36c7e9-8cb7-4fa1-9454-adbc2bad15f0',
        'Content-Type': 'application/json',
        'Referer': PAsearchSites.getSearchBaseURL(siteNum),
    }
    data = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum), headers=headers, params=params).json()

    return data['data']


def search(results, lang, siteNum, searchData):
    searchResults = getGraphQL(searchQuery, 'query', searchData.title)['search']['search']['result']

    for searchResult in searchResults:
        if searchResult['type'] == 'VIDEO':
            titleNoFormatting = PAutils.parseTitle(searchResult['name'], siteNum)
            curID = PAutils.Encode(searchResult['itemId'])

            releaseDate = searchData.dateFormat() if searchData.date else ''

            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Thicc18]' % titleNoFormatting, score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    videoId = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]

    splitted = videoId.split(':')
    modelId = splitted[0]
    scene = splitted[-1]
    sceneNum = int(scene.replace('scene', ''))

    detailsPageElements = getGraphQL(findVideoQuery, 'videoId', videoId)['video']['find']['result']

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['title'], siteNum)

    # Summary
    summary = detailsPageElements['description']['long'].strip()
    if not summary.endswith('.'):
        summary = summary + '.'

    metadata.summary = summary

    # Studio
    metadata.studio = 'Thicc18'

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    movieGenres.addGenre('Thicc')

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements['talent']:
        actorPhoto = []
        actorName = actorLink['talent']['name']

        actorPhoto.append('/members/models/%s/profile-sm.jpg' % actorLink['talent']['talentId'])
        actorPhotoURL = getGraphQL(assetQuery, 'paths', actorPhoto)['asset']['batch']['result'][0]['serve']['uri']

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    images = []
    images.append('/members/models/%s/scenes/%s/videothumb.jpg' % (modelId, scene))
    for idx in range(1, detailsPageElements['galleryCount'] + 1):
        path = '/members/models/%s/scenes/%s/photos/thumbs/thicc18-%s-%d-%d.jpg' % (modelId, scene, modelId, sceneNum, idx)
        images.append(path)

    posters = getGraphQL(assetQuery, 'paths', images)['asset']['batch']['result']

    for poster in posters:
        if poster:
            art.append(poster['serve']['uri'])

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
                if height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


searchQuery = 'query Search($query: String!) { search { search(input: {query: $query}) { result { type itemId name description images } } } }'
findVideoQuery = 'query FindVideo($videoId: ID!) { video { find(input: {videoId: $videoId}) { result { videoId title duration galleryCount description { short long } talent { type talent { talentId name } } } } } }'
assetQuery = 'query BatchFindAssetQuery($paths: [String!]!) { asset { batch(input: {paths: $paths}) { result { path mime size serve { type uri } } } } }'
