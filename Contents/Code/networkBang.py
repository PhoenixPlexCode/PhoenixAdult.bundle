import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchResults = []
    searchData.encoded = searchData.title.replace(' ', '+')

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchPageElements = HTML.ElementFromString(req.text)

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        sceneURL = sceneURL.split('?')[0]
        if 'com/video/' in sceneURL and 'index.php/' not in sceneURL not in searchResults:
            searchResults.append(sceneURL)

    for searchURL in searchResults:
        req = PAutils.HTTPRequest(searchURL)
        detailsPageElements = HTML.ElementFromString(req.text)
        videoPageElements = json.loads(detailsPageElements.xpath('//script[@type="application/ld+json"]')[-1].text_content().replace('\n', '').strip())

        titleNoFormatting = PAutils.parseTitle(PAutils.cleanHTML(videoPageElements['name']), siteNum)
        curID = PAutils.Encode(searchURL)

        date = videoPageElements['datePublished']
        if date:
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        displayDate = releaseDate if date else ''

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    for searchResult in searchPageElements.xpath('//ul[contains(@class, "grid")]//li[contains(@class, "relative")]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//a[contains(@class, "block")] | .//span[contains(@class, "block")]')[0].text_content().strip(), siteNum)
        sceneURL = searchResult.xpath('.//a/@href')[0]
        if 'http' not in sceneURL:
            sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
        curID = PAutils.Encode(sceneURL)

        try:
            date = searchResult.xpath('.//span[@class="hidden xs:inline-block truncate"]/text()')[0].strip()
        except:
            date = ''

        if date:
            releaseDate = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        displayDate = releaseDate if date else ''

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        if sceneURL not in searchResults:
            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    videoPageElements = json.loads(detailsPageElements.xpath('//script[@type="application/ld+json"]')[-1].text_content().replace('\n', '').strip())

    # Title
    metadata.title = PAutils.parseTitle(PAutils.cleanHTML(videoPageElements['name']), siteNum)

    # Summary
    metadata.summary = PAutils.cleanHTML(videoPageElements['description'])

    # Studio
    metadata.studio = re.sub(r'bang(?=(\s|$))(?!\!)', 'Bang!', PAutils.parseTitle(videoPageElements['productionCompany']['name'].strip(), siteNum), flags=re.IGNORECASE)

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = ""
    dvdTitle = ""
    try:
        tagline = re.sub(r'bang(?=(\s|$))(?!\!)', 'Bang!', PAutils.parseTitle(detailsPageElements.xpath('//p[contains(., "eries:")]/a[contains(@href, "video")]')[0].text_content().strip(), siteNum), flags=re.IGNORECASE)
    except:
        pass

    if tagline:
        metadata.tagline = tagline
        metadata.collections.add(tagline)
    else:
        metadata.collections.add(metadata.studio)

    try:
        dvdTitle = PAutils.parseTitle(detailsPageElements.xpath('//p[contains(., "Movie")]/a[contains(@href, "dvd")]')[0].text_content(), siteNum)
    except:
        pass

    if dvdTitle and siteNum == 1365:
        metadata.collections.add(dvdTitle)

    # Release Date
    date = videoPageElements['datePublished']
    if date:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actors
    movieActors.clearActors()
    if siteNum == 1365:
        actorXPATH = '//div[contains(@class, "clear-both")]//a[contains(@href, "pornstar")]'
    else:
        actorXPATH = '//div[contains(@class, "video-actors")]'

    for actorLink in detailsPageElements.xpath(actorXPATH):
        if siteNum == 1365:
            actorName = actorLink.text_content()

            modelURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.xpath('.//@href')[0]
            req = PAutils.HTTPRequest(modelURL)
            modelPage = HTML.ElementFromString(req.text)

            modelPageElements = json.loads(modelPage.xpath('//script[@type="application/ld+json"]')[0].text_content().strip())

            actorPhotoURL = modelPageElements['image'].split('?')[0].strip()
        else:
            actorName = actorLink.xpath('.//span')[0].text_content()
            actorPhotoURL = actorLink.xpath('.//img/@src')[0].split('?')[0]

        if actorName:
            movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[@class="actions"]/a | //a[@class="genres"]'):
        genreName = genreLink.text_content()

        movieGenres.addGenre(genreName)

    # Posters
    if 'covers' in videoPageElements['thumbnailUrl']:
        art.append(videoPageElements['thumbnailUrl'])
    else:
        match = re.search(r'(?<=shots/)\d+', videoPageElements['thumbnailUrl'])
        if match:
            movieID = match.group(0)
            art.append('https://i.bang.com/covers/%s/front.jpg' % movieID)
        art.append(videoPageElements['thumbnailUrl'])

    if 'trailer' in videoPageElements:
        for img in videoPageElements['trailer']:
            art.append(img['thumbnailUrl'])

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                im = StringIO(image.content)
                images.append(image)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                    posterExists = True
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    if not posterExists:
        for idx, image in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[art[idx - 1]] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
