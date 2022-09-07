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
    req = PAutils.HTTPRequest('https://www.naughtyamerica.com/scene/0' + sceneID)
    elements = HTML.ElementFromString(req.text)
    results = {}
    categories = elements.xpath('//div[contains(@class, "categories") and contains(@class, "grey-text")]/a')
    results['fantasies'] = [category.text for category in categories]
    actors = elements.xpath('//div[contains(@class, "performer-list")]/a')
    results['performers'] = [actor.text for actor in actors]
    results['title'] = elements.xpath('//div[contains(@class, "scene-info")]//h1/text()')[0]
    results['synopsis'] = elements.xpath('//div[contains(@class, "synopsis") and contains(@class, "grey-text")]//h2')[0].tail.strip()
    publishDate = elements.xpath('//div[contains(@class, "date-tags")]//span/text()')[0]
    results['publish_date'] = publishDate
    dateobject = datetime.strptime(publishDate, "%b %d, %Y")
    results['published_at'] = (dateobject - datetime(1970, 1, 1)).total_seconds() + 3600 * 8 #timezone offset of PT
    results['site'] = elements.xpath('//a[@class="site-title grey-text link"]/text()')[0]
    results['id'] = int(sceneID)
    return results


def search(results, lang, siteNum, searchData):
    sceneID = searchData.title.split(' ', 1)[0]
    if unicode(sceneID, 'UTF-8').isdigit():
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()
    else:
        sceneID = None

    url = PAsearchSites.getSearchSearchURL(siteNum) + '?x-algolia-application-id=I6P9Q9R18E&x-algolia-api-key=08396b1791d619478a55687b4deb48b4'
    if sceneID and not searchData.title:
        if int(sceneID) < 31400:
            searchResults = getAlgolia(url, 'nacms_combined_production', 'filters=id=' + sceneID)
        else:
            searchResults = [getNaughtyAmerica(sceneID)]
    else:
        searchResults = getAlgolia(url, 'nacms_combined_production', 'query=' + searchData.title)

    for searchResult in searchResults:
        titleNoFormatting = PAutils.parseTitle(searchResult['title'], siteNum)
        curID = searchResult['id']
        releaseDate = datetime.fromtimestamp(searchResult['published_at']).strftime('%Y-%m-%d')
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

    url = PAsearchSites.getSearchSearchURL(siteNum) + '?x-algolia-application-id=I6P9Q9R18E&x-algolia-api-key=08396b1791d619478a55687b4deb48b4'
    if int(sceneID) < 31400:
        detailsPageElements = getAlgolia(url, 'nacms_combined_production', 'filters=id=' + sceneID)[0]
    else:
        detailsPageElements = getNaughtyAmerica(sceneID)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['title'], siteNum)

    # Summary
    metadata.summary = detailsPageElements['synopsis']

    # Studio
    metadata.studio = 'Naughty America'

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)
    metadata.collections.add(detailsPageElements['site'])

    # Release Date
    date_object = datetime.fromtimestamp(detailsPageElements['published_at'])
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
    req = PAutils.HTTPRequest('https://www.naughtyamerica.com/scene/0' + sceneID)
    scenePageElements = HTML.ElementFromString(req.text)
    for photo in scenePageElements.xpath('//div[contains(@class, "contain-scene-images") and contains(@class, "desktop-only")]/a/@href'):
        img = 'https:' + re.sub(r'images\d+', 'images1', photo, 1, flags=re.IGNORECASE)
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
