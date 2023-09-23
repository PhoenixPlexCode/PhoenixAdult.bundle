import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.encoded = urllib.quote(searchData.title.replace(sceneID, '', 1).strip())

    url = PAsearchSites.getSearchSearchURL(siteNum) + 'videos/browse/search/' + searchData.encoded + '?page=1&sg=false&sort=release&video_type=scene&lang=en&site_id=10&genre=0&dach=false'
    data = PAutils.HTTPRequest(url)
    data = data.json()

    for searchResult in data['videos']['data']:
        titleNoFormatting = searchResult['title']['en']
        releaseDate = parse(searchResult['publication_date']).strftime('%Y-%m-%d')
        searchID = searchResult['id']
        curID = PAutils.Encode(PAsearchSites.getSearchSearchURL(siteNum) + '/videodetail/' + str(searchID))

        if sceneID and int(sceneID) == searchID:
            score = 100
        elif searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)

        actors = []
        for actorData in searchResult['actors']:
            actors.append(actorData['name'])
        actorsList = ', '.join(actors)

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s (%s) [%s] %s' % (titleNoFormatting, actorsList, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    req = PAutils.HTTPRequest(sceneURL)
    data = req.json()

    # Title
    metadata.title = data['video']['title']['en']

    # Summary
    metadata.summary = data['video']['description']['en']

    # Studio
    metadata.studio = 'Teen Core Club'

    # Tagline and Collection(s)
    tagline = data['video']['labels'][0]['name'].replace('.com', '').strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Actor(s)
    actors = []
    for actorData in data['video']['actors']:
        actorName = actorData['name']
        actors.append(actorName)

        movieActors.addActor(actorName, '')

    if actors and metadata.title.lower().startswith('bic_'):
        if len(actors) == 1:
            metadata.title = actors[0]
        elif len(actors) == 2:
            metadata.title = ' & '.join(actors)
        else:
            metadata.title = ', '.join(actors)

    # Date
    date = data['video']['publication_date']
    if date:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreData in data['video']['genres']:
        if genreData['title']['en']:
            genreName = genreData['title']['en']
            movieGenres.addGenre(genreName)

    try:
        if data['video']['artwork']['small']:
            art.append(data['video']['artwork']['small'])
        if data['video']['artwork']['large']:
            art.append(data['video']['artwork']['large'])

        if data['video']['cover']['small']:
            art.append(data['video']['cover']['small'])
        if data['video']['cover']['medium']:
            art.append(data['video']['cover']['medium'])
        if data['video']['cover']['large']:
            art.append(data['video']['cover']['large'])

        for screenshot in data['video']['screenshots']:
            art.append(screenshot)
    except:
        pass

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
