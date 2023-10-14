import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    for searchPageNum in range(1, 3):
        url = PAsearchSites.getSearchSearchURL(siteNum) + '%s&page=%d' % (searchData.encoded, searchPageNum)
        req = PAutils.HTTPRequest(url)
        searchResults = HTML.ElementFromString(req.text)
        for searchResult in searchResults.xpath('//div[contains(@class,"thumb thumb-photo")]'):
            titleNoFormatting = searchResult.xpath('.//a[@class="thumb__title-link"]')[0].text_content().strip()
            titleNoFormatting = PAutils.parseTitle(titleNoFormatting, siteNum)

            curID = PAutils.Encode(searchResult.xpath('.//a[@class="thumb__title-link"]/@href')[0])
            releaseDate = parse(searchResult.xpath('.//time')[0].text_content()).strftime('%Y-%m-%d')
            subSite = searchResult.xpath('.//a[@class="thumb__detail__site-link clr-grey"]')[0].text_content().strip()

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [TMW/%s] %s' % (titleNoFormatting, subSite, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    title = detailsPageElements.xpath('//h1[@id="video-title"]')[0].text_content().strip()
    title = PAutils.parseTitle(title, siteNum)
    metadata.title = title

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[@class="video-description-text"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Teen Mega World'

    # Tagline and Collection(s)
    tagline = detailsPageElements.xpath('//a[@class="video-site-link btn btn-ghost btn--rounded"]')[0].text_content().strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//span[@title="Video release date"]')[0].text_content().strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//a[@class="video-actor-link actor__link"]'):
        actorName = actorLink.text_content().strip()

        actorPageURL = actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPageElements = HTML.ElementFromString(req.text)
        actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + '/' + actorPageElements.xpath('//div[@class="model-profile-image-wrap"]//img/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    for genreLink in detailsPageElements.xpath('//a[@class="video-tag-link"]'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Posters
    xpaths = [
        '//img[@id="video-cover-image"]/@src',
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            if 'http' not in poster:
                poster = PAsearchSites.getSearchBaseURL(siteNum) + '/' + poster

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
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
