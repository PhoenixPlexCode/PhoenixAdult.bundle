import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = 0

    parts = searchData.title.split()
    if unicode(parts[0], 'utf8').isdigit():
        sceneID = parts[0]
        searchData.encoded = searchData.title.replace(sceneID, '', 1).strip()

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    if siteNum == 1583:
        for searchResult in searchResults.xpath('//div[@class="girl"]'):
            titleNoFormatting = '%s %s' % (searchResult.xpath('.//span[@class="name"]')[0].text_content().strip(), searchResult.xpath('.//span[@class="age"]')[0].text_content().strip())

            sceneURL = searchResult.xpath('./div/a/@href')[0]
            if 'http' not in sceneURL:
                sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
            curID = PAutils.Encode(sceneURL)
            searchID = int(sceneURL.split('-')[-1].replace('/', '').strip())

            subSite = searchResult.xpath('//head/title')[0].text_content().strip()

            date = searchResult.xpath('.//span[@class="updated"]')
            if date:
                releaseDate = datetime.strptime(date[0].text_content().strip(), '%m/%d/%Y').strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''

            displayDate = releaseDate if date else ''

            if int(sceneID) == searchID:
                score = 100
            elif searchData.date and displayDate:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [CzechAV/%s] %s' % (titleNoFormatting, subSite, displayDate), score=score, lang=lang))
    else:
        for searchResult in searchResults.xpath('//div[@class="episode__title"]'):
            titleNoFormatting = PAutils.parseTitle(searchResult.xpath('./a/h1|./a/h2')[0].text_content().strip(), siteNum)
            curID = PAutils.Encode(searchResult.xpath('./a/@href')[0])
            subSite = searchResult.xpath('//head/title')[0].text_content().strip()
            releaseDate = searchData.dateFormat() if searchData.date else ''

            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [CzechAV/%s]' % (titleNoFormatting, subSite), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    if siteNum == 1583:
        title = detailsPageElements.xpath('//span[@class="name"]')[0].text_content().strip()
    else:
        title = detailsPageElements.xpath('//h1[@class="nice-title"]|//h2[@class="nice-title"]')[0].text_content().split(':')[-1].strip()
    metadata.title = PAutils.parseTitle(title, siteNum)

    # Summary
    description = detailsPageElements.xpath('//div[contains(@class, "desc")]//p')
    if description:
        if siteNum == 1583:
            metadata.summary = description[1].text_content().strip()
        else:
            metadata.summary = description[0].text_content().strip()

    # Studio
    metadata.studio = 'Czech Authentic Videos'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//ul[@class="tags"]/li'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    if siteNum == 1583:
        actorName = '%s %s' % (title, detailsPageElements.xpath('//span[@class="age"]')[0].text_content().strip())
        movieActors.addActor(actorName, detailsPageElements.xpath('//div[contains(@class, "gallery")]//@href')[0])

    # Posters
    xpaths = [
        '//meta[@property="og:image"]/@content',
        '//img[@class="thumb"]/@src',
        '//div[contains(@class, "gallery")]//@href'
    ]

    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            art.append(poster)

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
