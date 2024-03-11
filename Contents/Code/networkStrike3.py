import PAsearchSites
import PAutils


def getDatafromAPI(url, query, variables, referer):
    headers = {
        'Content-Type': 'application/json',
        'Referer': referer
    }
    params = json.dumps({'query': query, 'variables': json.loads(variables)})
    req = PAutils.HTTPRequest(url, params=params, headers=headers)

    if req:
        return req.json()['data']

    return req


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit() and len(parts[0]) > 4:
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()

        search_variables = json.dumps({'videoId': sceneID, 'site': PAsearchSites.getSearchSiteName(siteNum).upper()})
        searchResult = getDatafromAPI(PAsearchSites.getSearchSearchURL(siteNum), search_id_query, search_variables, PAsearchSites.getSearchBaseURL(siteNum))
        if searchResult:
            titleNoFormatting = PAutils.parseTitle(searchResult['findOneVideo']['title'], siteNum)
            releaseDate = parse(searchResult['findOneVideo']['releaseDate']).strftime('%Y-%m-%d')
            curID = PAutils.Encode(searchResult['findOneVideo']['slug'])
            videoID = int(searchResult['findOneVideo']['videoId'])

            if int(sceneID) == videoID:
                score = 100
            elif searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))
    else:
        search_variables = json.dumps({'query': searchData.title, 'site': PAsearchSites.getSearchSiteName(siteNum).upper(), 'first': 10, 'skip': 0})
        searchResults = getDatafromAPI(PAsearchSites.getSearchSearchURL(siteNum), search_query, search_variables, PAsearchSites.getSearchBaseURL(siteNum))
        if searchResults:
            for searchResult in searchResults['searchVideos']['edges']:
                titleNoFormatting = PAutils.parseTitle(searchResult['node']['title'], siteNum)
                releaseDate = parse(searchResult['node']['releaseDate']).strftime('%Y-%m-%d')
                curID = PAutils.Encode(searchResult['node']['slug'])

                if searchData.date:
                    score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
                else:
                    score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneName = PAutils.Decode(metadata_id[0])

    update_variables = json.dumps({'slug': sceneName, 'site': PAsearchSites.getSearchSiteName(siteNum).upper()})
    detailsPageElements = getDatafromAPI(PAsearchSites.getSearchSearchURL(siteNum), update_query, update_variables, PAsearchSites.getSearchBaseURL(siteNum))
    video = detailsPageElements['findOneVideo']
    pictureset = video['carousel']

    # Title
    metadata.title = PAutils.parseTitle(video['title'], siteNum)

    # Summary
    metadata.summary = video['description']

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum).title()

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Release Date
    date_object = parse(video['releaseDate'])
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    if metadata.studio == 'Tushy' or metadata.studio == 'TushyRaw':
        movieGenres.addGenre('Anal')

    if video['categories']:
        for tag in video['categories']:
            genreName = tag['name']

            movieGenres.addGenre(genreName)

    # Actor(s)
    actors = video['models']
    for actor in actors:
        actorName = actor['name']
        actorPhotoURL = ''
        if actor['images']:
            actorPhotoURL = actor['images']['listing'][0]['highdpi']['double']

        movieActors.addActor(actorName, actorPhotoURL)

    # Director
    if video['directors']:
        directorName = video['directors'][0]['name']

        movieActors.addDirector(directorName, '')

    # Posters
    for name in ['movie', 'poster']:
        if name in video['carousel'] and video['images'][name]:
            image = video['images'][name][-1]
            if 'highdpi' in image:
                art.append(image['highdpi']['3x'])
            else:
                art.append(image['src'])
            break

    for image in pictureset:
        img = image['listing'][0]['highdpi']['triple']

        art.append(img)

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        cleanUrl = posterUrl.split('?')[0]
        art[idx - 1] = cleanUrl
        if not PAsearchSites.posterAlreadyExists(cleanUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    metadata.posters[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
                    posterExists = True
                if width > height:
                    # Item is an art item
                    images.append((image, cleanUrl))
                    metadata.art[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass
        elif PAsearchSites.posterOnlyAlreadyExists(cleanUrl, metadata):
            posterExists = True

    if not posterExists:
        for idx, (image, cleanUrl) in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


search_query = 'query getSearchResults($query:String!,$site:Site!,$first:Int,$skip:Int){searchVideos(input:{query:$query,site:$site,first:$first,skip:$skip}){edges{node{videoId title releaseDate slug images{listing{src}}}}}}'
update_query = 'query getSearchResults($slug:String!,$site:Site!){findOneVideo(input:{slug:$slug,site:$site}){videoId title description releaseDate models{name slug images{listing{highdpi{double}}}}directors{name}categories{name}carousel{listing{highdpi{triple}}}}}'
search_id_query = 'query getSearchResults($videoId:ID!,$site:Site!){findOneVideo(input:{videoId:$videoId,site:$site}){videoId title releaseDate slug}}'
