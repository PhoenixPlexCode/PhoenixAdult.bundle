import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="item-video-overlay"]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('./a')[0].get('title').strip(), siteNum)
        curID = PAutils.Encode(searchResult.xpath('./a/@href')[0])
        releaseDate = parse(searchResult.xpath('.//p[@class="video-date"]')[0].text_content().strip()).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//div[@class="main-info-left"]/h1')[0].text_content().strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[@class="description"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'LoveHerFilms'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="date"]')[0].text_content().strip()
    if date:
        date_object = datetime.strptime(date, '%B %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="video-tags"]/a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)
    movieGenres.addGenre('Foot Sex')

    # Actor(s)
    actors = detailsPageElements.xpath('//div[@class="featured"]/a')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            actorPhotoURL = ''
            try:
                actorPageURL = actorLink.get('href')
                req = PAutils.HTTPRequest(actorPageURL)
                actorPage = HTML.ElementFromString(req.text)
                actorPhotoURL = actorPage.xpath('//div[@class="picture"]/img')[0].get("src0_3x")
                if 'http' not in actorPhotoURL:
                    actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL
            except:
                pass

            movieActors.addActor(actorName, actorPhotoURL)

    # Photos
    xpaths = [
        '//meta[@property="og:image"]/@content',
        '//div[@class="photos"]/a/img/@src'
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
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
