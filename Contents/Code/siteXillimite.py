import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//a[contains(@class, "movies")]'):
        titleNoFormatting = searchResult.xpath('.//img/@alt')[0].strip()

        sceneURL = searchResult.get('href')
        if not sceneURL.startswith('http'):
            sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL

        curID = PAutils.Encode(sceneURL)
        releaseDate = searchData.dateFormat() if searchData.date else ''

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

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
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content().strip()

    # Summary
    description = detailsPageElements.xpath('//div[@id="synopsis"]')
    if description:
        description = description[0].text_content()
    else:
        description = detailsPageElements.xpath('//meta[@name="twitter:description"]/@content')
        if description:
            description = description[0]

    if description:
        metadata.summary = description.replace('</br>', '\n').replace('<br>', '\n').strip()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="casting"]//div[contains(@class, "slider-xl")]//a[@class="movies"]/img'):
        actorName = actorLink.get('alt')
        actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.get('data-src')

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[contains(@class, "covers")]/a[contains(@class, "cover")]/@href',
        '//div[contains(@class, "screenshots")]//div[@class="slides"]//a/@href',
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            poster = PAsearchSites.getSearchBaseURL(siteNum) + poster.replace('blur9/', '/')

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
                if width > 100 and idx > 1:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
