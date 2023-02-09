import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneId = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneId = parts[0]
        searchData.title = searchData.title.replace(sceneId, '', 1).strip()

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded.lower())
    searchPageElements = HTML.ElementFromString(req.text)

    searchResults = json.loads(searchPageElements.xpath('//script[@type="application/json"]')[0].text_content())

    if PAsearchSites.getSearchSiteName(siteNum) == 'ComeInside':
        data = searchResults['props']['pageProps']['model_contents']
    else:
        data = searchResults['props']['pageProps']['contents']['data']

    if searchResults:
        for searchResult in data:
            titleNoFormatting = PAutils.parseTitle(searchResult['title'], siteNum)
            videoId = searchResult['id']

            if PAsearchSites.getSearchSiteName(siteNum) == 'ComeInside':
                releaseDate = parse(searchResult['created_at']).strftime('%Y-%m-%d')
                sceneURL = '%s/scenes/%s/%s' % (PAsearchSites.getSearchBaseURL(siteNum), videoId, searchResult['slug'])
            else:
                releaseDate = parse(searchResult['publish_date']).strftime('%Y-%m-%d')
                sceneURL = '%s/videos/%s' % (PAsearchSites.getSearchBaseURL(siteNum), searchResult['slug'])

            curID = PAutils.Encode(sceneURL)

            if sceneId and int(sceneId) == int(videoId):
                score == 100
            elif searchData.date:
                score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)
    videoPageElements = json.loads(detailsPageElements.xpath('//script[@type="application/json"]')[0].text_content())

    if PAsearchSites.getSearchSiteName(siteNum) == 'ComeInside':
        video = videoPageElements['props']['pageProps']['playlist']
        content = videoPageElements['props']['pageProps']['content']
    else:
        video = videoPageElements['props']['pageProps']['content']
        content = video

    # Title
    metadata.title = PAutils.parseTitle(video['title'], siteNum)

    # Summary
    metadata.summary = video['description']

    # Studio
    metadata.studio = 'Radical Cash'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date_object = parse(video['publish_date'])
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in content['tags']:
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actor in video['models_thumbs']:
        actorName = actor['name']
        actorPhotoURL = actor['thumb']

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art.append(content['trailer_screencap'])
    for imageType in ['extra_thumbnails']:
        if imageType in content:
            for image in list(content[imageType]):
                art.append(image)

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
