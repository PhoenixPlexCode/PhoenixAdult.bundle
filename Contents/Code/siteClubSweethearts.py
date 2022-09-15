import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.replace(' ', '_').replace('\'', '')
    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content().strip(), siteNum)
    curID = PAutils.Encode(sceneURL)
    date = detailsPageElements.xpath('//p[@class="update-info-line regular"]/b')[0].text_content().strip()
    releaseDate = parse(date).strftime('%Y-%m-%d')

    if searchData.date:
        score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
    else:
        score = 90

    results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [ClubSeventeen] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content().strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[contains(@class, "description-text")]')[0].text_content().strip()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.clear()
    try:
        tagline = detailsPageElements.xpath('//b[contains(., "Series")]//following-sibling::a')[0].text_content().strip()
        metadata.tagline = tagline
        metadata.collections.add(tagline)
    except:
        pass

    # Release Date
    date = detailsPageElements.xpath('//p[@class="update-info-line regular"]/b')[0].text_content().strip()
    if date:
        date_object = datetime.strptime(date, '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//a[@class="underline-text"]'):
        genreName = PAutils.parseTitle(genreLink.text_content().strip(), siteNum)

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//b[contains(., "Performers")]//following-sibling::a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + '/' + actorLink.get("href")
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        img = actorPage.xpath('//img[@class="model-profile-image"]/@src')
        if img:
            actorPhotoURL = img[0]
            if 'http' not in actorPhotoURL:
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@class="video-wrapper"][.//a[contains(@href, "%s")]]//@data-image' % sceneURL.split('=')[-1].lower()
    ]

    if actorPage:
        for xpath in xpaths:
            for img in actorPage.xpath(xpath):
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
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
