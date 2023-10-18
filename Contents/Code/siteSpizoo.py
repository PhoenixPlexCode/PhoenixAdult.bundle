import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = urllib.quote('"%s"' % searchData.title)
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@class="category_listing_wrapper_updates"]'):
        titleNoFormatting = searchResult.xpath('.//h3')[0].text_content().strip()
        if titleNoFormatting[-3:] == ' 4k':
            titleNoFormatting = titleNoFormatting[:-3].strip()
        curID = PAutils.Encode(searchResult.xpath('.//a/@href')[0])

        try:
            xPath = PAutils.getDictValuesFromKey(xPathDB, str(siteNum))
            releaseDate = parse(searchResult.xpath(xPath[0])[-1].strip()).strftime('%Y-%m-%d')
        except:
            releaseDate = ''

        if searchData.date and releaseDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    title = detailsPageElements.xpath('//h1/text() | //video/@data-video')[0].strip()
    if title[-3:] == ' 4k':
        title = title[:-3].strip()
    metadata.title = PAutils.parseTitle(title, siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[@class="description"] | //p[@class="description-scene"] | //h2/following-sibling::p')[0].text_content().strip()

    # Studio
    metadata.studio = 'Spizoo'

    # Tagline and Collection(s)
    try:
        tagline = detailsPageElements.xpath('//i[@id="site"]/@value')[0].strip()
    except:
        if 'Spizoo' not in PAsearchSites.getSearchSiteName(siteNum):
            tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//p[@class="date"]')
    if date:
        date = date[0].text_content()[:10]
        date_object = datetime.strptime(date, '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    genres = detailsPageElements.xpath('//div[@class="categories-holder"]/a|//div[./h3[contains(., "Categories")]]/a')
    if genres:
        for genreLink in genres:
            genreName = genreLink.text_content().lower().strip()

            movieGenres.addGenre(genreName)

    # Actor(s)
    if siteNum == 1374:
        xPath = '//div[./h3[contains(., "Girls")]]/a'
    elif siteNum == 577:
        xPath = '//div[./h3[contains(., "playmates")]]/a'
    else:
        xPath = '//h3[text()="Pornstars:"]/../a'

    for actorLink in detailsPageElements.xpath(xPath):
        actorName = actorLink.text_content().replace('.', '').strip()
        actorPhotoURL = ''

        actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        try:
            actorPhotoURL = actorPage.xpath('//div[@class="model-bio-pic"]/img/@src')[0]
        except:
            actorPhotoURL = actorPage.xpath('//div[@class="model-bio-pic"]/img/@src0_1x')[0]

        if actorPhotoURL:
            if 'http' not in actorPhotoURL:
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//section[@id="photos-tour"]//img[contains(@class, "update_thumb thumbs")]/@src',
        '//div[@class="content-block-video"]//img/@alt'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if '&imgh' in img:
                img = img.split('&imgh')[0]

            art.append(img)

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        # Remove Timestamp and Token from URL
        cleanUrl = posterUrl.split('?')[0]
        art[idx - 1] = cleanUrl
        if not PAsearchSites.posterAlreadyExists(cleanUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[cleanUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


xPathDB = {
    ('293', '571', '572', '573', '574', '575', '576', '1374'): ['.//div[./h4[contains(., "date")]]/text()'],
    ('577', '1757'): ['.//div[./h4[contains(., "date")]]/p/text()']
}
