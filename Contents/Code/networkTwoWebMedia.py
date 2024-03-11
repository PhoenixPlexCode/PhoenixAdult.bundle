import PAsearchSites
import PAutils


def getJSONfromPage(url):
    req = PAutils.HTTPRequest(url)
    detailsPageElements = HTML.ElementFromString(req.text)

    if req.ok:
        data = None
        node = detailsPageElements.xpath('//script[@id="__NEXT_DATA__"]')
        if node:
            data = node[0].text_content()

        if data:
            return json.loads(data)['props']['pageProps']

    return None


def search(results, lang, siteNum, searchData):
    searchURL = '%s/%s' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded)
    searchResults = getJSONfromPage(searchURL)['contents']['data']
    for searchResult in searchResults:
        titleNoFormatting = PAutils.parseTitle(searchResult['title'], siteNum)
        sceneURL = '%s/videos/%s' % (PAsearchSites.getSearchBaseURL(siteNum), searchResult['slug'])
        curID = PAutils.Encode(sceneURL)

        date = searchResult['publish_date']
        if date:
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [TwoWebMedia/%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    jsonPageElements = getJSONfromPage(sceneURL)
    models = jsonPageElements['models']
    detailsPageElements = jsonPageElements['content']

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['title'], siteNum)

    # Summary
    metadata.summary = detailsPageElements['description']

    # Studio
    metadata.studio = 'TwoWebMedia'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements['publish_date'].split()[0]
    if date:
        date_object = datetime.strptime(date, '%Y/%m/%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements['tags']:
        genreName = genreLink

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in models:
        actorName = actorLink['name']
        actorPhotoURL = actorLink['thumbnails'][0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    for idx, poster in enumerate(detailsPageElements['photos']['full']):
        art.append(detailsPageElements['photos']['full'][str(idx)])

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        # Remove Timestamp and Token from URL
        cleanUrl = posterUrl.split('?')[0]
        art[idx - 1] = cleanUrl
        if not PAsearchSites.posterAlreadyExists(cleanUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': sceneURL})
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100:
                    # Item is an art item
                    metadata.art[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
