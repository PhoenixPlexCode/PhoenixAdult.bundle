import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    matchID = None
    sourceID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sourceID = parts[0]
        searchData.title = searchData.title.replace(sourceID, '', 1).strip()

        sceneURL = '%s/contents/%s' % (PAsearchSites.getSearchBaseURL(siteNum), sourceID)
        curID = PAutils.Encode(sceneURL)

        req = PAutils.HTTPRequest(sceneURL)

        if req.ok:
            scenePageElements = req.json()
            titleNoFormatting = PAutils.parseTitle(scenePageElements['scene_name'], siteNum)

            date = scenePageElements['publish_date']
            if date:
                releaseDate = parse(date).strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''

            displayDate = releaseDate if date else ''

            score = 100

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Pornbox] %s' % (titleNoFormatting, displayDate), score=score, lang=lang))

    parts = searchData.title.split()
    sceneID = parts[0]

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.title)
    searchResults = req.json()['content']['contents']

    for searchResult in searchResults:
        titleNoFormatting = PAutils.parseTitle(searchResult['scene_name'], siteNum)
        match = re.search(r'\w+\d$', titleNoFormatting)
        if match:
            matchID = match.group(0)
            titleNoFormatting = re.sub(r'\w+\d$', '', titleNoFormatting).strip()
            titleNoFormatting = '[%s] %s' % (matchID, titleNoFormatting)

        sceneURL = '%s/contents/%s' % (PAsearchSites.getSearchBaseURL(siteNum), searchResult['content_id'])
        curID = PAutils.Encode(sceneURL)

        date = searchResult['publish_date']
        if date:
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if matchID and sceneID.lower() == matchID.lower():
            matchID = None
            score = 100
        elif sourceID and int(sourceID) == searchResult['source_id']:
            score = 100
        elif searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Pornbox]' % (titleNoFormatting), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = req.json()

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['scene_name'], siteNum)

    # Summary
    try:
        metadata.summary = PAutils.cleanSummary(detailsPageElements['small_description'])
    except:
        pass

    # Studio
    metadata.studio = 'Pornbox'

    # Tagline and Collection(s)
    tagline = PAutils.parseTitle(detailsPageElements['studio'], siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements['publish_date']
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements['niches']:
        genreName = genreLink['niche']

        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = []
    if 'models' in detailsPageElements:
        actors.extend(detailsPageElements['models'])
    if 'male_models' in detailsPageElements:
        actors.extend(detailsPageElements['male_models'])
    for actorLink in actors:
        actorName = actorLink['model_name']
        actorPhotoURL = ''

        actorPageURL = '%s/model/info/%s' % (PAsearchSites.getSearchBaseURL(siteNum), actorLink['model_id'])
        req = PAutils.HTTPRequest(actorPageURL)
        actorPageElements = req.json()

        if actorPageElements['headshot']:
            actorPhotoURL = actorPageElements['headshot']

        movieActors.addActor(actorName, actorPhotoURL)

    # Director(s)
    if tagline == 'Giorgio Grandi' or 'Giorgio\'s Lab' in tagline:
        directorName = 'Giorgio Grandi'

        movieActors.addDirector(directorName, '')

    # Posters/Background
    art.append(detailsPageElements['player_poster'])

    for x in range(1, len(detailsPageElements['screenshots'])):
        # Only grab every 10th image for videos with over 50 images
        if len(detailsPageElements['screenshots']) > 50 and x % 10 == 0:
            art.append(detailsPageElements['screenshots'][x]['xga_size'])
        elif len(detailsPageElements['screenshots']) <= 50:
            art.append(detailsPageElements['screenshots'][x]['xga_size'])

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
