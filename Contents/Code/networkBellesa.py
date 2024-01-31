import PAsearchSites
import PAutils


def getJSONfromAPI(type, query, siteNum):
    url = '%s/%s?%s' % (PAsearchSites.getSearchSearchURL(siteNum), type, query)
    headers = {
        'Content-Type': 'application/json',
        'Referer': PAsearchSites.getSearchBaseURL(siteNum)
    }
    req = PAutils.HTTPRequest(url, headers=headers)
    result = HTML.ElementFromString(req.text)

    return json.loads(result.xpath('//body')[0].text_content())


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()

    if sceneID:
        scenePageElements = getJSONfromAPI('videos', 'filter[id]=%s' % sceneID, siteNum)[0]

        titleNoFormatting = PAutils.parseTitle(scenePageElements['title'], siteNum)
        curID = sceneID
        subSite = scenePageElements['content_provider'][0]['name']

        date = scenePageElements['posted_on']
        if date:
            releaseDate = datetime.fromtimestamp(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        displayDate = releaseDate if date else ''

        score = 100

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Bellesa/%s] %s' % (titleNoFormatting, subSite, displayDate), score=score, lang=lang))
    else:
        searchResults = getJSONfromAPI('search', 'limit=40&order[relevance]=DESC&q=%s&providers=bellesa' % searchData.title.replace(' ', '%20'), siteNum)

        for searchResult in searchResults['videos']:
            titleNoFormatting = PAutils.parseTitle(searchResult['title'], siteNum)
            curID = searchResult['id']

            date = searchResult['posted_on']
            if date:
                releaseDate = datetime.fromtimestamp(date).strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''
            displayDate = releaseDate if date else ''

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Bellesa] %s' % (titleNoFormatting, displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneDate = metadata_id[2]
    sceneID = metadata_id[0]

    detailsPageElements = getJSONfromAPI('videos', 'filter[id]=%s' % sceneID, siteNum)[0]

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['title'], siteNum)

    # Summary
    metadata.summary = detailsPageElements['description']

    # Studio
    metadata.studio = 'Bellesa'

    # Tagline and Collection(s)
    tagline = detailsPageElements['content_provider'][0]['name']
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    genres = detailsPageElements['tags'].split(',')
    for genreLink in genres:
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = detailsPageElements['performers']

    for actor in actors:
        actorName = actor['name']
        actorPhotoURL = ''

        if actor['image']:
            actorPhotoURL = actor['image']

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art.append(detailsPageElements['image'])

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
