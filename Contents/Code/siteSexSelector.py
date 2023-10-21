import PAsearchSites
import PAutils


def getJSONfromPage(url):
    req = PAutils.HTTPRequest(url)
    detailsPageElements = HTML.ElementFromString(req.text)

    if req.ok:
        data = None
        node = detailsPageElements.xpath('//script[contains(@id, "__NEXT_DATA__")]')
        if node:
            data = node[0].text_content()

        if data:
            return json.loads(data)['props']['pageProps']['shoot']

    return None


def search(results, lang, siteNum, searchData):
    searchID = None
    parts = searchData.title.split()
    sceneResults = []
    if unicode(parts[0], 'UTF-8').isdigit():
        searchID = parts[0]
        searchData.title = searchData.title.replace(searchID, '').strip()

        directSceneURL = '%svideo/%s/%s' % (PAsearchSites.getSearchSearchURL(siteNum), searchID, slugify(searchData.title))
        sceneResults = [directSceneURL]

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        sceneURL = sceneURL.split('?')[0]
        if '/video/' in sceneURL and sceneURL not in sceneResults:
            sceneResults.append(sceneURL)

    for sceneURL in sceneResults:
        detailsPageElements = getJSONfromPage(sceneURL)

        if detailsPageElements:
            titleNoFormatting = PAutils.parseTitle(detailsPageElements['title'].strip(), siteNum)
            curID = PAutils.Encode(sceneURL)

            date = detailsPageElements['publishDate'].split('T')[0]
            if date:
                releaseDate = parse(date).strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''

            displayDate = releaseDate if date else ''

            if searchData.date and displayDate:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title, titleNoFormatting)

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    detailsPageElements = getJSONfromPage(sceneURL)

    # Title
    metadata.title = detailsPageElements['title']

    # Summary
    metadata.summary = detailsPageElements['description']

    # Studio
    metadata.studio = 'BangBros'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements['publishDate'].split('T')[0]
    if date:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements['tag']:
        genreName = genreLink['name']

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements['model']:
        actorName = actorLink['name']
        actorPhotoURL = '%s_next/image?url=https%%3A%%2F%%2Fimages2.bangbros.com%%2Fmodelprofiles%%2F%s_big.jpg&w=828&q=75' % (PAsearchSites.getSearchSearchURL(siteNum), actorLink['code'])

        movieActors.addActor(actorName, actorPhotoURL)

    # Photos
    code = detailsPageElements['code']
    for idx in range(21):
        poster = '%s_next/image?url=https%%3A%%2F%%2Fsm-members.bangbros.com%%2Fshoots%%2Fsexselector%%2F%s%%2Fposter%%2F%s_%02d_2160.jpg&w=1080&q=75' % (PAsearchSites.getSearchSearchURL(siteNum), code, code, idx)

        art.append(poster)

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
