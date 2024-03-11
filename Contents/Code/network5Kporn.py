import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    cookies = {'nats': 'MC4wLjMuNTguMC4wLjAuMC4w'}
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded, cookies=cookies)
    searchResults = HTML.ElementFromString(req.json()['html'])
    for searchResult in searchResults.xpath('//div[@class="ep"]'):
        titleNoFormatting = searchResult.xpath('.//h3[@class="ep-title"]')[0].text_content().strip()
        sceneURL = searchResult.xpath('.//a/@href')[0]
        curID = PAutils.Encode(sceneURL)

        releaseDate = searchData.dateFormat() if searchData.date else ''

        score = 100 - Util.LevenshteinDistance(titleNoActors.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = ''
    if len(metadata_id) > 2:
        sceneDate = metadata_id[2]

    cookies = {'nats': 'MC4wLjMuNTguMC4wLjAuMC4w'}
    req = PAutils.HTTPRequest(sceneURL, cookies=cookies)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//title')[0].text_content().split('|')[0], siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "video-summary")]//p[@class=""]')[0].text_content()

    # Studio
    metadata.studio = '5Kporn'

    # Tagline and Collection(s)
    metadata.tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.collections.add(metadata.tagline)

    # Date
    date = detailsPageElements.xpath('//h5[contains(., "Published")]')
    if date:
        date = date[0].text_content().replace('Published:', '').strip()
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres

    # Actor(s)
    actors = detailsPageElements.xpath('//h5[contains(., "Starring")]/a')
    for actorLink in actors:
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        modelURL = actorLink.xpath('.//@href')[0]
        req = PAutils.HTTPRequest(modelURL, cookies=cookies)
        actorsPageElements = HTML.ElementFromString(req.text)

        img = actorsPageElements.xpath('//img[@class="model-image"]/@src')
        if img:
            actorPhotoURL = img[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[contains(@class, "gal")]//img/@src',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(img)

    for idx in range(1, 3):
        photoPageURL = '%s/photoset?page=%d' % (sceneURL, idx)
        req = PAutils.HTTPRequest(photoPageURL, cookies=cookies)
        photoPageElements = HTML.ElementFromString(req.text)
        for img in photoPageElements.xpath('//img[@class="card-img-top"]/@src'):
            if 'full' not in img:
                art.append(img)

    Log('Artwork found: %d' % len(art))
    images = []
    posterExists = False
    for idx, posterUrl in enumerate(art, 1):
        # Remove Timestamp and Token from URL
        cleanUrl = re.sub(r'\/expiretime=.*?(?<=\/).*?(?=\/)', '', posterUrl.split('?')[0])
        art[idx - 1] = cleanUrl
        if not PAsearchSites.posterAlreadyExists(cleanUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': sceneURL}, cookies=cookies)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    metadata.posters[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
                    posterExists = True
                if width > 1000 and width > height:
                    # Item is an art item
                    images.append((image, cleanUrl))
                    metadata.art[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass
        elif PAsearchSites.posterOnlyAlreadyExists(cleanUrl, metadata):
            posterExists = True

    if not posterExists:
        for idx, (image, cleanUrl) in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
