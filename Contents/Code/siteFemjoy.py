import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchTitle, encodedTitle, searchDate, filename):
    searchURL = PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle
    req = PAutils.HTTPRequest(searchURL)
    searchResults = req.json()

    if 'results' not in searchResults or not searchResults['results'] and filename:
        # femjoy.17.03.12.maria.rya.girl.in.the.mirror.mp4
        # try to extract as much of the title as possible without including the model
        m = re.search(r'femjoy\.(\d{2}\.\d{2}\.\d{2})\.(.+)', filename, re.IGNORECASE)
        if m:
            searchDate = parse('20' + m.group(1)).strftime('%Y-%m-%d')
            searchWords = m.group(2).split('.')
            wordCount = len(searchWords)
            if wordCount > 2:
                searchTitle = ' '.join(searchWords[2:])
            else:
                searchTitle = searchWords[-1]

        else:
            # Belinda & Fiva - Give me your hand 29-Mar-2010.mp4
            # take everything from after the dash and before the date
            m = re.search(r'.+ - (.+) (\d{2}-[a-z]{3}-\d{4})', filename, re.IGNORECASE)
            if m:
                searchDate = parse(m.group(2)).strftime('%Y-%m-%d')
                searchTitle = m.group(1)

        encodedTitle = urllib.quote(searchTitle)
        searchURL = PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle
        req = PAutils.HTTPRequest(searchURL)
        searchResults = req.json()

    if 'results' in searchResults:
        curID = PAutils.Encode(searchURL)

        for searchResult in searchResults['results']:
            titleNoFormatting = searchResult['title']
            slug = searchResult['slug']

            date = searchResult['release_date']
            if date:
                releaseDate = parse(date).strftime('%Y-%m-%d')
            else:
                releaseDate = parse(searchDate).strftime('%Y-%m-%d') if searchDate else ''
            displayDate = releaseDate if date else ''

            actorsString = getActorsString(searchResult['actors'])

            if searchDate and displayDate:
                score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, slug), name='%s - %s [%s] %s' % (titleNoFormatting, actorsString, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    searchURL = PAutils.Decode(metadata_id[0])
    slug = metadata_id[2]
    req = PAutils.HTTPRequest(searchURL)
    detailsPageElements = None
    searchResults = req.json()
    if 'results' not in searchResults:
        return metadata

    for scene in searchResults['results']:
        if scene['slug'] == slug:
            detailsPageElements = scene
            break

    if not detailsPageElements:
        return metadata

    # Title
    # metadata.title = '%s - %s' % (scene.get('title'), getActorsString(scene.get('actors')))  # do we want the actor names in the title?
    metadata.title = detailsPageElements['title']

    # Summary
    metadata.summary = re.sub(r'<.*?>', '', detailsPageElements['long_description']).strip()  # must strip HTML tags

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = metadata.studio
    metadata.collections.add(metadata.studio)

    # Release date
    date_object = parse(detailsPageElements['release_date'])
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()

    # Actors
    movieActors.clearActors()
    if 'actors' in detailsPageElements:
        for actorLink in detailsPageElements['actors']:
            actorName = actorLink['name']
            actorPhotoURL = actorLink['thumb']['image']

            if actorPhotoURL.endswith('noimageavailable.gif'):
                actorSearchURL = PAsearchSites.getSearchBaseURL(siteNum) + '/api/v2/search/actors?thumb_size=355x475&query=' + actorName.split(' ')[0]
                req = PAutils.HTTPRequest(actorSearchURL)
                searchResults = req.json()
                if 'results' in searchResults:
                    for searchResult in searchResults['results']:
                        if searchResult['id'] == actorLink['id']:
                            actorPhotoURL = searchResult['thumb']['image']
                            break

            movieActors.addActor(actorName, actorPhotoURL)

    # Director
    metadata.directors.clear()
    if 'directors' in detailsPageElements:
        for directorLink in detailsPageElements['directors']:
            director = metadata.directors.new()
            director.name = directorLink['name']

    # Posters
    art = [
        detailsPageElements['thumb']['image']
    ]

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


def getActorsString(actors):
    # produce 'a, b, c and d' from a list of actor objects
    names = []
    for actor in actors:
        names.append(actor['name'])

    count = len(names)
    if count == 1:
        return names[0]
    else:
        names[count - 2] = ' and '.join(names[-2:])
        names.pop(count - 1)

        return ', '.join(names)
