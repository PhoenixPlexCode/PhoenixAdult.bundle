import PAsearchSites
import PAutils

xPathMap = {
    'SexBabesVR': {
        'date': '//div[contains(@class, "video-additional")]/div/span[@property="dc:date"]',
        'summary': '//div[contains(@class, "video-group-bottom")]/p',
        'actor': '//div[@class="video-actress-name"]//a',
        'actorPhoto': '//div[contains(@class, "model-img-wrapper")]/figure/a/img',
        'images': '//div[contains(@class, "video-gallery")]//div//figure//a'
    },
    'StasyQ VR': {
        'date': '//div[@class="video-meta-date"]',
        'summary': '//div[@class="video-info"]/p',
        'actor': '//div[@class="model-one-inner js-trigger-lazy-item"]//a',
        'actorPhoto': '//div[contains(@class, "model-one-inner")]//img',
        'images': '//div[contains(@class, "video-gallery")]//div//figure//a'
    },
    'RealJamVR': {
        'date': '//div[@class="c-video-item-header-date date"]',
        'summary': '//div[@class="c-video-item-desc desc"]',
        'actor': '//div[@class="c-video-item-header-featuring featuring commed"]//a',
        'actorPhoto': '//div[@class="row actor-info"]//img',
        'images': '//a[@class="c-video-item-scene-previews-link"]'
    }
}


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.lower().replace(' ', '-')
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    titleNoFormatting = searchResults.xpath('//h1')[0].text_content().strip()
    curID = searchData.encoded

    releaseDate = ''
    for key in xPathMap.keys():
        date = searchResults.xpath(xPathMap[key]['date'])
        if date:
            date = date[0].text_content().strip()
            releaseDate = parse(date).strftime('%Y-%m-%d')
            break

    score = 100

    results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + metadata_id[0]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    siteName = PAsearchSites.getSearchSiteName(siteNum)
    siteXPath = xPathMap.get(siteName)

    # Title
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath(siteXPath['summary'])[0].text_content().strip()

    # Studio
    metadata.studio = siteName

    # Tagline and Collection
    metadata.collections.clear()
    rawtagline = detailsPageElements.xpath('//title')[0].text_content().strip()
    if '|' in rawtagline:
        tagline = rawtagline.split('|')[1].strip()
    elif '-' in rawtagline:
        tagline = rawtagline.split('-')[0].strip()

    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    maybeDate = detailsPageElements.xpath(siteXPath['date'])
    if maybeDate:
        date = maybeDate[0].text_content().strip()
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[contains(@class, "tags")]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath(siteXPath['actor']):
        actorName = actorLink.text_content().strip()
        actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        actorPhotoURL = actorPage.xpath(siteXPath['actorPhoto'])[0].get('src').split('?')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    for poster in detailsPageElements.xpath(siteXPath['images']):
        img = poster.get('href').split('?')[0]
        if img.startswith('http'):
            art.append(img)

    poster = detailsPageElements.xpath('//div[@class="splash-screen fullscreen-message is-visible"] | //dl8-video')[0]
    img = poster.get('poster')
    if not img:
        img = poster.get('style').split('url(')[1].split(')')[0]

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
