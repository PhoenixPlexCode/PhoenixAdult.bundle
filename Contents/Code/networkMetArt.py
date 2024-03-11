import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + '/search-results?query[contentType]=movies&searchPhrase=' + searchData.encoded)
    searchResults = req.json()
    for searchResult in searchResults['items']:
        subSite = PAsearchSites.getSearchSiteName(siteNum)
        titleNoFormatting = searchResult['item']['name']

        sceneURL = searchResult['item']['path'].rsplit('/', 2)
        sceneURL = '%s/movie?name=%s&date=%s' % (PAsearchSites.getSearchSearchURL(siteNum), sceneURL[2], sceneURL[1])
        curID = PAutils.Encode(sceneURL)

        releaseDate = parse(searchResult['item']['publishedAt']).strftime('%Y-%m-%d')
        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [MetArt/%s] %s' % (titleNoFormatting, subSite, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = req.json()

    # Title
    metadata.title = detailsPageElements['name']

    # Summary
    metadata.summary = detailsPageElements['description']

    # Studio
    metadata.studio = 'MetArt'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements['publishedAt']
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements['tags']:
        genreName = genreLink.title()

        movieGenres.addGenre(genreName)
    movieGenres.addGenre('Glamorous')

    # Actor(s)
    for actorLink in detailsPageElements['models']:
        actorName = actorLink['name']
        actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink['headshotImagePath']

        movieActors.addActor(actorName, actorPhotoURL)

    # Director(s)
    for directorLink in detailsPageElements['photographers']:
        directorName = directorLink['name']

        movieActors.addDirector(directorName, '')

    # Posters
    siteUUID = detailsPageElements['siteUUID']
    CDNurl = 'https://cdn.metartnetwork.com/' + siteUUID
    art.append(CDNurl + detailsPageElements['coverImagePath'])
    art.append(CDNurl + detailsPageElements['splashImagePath'])

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
