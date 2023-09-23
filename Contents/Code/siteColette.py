import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    directURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.title.replace(' ', '_')
    searchResults = [directURL]

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if '/videos/' in sceneURL and sceneURL not in searchResults:
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL, cookies={"_warning": "True"})
        if '/join/' not in req.url:
            detailsPageElements = HTML.ElementFromString(req.text)

            titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//div[@class="row info"]/div/h1')[0].text_content().strip(), siteNum)
            subSite = PAsearchSites.getSearchSiteName(siteNum)
            curID = PAutils.Encode(sceneURL)
            releaseDate = parse(detailsPageElements.xpath('//h2')[0].text_content().strip()).strftime('%Y-%m-%d') or searchData.dateFormat()
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())
            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (titleNoFormatting, subSite), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL, cookies={"_warning": "True"})
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="row info"]/div/h1')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "info")]/p')[1].text_content().strip()

    # Studio
    metadata.studio = 'Colette'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release date
    date = parse(metadata_id[2]) or parse(detailsPageElements.xpath('//h2')[0].text_content().strip()).strftime('%Y-%m-%d')
    metadata.originally_available_at = date
    metadata.year = metadata.originally_available_at.year

    # Actor(s)
    actors = detailsPageElements.xpath('//div[contains(@class, "info")]/h2/a')
    for actorLink in actors:
        actorName = actorLink.text_content().strip()
        actorPageURL = actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL, cookies={"_warning": "True"})
        actorPage = HTML.ElementFromString(req.text)
        actorPhotoInterchange = actorPage.xpath('//img[@class="info-img"]/@data-interchange')[0]
        actorPhotoURL = actorPhotoInterchange.replace("[", "").replace("]", "").replace(", (small)", "").replace(", (medium)", "").replace(", (large)", "").split(",")[2].strip()
        movieActors.addActor(actorName, actorPhotoURL)

    # Genre
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

    # Posters
    xpaths = [
        '//div[contains(@class, "gallery-item")]/a/img/@src',
        '//div[contains(@class, "video-tour")]//a/img/@src',
    ]
    interchangeXpaths = [
        '//div[contains(@class, "widescreen")]//img/@data-interchange',
        '//div[contains(@class, "columns")]/img/@data-interchange',
    ]
    elements = [detailsPageElements]
    ID = sceneURL.replace('https://www.colette.com/videos/', '')
    galleryURL = sceneURL.replace('/videos/', '/galleries/')
    if ID in galleryFix:
        galleryURL = galleryURL.replace(ID, galleryFix[ID])
    req = PAutils.HTTPRequest(galleryURL, cookies={"_warning": "True"})
    galleryPageElements = HTML.ElementFromString(req.text)
    elements.insert(0, galleryPageElements)
    for element in elements:
        for xpath in xpaths:
            for img in element.xpath(xpath):
                art.append(img)
        for xpath in interchangeXpaths:
            for img in element.xpath(xpath):
                interchangeIMG = img.replace("[", "").replace("]", "").replace(", (small)", "").replace(", (medium)", "").replace(", (large)", "").split(",")[2].strip()
                art.append(interchangeIMG)
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, cookies={"_warning": "True"})
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


galleryFix = {
    'The_Perfect_Threesome': 'The_Perfect_Threesome_or_Pussy_Galore',
}
