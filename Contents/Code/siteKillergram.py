import PAsearchSites
import PAutils


def fetchPageContent(siteNum, sceneID):
    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + sceneID
    req = PAutils.HTTPRequest(sceneURL)
    return HTML.ElementFromString(req.text)


def extractTitle(detailPageElements):
    searchResult = detailPageElements.xpath('//img[@id="episode_001"]/@src')
    titleMatches = re.match(r"https://media.killergram.com/models/(?P<actress>[\w ]+)/(?P=actress)_(?P<title>[\w ]+)/.*", searchResult[0].strip())
    return titleMatches.group('title')


def extractDate(detailPageElements):
    searchResult = detailPageElements.xpath('//span[@class="episodeheader" and text()[contains(., "published")]]/parent::node()/text()')
    return searchResult[0].strip()


def extractSummary(detailPageElements):
    searchResult = detailPageElements.xpath('//table[@class="episodetext"]//tr[5]/td[2]/text()')
    return searchResult[0].strip()


def extractActors(detailPageElements):
    actors = []
    actorResults = detailPageElements.xpath('//span[@class="episodeheader" and text()[contains(., "starring")]]/parent::node()/span[@class="modelstarring"]/a/text()')
    for actor in actorResults:
        actors.append(actor.strip())
    return actors


def extractImages(detailPageElements, art):
    prevImage = 000
    isImage = True
    while isImage:
        currImage = prevImage + 1
        imageResult = detailPageElements.xpath('//img[@id="episode_' + str(currImage).zfill(3) + '"]/@src')
        if len(imageResult) > 0 and len(imageResult[0]) > 0:
            art.append(imageResult[0].strip())
            prevImage = currImage
        else:
            isImage = False


def search(results, lang, siteNum, searchData):
    sceneID = searchData.title.split(' ', 1)[0]
    detailsPageElements = fetchPageContent(siteNum, sceneID)
    titleNoFormatting = extractTitle(detailsPageElements)
    releaseDate = parse(extractDate(detailsPageElements)).strftime('%d %B %Y')
    score = 100

    results.Append(MetadataSearchResult(id='%s|%d' % (sceneID, siteNum), name='[Killergram] %s - %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneID = metadata_id[0]
    detailsPageElements = fetchPageContent(siteNum, sceneID)

    # Title
    metadata.title = extractTitle(detailsPageElements)

    # Summary
    metadata.summary = extractSummary(detailsPageElements)

    # Studio
    metadata.studio = "Killergram"

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    metadata.originally_available_at = datetime.strptime(extractDate(detailsPageElements), '%d %B %Y')
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.addGenre('British')

    # Actor(s)
    for actor in extractActors(detailsPageElements):
        movieActors.addActor(actor, '')

    # Posters
    extractImages(detailsPageElements, art)

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
