import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="video-post-content"]'):
        titleNoFormatting = searchResult.xpath('.//a[@class="video-post-main"]//img/@alt')[0]
        femaleActor = searchResult.xpath('.//span[@class="video-model-list w-100"]//a')[0].text_content()
        curID = PAutils.Encode(searchResult.xpath('.//a[@class="video-post-main"]/@href')[0])
        releaseDate = parse(searchResult.xpath('.//span[@class="video-data float-right"]//em')[0].text_content().strip()).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] [%s] %s' % (titleNoFormatting, femaleActor, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="video-page-header"]//h1')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="info-video-description"]//p')[0].text_content().strip()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//ul[@class="list-unstyled info-video-details"]//li[1]//span')
    if date:
        date = date[0].text_content().strip()
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="info-video-category"]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = detailsPageElements.xpath('//div[@class="info-video-models"]//a')
    for actorLink in actors:
        actorName = actorLink.text_content()
        actorPageURL = actorLink.get('href')

        req = PAutils.HTTPRequest(actorPageURL)
        detailsActorPage = HTML.ElementFromString(req.text)
        actorPhotoURL = detailsActorPage.xpath('//div[@class="m-images"]//img/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Director
    directorName = 'Markus Dupree'
    movieActors.addDirector(directorName, '')

    # Posters/Background
    xpaths = [
        '//div[@class="swiper-wrapper"]//figure//a/@href'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
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
