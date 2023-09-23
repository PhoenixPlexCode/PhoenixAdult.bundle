import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.title = re.sub(r'\E\d+(?=\s)', '', searchData.title)
    searchData.encoded = searchData.title.lower().replace(' ', '-')
    directURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded + '.html'

    searchResults = [directURL]
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if '/trailers/' in sceneURL and sceneURL not in searchResults:
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        titleNoFormatting = detailsPageElements.xpath('//h1')[0].text_content().strip()
        curID = PAutils.Encode(sceneURL)

        score = 100 - Util.LevenshteinDistance(searchData.title, titleNoFormatting)

        if '404 Error' not in titleNoFormatting:
            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)
    req = PAutils.HTTPRequest('https://www.iafd.com/studio.rme/studio=9856/blackpayback.com.htm')
    IAFDStudioElements = HTML.ElementFromString(req.text)

    title = detailsPageElements.xpath('//h1')[0].text_content().strip()

    iafdURL = ''
    date = ''
    actors = []
    for scene in IAFDStudioElements.xpath('//table[@id="studio"]/tbody/tr'):
        searchTitle = scene.xpath('.//a')[0].text_content().split('(')[0].strip()
        if title.lower() == searchTitle.lower():
            iafdURL = 'https://www.iafd.com%s' % scene.xpath('.//a/@href')[0]
            break

    if iafdURL:
        req = req = PAutils.HTTPRequest(iafdURL)
        IAFDSceneElements = HTML.ElementFromString(req.text)

        date = IAFDSceneElements.xpath('//p[contains(., "Release Date")]//following-sibling::p[@class="biodata"]')[0].text_content().strip()
        actors = IAFDSceneElements.xpath('//div[@class="castbox"]')

    # Title
    metadata.title = title

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="videoDetails clear"]/p')[0].text_content().strip()

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.studio = tagline
    metadata.collections.add(tagline)

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="featuring clear"]//li[./a]'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in actors:
        actorName = actorLink.text_content().strip()
        actorPhotoURL = actorLink.xpath('.//img/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Release Date
    if date:
        date_object = datetime.strptime(date, '%b %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Posters
    xpaths = [
        '//div[@class="player"]/script',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            match = re.search(r'(?<=(poster=")).*?(?=")', img.text_content())
            if match:
                img = match.group(0)
                if 'http' not in img:
                    img = PAsearchSites.getSearchBaseURL(siteNum) + img

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
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
