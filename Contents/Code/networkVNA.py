import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = searchData.title.split(' ', 1)[0]
    if unicode(sceneID, 'UTF-8').isdigit():
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()
    else:
        sceneID = None

    searchResults = []
    if sceneID:
        directURL = PAsearchSites.getSearchSearchURL(siteNum) + sceneID
        searchResults.append(directURL)

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if '/videos/' in sceneURL and '/page/' not in sceneURL:
            if sceneURL not in searchResults:
                searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        if req.ok:
            detailsPageElements = HTML.ElementFromString(req.text)
            titleNoFormatting = detailsPageElements.xpath('//h1[@class="customhcolor"]')[0].text_content()
            if 'http' not in sceneURL:
                sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + sceneID
            curID = PAutils.Encode(sceneURL)

            releaseDate = ''
            date = detailsPageElements.xpath('//div[@class="date"]')[0].text_content().strip()
            if date:
                releaseDate = parse(date).strftime('%Y-%m-%d')

            if searchData.date and releaseDate:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='[%s] %s %s' % (PAsearchSites.getSearchSiteName(siteNum), titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@class="customhcolor"]')[0].text_content()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="customhcolor2"]')[0].text_content().strip()

    if siteNum == 1287:
        metadata.summary = metadata.summary.split('Don\'t forget to join me')[0]

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.tagline = metadata.studio
    metadata.collections.add('VNA Network')
    metadata.collections.add(metadata.studio)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="date"]')[0].text_content().strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//h4[@class="customhcolor"]')[0].text_content().strip().split(',')
    for genre in genres:
        movieGenres.addGenre(genre.strip())

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//h3[@class="customhcolor"]')[0].text_content().replace('&nbsp', '').split(',')
    for actor in actors:
        actorName = actor.strip()
        if actorName.endswith(' XXX'):
            actorName = actorName[:-4]

        movieActors.addActor(actorName, '')

    # Posters/Background
    art = []
    xpaths = [
        '//center//img/@src',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if 'http' not in img:
                img = PAsearchSites.getSearchBaseURL(siteNum) + '/' + img

            art.append(img)

    # add thumbnails not found on scene page
    thumb2 = art[0].replace('thumb_1', 'thumb_2')
    thumb3 = art[0].replace('thumb_1', 'thumb_3')
    art.append(thumb2)
    art.append(thumb3)

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
