import PAutils


def search(results, media, lang, siteNum, searchTitle, encodedTitle, searchDate):
    searchTitle = searchTitle.replace(' AND ', ' and ').replace(' And ', ' and ').replace(' In ', ' in ').replace(' At ', ' at ')
    parse_siteName = searchTitle.rsplit(' at ', 1)
    if len(parse_siteName) > 1:
        siteName = parse_siteName[1].strip()
    else:
        siteName = ''

    parse_sceneName = parse_siteName[0].split(' in ', 1)
    if len(parse_sceneName) > 1:
        sceneName = parse_sceneName[1].strip().title()
    else:
        sceneName = ''

    actors = parse_sceneName[0].split(' and ')
    actorsFormatted = []
    for actor in actors:
        actorsFormatted.append(actor.strip().title())
    displayName = ', '.join(actorsFormatted)
    curID = PAutils.Encode(displayName)

    if searchDate:
        releaseDate = parse(searchDate).strftime('%Y-%m-%d')
    else:
        releaseDate = ''

    score = 100

    results.Append(MetadataSearchResult(id='%s|%d|%s|%s|%s' % (curID, siteNum, releaseDate, sceneName, siteName), name='%s [%s] %s' % (displayName, siteName, releaseDate), score=score, lang=lang))

    return results


def update(metadata, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneActors = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    sceneName = metadata_id[3]
    siteName = metadata_id[4]

    # Title
    if sceneName:
        metadata.title = sceneName
    elif siteName:
        metadata.title = '%s - %s' % (sceneActors, siteName)
    else:
        metadata.title = sceneActors

    # Studio
    if siteName:
        metadata.studio = siteName
        metadata.collections.add(siteName)

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = 'Actors Manually Added'
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_Object = parse(sceneDate)
        metadata.originally_available_at = date_Object
        metadata.year = metadata.originally_available_at.year

    # Actors
    movieActors.clearActors()
    for actor in sceneActors.split(','):
        actorName = actor.strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    return metadata
