import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    pages = searchResults.xpath('//div[@class="pagination"]/ul/li/a/@href')
    for link in pages:
        req = PAutils.HTTPRequest(link)
        searchResults = HTML.ElementFromString(req.text)
        for searchResult in searchResults.xpath('//li[.//div[@class="time-infos"]]//a'):
            siteName = PAsearchSites.getSearchSiteName(siteNum)
            titleNoFormatting = searchResult.xpath('./@title')[0].strip()
            curID = PAutils.Encode(searchResult.xpath('./@href')[0])

            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, siteName), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@itemprop="headline"]//span/text()')[-1].lstrip("- ").strip()

    # Summary
    description = detailsPageElements.xpath('//div[contains(@class, "video-embed")]//p')
    if description:
        metadata.summary = description[0].text_content().strip()

    # Release date
    date = detailsPageElements.xpath('//div[@class="post_date"]/text()')
    if date:
        date_object = parse(date[0])
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//div[@itemprop="keywords"]//a')
    for genreLink in genres:
        genreName = genreLink.xpath('./text()')[0].strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[@itemprop="actor"]//a/text()')
    for actorLink in actors:
        actorName = actorLink.strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Posters
    art = []
    xpaths = [
        '//img[contains(@class, "fp-splash")]/@src',
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
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
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
