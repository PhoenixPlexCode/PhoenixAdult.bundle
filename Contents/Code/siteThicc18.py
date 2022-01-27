import PAsearchSites
import PAutils


def getGraphQL(operationName, queryType, variable, query):
    params = json.dumps({'operationName': operationName, 'query': queryType, 'variables': {variable: query}})
    headers = {
        'argonath-api-key': '0e36c7e9-8cb7-4fa1-9454-adbc2bad15f0',
        'Content-Type': 'application/json',
        'Referer': 'https://thicc18.com'
    }
    data = PAutils.HTTPRequest('https://thicc18.team18.app/graphql', headers=headers, params=params).json()

    return data['data']


def search(results, lang, siteNum, searchData):
    searchResults = getGraphQL('Search', searchQuery, 'query', searchData.title)['search']['search']['result']

    for searchResult in searchResults:
        if searchResult['type'] == 'VIDEO':
            titleNoFormatting = PAutils.parseTitle(searchResult['name'], siteNum)
            curID = PAutils.Encode(searchResult['itemId'])

            releaseDate = searchData.dateFormat() if searchData.date else ''

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Thicc18] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    videoId = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    modelId = videoId.split(':')[0]
    scene = videoId.split(':')[-1]
    sceneNum = int(scene.replace('scene', ''))

    detailsPageElements = getGraphQL('FindVideo', findVideoQuery, 'videoId', videoId)['video']['find']['result']

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['title'], siteNum)

    # Summary
    pattern = r'.*(?<=\.)$'
    summary = detailsPageElements['description']['long'].strip()
    match = re.match(pattern, summary)
    if not match:
        metadata.summary = summary + '.'
    else:
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
        actorPhotoURL = getGraphQL('BatchFindAssetQuery', assetQuery, 'paths', actorPhoto)['asset']['batch']['result'][0]['serve']['uri']

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    images = []
    for idx in range(1, detailsPageElements['galleryCount'] + 1):
        path = '/members/models/%s/scenes/%s/photos/thumbs/thicc18-%s-%d-%d.jpg' % (modelId, scene, modelId, sceneNum, idx)
        images.append(path)

    posters = getGraphQL('BatchFindAssetQuery', assetQuery, 'paths', images)['asset']['batch']['result']

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


searchQuery = 'query Search($query: String!) {\n  search {\n    search(input: {query: $query}) {\n      result {\n        type\n        itemId\n        name\n        description\n        images\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n'
findVideoQuery = 'query FindVideo($videoId: ID!) {\n  video {\n    find(input: {videoId: $videoId}) {\n      result {\n        videoId\n        title\n        duration\n        galleryCount\n        description {\n          short\n          long\n          __typename\n        }\n        talent {\n          type\n          talent {\n            talentId\n            name\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n'
assetQuery = 'query BatchFindAssetQuery($paths: [String!]!) {\n  asset {\n    batch(input: {paths: $paths}) {\n      result {\n        path\n        mime\n        size\n        serve {\n          type\n          uri\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n'
