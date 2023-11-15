import PAsearchSites
import PAutils


def getToken(url):
    if '//api.' in url:
        url = url.replace('//api.', '//', 1)

    req = PAutils.HTTPRequest(url)

    if req:
        return re.search(r'\.access_token=\"(.*?)\"', req.text).group(1)

    return None


def getDatafromAPI(baseURL, searchData, token, search=True):
    data = {}
    headers = {'Authorization': 'Bearer ' + token}

    if search:
        headers['Content-Type'] = 'application/json'
        params = json.dumps({'query': searchData})
        req = PAutils.HTTPRequest(baseURL, headers=headers, params=params)
    else:
        url = baseURL + '/api/movies/slug/' + str(searchData)
        headers = {'Authorization': 'Bearer ' + token}
        req = PAutils.HTTPRequest(url, headers=headers)

    if req:
        data = req.json()
        if 'data' in data:
            return data['data']

    return data


def search(results, lang, siteNum, searchData):
    token = getToken(PAsearchSites.getSearchBaseURL(siteNum))
    if token:
        searchResults = getDatafromAPI(PAsearchSites.getSearchSearchURL(siteNum), searchData.title, token)
        for searchResult in searchResults:
            if searchResult['resourceType'] == 'movies':
                curID = searchResult['slug']
                titleNoFormatting = searchResult['title']

                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s' % (titleNoFormatting), score=score, lang=lang))

        # Also try to get a direct match from the title slug
        slug = searchData.title.replace(' ', '-').lower()
        directMatch = getDatafromAPI(PAsearchSites.getSearchBaseURL(siteNum), slug, token, False)
        if directMatch:
            curID = directMatch['slug']
            titleNoFormatting = directMatch['title']
            # This is a perfect match, so give it a perfect score
            score = 100
            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s' % (titleNoFormatting), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneID = metadata_id[0]

    token = getToken(PAsearchSites.getSearchBaseURL(siteNum))
    detailsPageElements = getDatafromAPI(PAsearchSites.getSearchBaseURL(siteNum), sceneID, token, False)

    # Title
    metadata.title = detailsPageElements['title']

    # Summary
    metadata.summary = detailsPageElements['synopsis_clean']

    # Studio
    producerLink = detailsPageElements['producer']
    metadata.studio = '%s %s' % (producerLink['name'], producerLink['last_name'])

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date_object = parse(detailsPageElements['release_date'])
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements['tags']:
        genreName = genreLink['title']
        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements['performers']:
        actorName = '%s %s' % (actorLink['name'], actorLink['last_name'])
        if actorLink['poster_image'] is not None:
            actorPhotoURL = actorLink['poster_image'].split('?', 1)[0]
        else:
            actorPhotoURL = ''
        movieActors.addActor(actorName, actorPhotoURL)

    # Director
    directorLink = detailsPageElements['director']
    directorName = '%s %s' % (directorLink['name'], directorLink['last_name'])
    movieActors.addDirector(directorName, '')

    # Poster
    art.append(detailsPageElements['poster_picture'].split('?', 1)[0])

    for photoLink in detailsPageElements['album']:
        img = photoLink['path'].split('?', 1)[0]
        art.append(img)

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
