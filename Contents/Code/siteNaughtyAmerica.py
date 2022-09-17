import PAsearchSites
import PAutils


def getAlgolia(url, indexName, params):
    params = json.dumps({'requests': [{'indexName': indexName, 'params': params + '&hitsPerPage=100'}]})
    headers = {
        'Content-Type': 'application/json'
    }
    data = PAutils.HTTPRequest(url, headers=headers, params=params).json()

    return data['results'][0]['hits']


def getNaughtyAmerica(sceneID):
    re_image = re.compile(r'images\d+', re.IGNORECASE)

    req = PAutils.HTTPRequest('https://www.naughtyamerica.com/scene/0' + sceneID)
    scenePageElements = HTML.ElementFromString(req.text)

    photoElements = scenePageElements.xpath('//div[contains(@class, "contain-scene-images") and contains(@class, "desktop-only")]/a/@href')

    photos = []
    for photo in photoElements:
        img = 'https:' + re_image.sub('images1', photo, 1)
        photos.append(img)

    results = {
        'id': int(sceneID),
        'title': scenePageElements.xpath('//div[contains(@class, "scene-info")]//h1/text()')[0],
        'site': scenePageElements.xpath('//a[@class="site-title grey-text link"]/text()')[0],
        'published_at': parse(scenePageElements.xpath('//div[contains(@class, "date-tags")]//span/text()')[0]),
        'fantasies': scenePageElements.xpath('//div[contains(@class, "categories") and contains(@class, "grey-text")]/a/text()'),
        'performers': scenePageElements.xpath('//div[contains(@class, "performer-list")]/a/text()'),
        'synopsis': scenePageElements.xpath('//div[contains(@class, "synopsis") and contains(@class, "grey-text")]//h2')[0].tail.strip(),
        'photos': photos,
    }

    return results


def search(results, lang, siteNum, searchData):
    sceneID = searchData.title.split(' ', 1)[0]
    if unicode(sceneID, 'UTF-8').isdigit():
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()
    else:
        sceneID = None

    url = PAsearchSites.getSearchSearchURL(siteNum) + '?x-algolia-application-id=I6P9Q9R18E&x-algolia-api-key=08396b1791d619478a55687b4deb48b4'
    if sceneID:
        searchResults = [getNaughtyAmerica(sceneID)]
    else:
        searchResults = getAlgolia(url, 'nacms_combined_production', 'query=' + searchData.title)

    for searchResult in searchResults:
        titleNoFormatting = PAutils.parseTitle(searchResult['title'], siteNum)
        curID = searchResult['id']
        releaseDate = searchResult['published_at'].strftime('%Y-%m-%d')
        siteName = searchResult['site']

        if sceneID:
            score = 100 - Util.LevenshteinDistance(sceneID, curID)
        elif searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%d|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, siteName, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneID = metadata_id[0]

    # url = PAsearchSites.getSearchSearchURL(siteNum) + '?x-algolia-application-id=I6P9Q9R18E&x-algolia-api-key=08396b1791d619478a55687b4deb48b4'
    detailsPageElements = getNaughtyAmerica(sceneID)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['title'], siteNum)

    # Summary
    metadata.summary = detailsPageElements['synopsis']

    # Studio
    metadata.studio = 'Naughty America'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = detailsPageElements['site']
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date_object = detailsPageElements['published_at']
    if isinstance(date_object, int):
        date_object = datetime.fromtimestamp(date_object)

    if date_object:
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements['fantasies']:
        genreName = genreLink

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements['performers']:
        actorName = actorLink
        actorPhotoURL = ''

        actorsPageURL = 'https://www.naughtyamerica.com/pornstar/' + actorName.lower().replace(' ', '-').replace("'", '')
        req = PAutils.HTTPRequest(actorsPageURL)
        actorsPageElements = HTML.ElementFromString(req.text)
        img = actorsPageElements.xpath('//img[@class="performer-pic"]/@src')
        if img:
            actorPhotoURL = 'https:' + img[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    for img in detailsPageElements['photos']:
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
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
