import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchResults = []
    searchID = None

    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()
    else:
        sceneID = re.sub(r'\D', '', searchData.title)
        actorName = re.sub(r'\s\d.*', '', searchData.title).replace(' ', '-')
        directURL = '%s%s/%s/' % (PAsearchSites.getSearchSearchURL(siteNum), actorName, sceneID)
        searchResults.append(directURL)

    urlID = PAsearchSites.getSearchSearchURL(siteNum).replace(PAsearchSites.getSearchBaseURL(siteNum), '')

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if urlID in sceneURL and '?' not in sceneURL and sceneURL not in searchResults:
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        searchPageElements = HTML.ElementFromString(req.text)
        titleNoFormatting = PAutils.parseTitle(searchPageElements.xpath('//h1')[0].text_content().strip(), siteNum)

        if '404' not in titleNoFormatting:
            match = re.search(r'(?<=\/)\d+(?=\/)', sceneURL)
            if match:
                searchID = match.group(0)

            curID = PAutils.Encode(sceneURL)

            try:
                date = searchPageElements.xpath('//div[./span[contains(., "Date:")]]//span[@class="value"]')[0].text_content().strip()
            except:
                date = ''

            if date:
                releaseDate = parse(date).strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''
            displayDate = releaseDate if date else ''

            if searchID and searchID == sceneID:
                score = 100
            elif searchData.date and displayDate:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]

    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content().strip(), siteNum)

    # Summary
    summary_xpaths = [
        '//div[@class="p-desc"]',
        '//div[contains(@class, "desc")]'
    ]

    for xpath in summary_xpaths:
        for summary in detailsPageElements.xpath(xpath):
            metadata.summary = summary.text_content().replace('Read More »', '').strip()
            break

    # Studio
    metadata.studio = 'Score Group'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(metadata.tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Release Date
    date = detailsPageElements.xpath('//div/span[@class="value"]')
    if date:
        date = date[1].text_content().strip()
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//div/span[@class="value"]/a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    if siteNum == 1344:
        movieActors.addActor('Christy Marks', '')

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[@class="mb-3"]/a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Posters/Background
    match = re.search(r'posterImage: \'(.*)\'', req.text)
    if match:
        art.append(match.group(1))

    xpaths = [
        '//script[@type]/text()',
        '//div[contains(@class, "thumb")]/img/@src',
        '//div[contains(@class, "p-image")]/a/img/@src',
        '//div[contains(@class, "dl-opts")]/a/img/@src',
        '//div[contains(@class, "p-photos")]/div/div/a/@href',
        '//div[contains(@class, "gallery")]/div/div/a/@href'
    ]

    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            match = re.search(r'(?<=(poster: \')).*(?=\')', poster)
            if match:
                poster = match.group(0)

            if not poster.startswith('http'):
                poster = 'http:' + poster

            if 'shared-bits' not in poster:
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
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
