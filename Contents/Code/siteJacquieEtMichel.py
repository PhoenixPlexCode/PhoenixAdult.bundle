import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]

    url = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded
    req = PAutils.HTTPRequest(url)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//a[@class="content-card content-card--video"]'):
        titleNoFormatting = searchResult.xpath('.//h2[@class="content-card__title"]')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('./@href')[0])
        date = searchResult.xpath('.//div[@class="content-card__date"]')[0].text_content().replace('Added on', '').strip()
        releaseDate = parse(date).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    # SceneId search
    if sceneID:
        url = PAsearchSites.getSearchBaseURL(siteNum) + '/en/content/' + sceneID
        req = PAutils.HTTPRequest(url)
        detailsPageElements = HTML.ElementFromString(req.text)

        titleNoFormatting = detailsPageElements.xpath('//h1[@class="content-detail__title"]')[0].text_content().strip()
        curID = PAutils.Encode(url)

        score = 100

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@class="content-detail__title"]')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="content-detail__description"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Jacquie Et Michel TV'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="content-detail__row"]//li[@class="content-detail__tag"]'):
        genreName = genreLink.text_content().replace(',', '').strip()
        if genreName == 'Sodomy':
            genreName = 'Anal'

        movieGenres.addGenre(genreName)

    movieGenres.addGenre('French porn')

    # Release Date
    date = detailsPageElements.xpath('//div[@class="content-detail__infos__row"]//p[@class="content-detail__description content-detail__description--link"]')[1].text_content().strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Actor(s)
    for actorLink in getJMTVActors(sceneURL):
        actorName = actorLink
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Poster
    img = detailsPageElements.xpath('//video/@poster')[0]
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
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


def getJMTVActors(url):
    # Actor(s) for scenes must be manually specified using a URL fragment:
    scenes = {
        '4554/ibiza-1-crumb-in-the-mouth': [
            'Alexis Crystal',
            'Cassie Del Isla',
            'Dorian Del Isla',
        ],
        '4558/orgies-in-ibiza-2-lucys-surprise': [
            'Alexis Crystal',
            'Cassie Del Isla',
            'Lucy Heart',
            'Dorian Del Isla',
            'James Burnett Klein',
            'Vlad Castle',
        ],
        '4564/orgies-in-ibiza-3-overheated-orgy-by-the-pool': [
            'Alexis Crystal',
            'Cassie Del Isla',
            'Lucy Heart',
            'Dorian Del Isla',
            'James Burnett Klein',
            'Vlad Castle',
        ],
        '4570/orgies-in-ibiza-4-orgy-with-a-bang-for-the-last-night': [
            'Alexis Crystal',
            'Cassie Del Isla',
            'Lucy Heart',
            'Dorian Del Isla',
            'James Burnett Klein',
            'Vlad Castle',
        ],
    }

    actorList = []
    for urlFragment, actors in scenes.items():
        if urlFragment in url:
            actorList = actors
            break

    return actorList
