import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneId = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneId = parts[0]

        if int(sceneId) > 10000:
            searchData.title = searchData.title.replace(sceneId, '', 1).strip()

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchPageElements = HTML.ElementFromString(req.text)

    searchResults = json.loads(searchPageElements.xpath('//script[@type="application/json"]')[0].text_content())

    if searchResults:
        for searchResult in searchResults['props']['pageProps']['videos']:
            titleNoFormatting = PAutils.parseTitle(searchResult['title'], siteNum)
            releaseDate = parse(searchResult['releaseDate']).strftime('%Y-%m-%d')
            sceneURL = '%s/videos/%s' % (PAsearchSites.getSearchBaseURL(siteNum), searchResult['id'].split(':')[-1])
            videoId = searchResult['videoId']
            curID = PAutils.Encode(sceneURL)

            if sceneId and int(sceneId) == int(videoId):
                score == 100
            elif searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    videoPageElements = json.loads(detailsPageElements.xpath('//script[@type="application/json"]')[0].text_content())

    video = videoPageElements['props']['pageProps']['video']
    pictureset = video['carousel']

    # Title
    metadata.title = PAutils.parseTitle(video['title'], siteNum)

    # Summary
    metadata.summary = video['description']

    # Director
    if video['directors']:
        director = metadata.directors.new()
        director.name = video['directors'][0]['name']

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum).title()

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)

    # Release Date
    date_object = parse(video['releaseDate'])
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    if metadata.studio == 'Tushy' or metadata.studio == 'TushyRaw':
        movieGenres.addGenre('Anal')

    for genreLink in detailsPageElements.xpath('//meta[@name="keywords"]/@content')[0].split(','):
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = video['modelsSlugged']
    for actor in actors:
        actorName = actor['name']
        actorPhotoURL = ''

        modelURL = '%s/models/%s' % (PAsearchSites.getSearchBaseURL(siteNum), actor['slugged'])
        req = PAutils.HTTPRequest(modelURL)
        modelPageElements = HTML.ElementFromString(req.text)
        model = json.loads(modelPageElements.xpath('//script[@type="application/json"]')[0].text_content())
        actorPhotoURL = model['props']['pageProps']['hero']['sources'][0]['src']

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    for name in ['mainPortrait', 'mainLandscape']:
        if name == 'mainPortrait':
            image = video['images']['poster'][0]
        else:
            image = video['images']['poster'][-1]

        if 'highdpi' in image:
            art.append(image['highdpi']['double'])
        else:
            art.append(image['src'])

    for image in pictureset:
        img = image['main'][0]['src']

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
                if height > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
