import PAsearchSites
import PAutils

xPathMap = {
    'SexBabesVR': {
        'date': '//div[contains(@class, "video-detail__description--container")]/div[last()]',
        'summary': '//div[contains(@class, "video-detail")]/div/p',
        'tags': '//a[contains(@class, "tag")]',
        'actor': '//div[@class="video-detail__description--author"]//a',
        'actorPhoto': '//img[contains(@class, "cover-picture")]',
        'images': '//a[contains(@data-fancybox, "gallery")]//img/@src',
        'poster': '//dl8-video'
    },
    'StasyQ VR': {
        'date': '//div[@class="video-meta-date"]',
        'summary': '//div[@class="video-info"]/p',
        'tags': '//div[contains(@class, "my-2 lh-lg")]//a',
        'actor': '//div[@class="model-one-inner js-trigger-lazy-item"]//a',
        'actorPhoto': '//div[contains(@class, "model-one-inner")]//img',
        'images': '//div[contains(@class, "video-gallery")]//div//figure//a/@href',
        'poster': '//div[@class="splash-screen fullscreen-message is-visible"] | //dl8-video'
    },
    'RealJamVR': {
        'date': '//div[@class="ms-4 text-nowrap"]',
        'summary': '//div[@class="opacity-75 my-2"]',
        'tags': '//div[contains(@class, "my-2 lh-lg")]//a',
        'actor': '//div[@class="scene-view mx-auto"]/a',
        'actorPhoto': '//div[@class="col-12 col-lg-4 pe-lg-0"]//img',
        'images': '//img[@class="img-thumb"]/@src',
        'poster': '//div[@class="splash-screen fullscreen-message is-visible"] | //dl8-video'
    }
}


def search(results, lang, siteNum, searchData):
    siteName = PAsearchSites.getSearchSiteName(siteNum).lower() + '-'
    searchData.encoded = searchData.filename.lower().replace(' ', '-').replace('_', ' ').replace(siteName, '')
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

    results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (
        titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

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
    maybeSummary = detailsPageElements.xpath(siteXPath['summary'])
    if maybeSummary:
        metadata.summary = maybeSummary[0].text_content().strip()

    # Studio
    metadata.studio = siteName

    # Tagline and Collection(s)
    tagline = detailsPageElements.xpath('//title')[0].text_content().strip()
    if '|' in tagline:
        tagline = tagline.split('|')[1].strip()
    elif '-' in tagline:
        tagline = tagline.split('-')[0].strip()

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
    for genreLink in detailsPageElements.xpath(siteXPath['tags']):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath(siteXPath['actor']):
        actorName = actorLink.text_content().strip()
        actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        actorPhotoURL = ""
        maybeActorPhoto = actorPage.xpath(siteXPath['actorPhoto'])
        if maybeActorPhoto:
            actorPhotoURL = maybeActorPhoto[0].get('src').split('?')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    for poster in detailsPageElements.xpath(siteXPath['images']):
        img = poster.split('?')[0]
        if img.startswith('http'):
            art.append(img)

    poster = detailsPageElements.xpath(siteXPath['poster'])[0]
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
