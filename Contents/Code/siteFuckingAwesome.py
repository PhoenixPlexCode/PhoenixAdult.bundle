import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="gallery"]/div'):
        titleNoFormatting = searchResult.xpath('.//div[@class="video-title truncate"]/a')[0].text_content().strip()
        curID = PAutils.Encode(PAsearchSites.getSearchBaseURL(siteNum) + searchResult.xpath('.//div[@class="video-title truncate"]/a/@href')[0].strip())
        releaseDate = parse(searchResult.xpath('.//span[@class="small date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
        firstActor = searchResult.xpath('.//span[@class="subtitle small"]/a')[0].text_content().strip()

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s %s in %s [FuckingAwesome]' % (releaseDate, firstActor, titleNoFormatting), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="more text-justify"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'FuckingAwesome'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="videodate"]/strong')[0].text_content().strip()
    if date:
        date_object = datetime.strptime(date, '%B %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="tags"]/ul/li/a'):
        genreName = genreLink.text_content().strip().lower()

        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = detailsPageElements.xpath('//div[@class="pornstarnames"]/ul/li/a[contains(@href, "pornstars")]')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = str(actorLink.text_content().strip())

            actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.get("href")
            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            actorPhotoURL = actorPage.xpath('//div[@class="pornstar-pic "]/img/@src')[0]
            if 'http' not in actorPhotoURL:
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//span[@class="et_pb_image_wrap "]/img/@content'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(img)

    try:
        photoPageUrl = PAsearchSites.getSearchBaseURL(siteNum) + detailsPageElements.xpath('//li[@class="photos"]/a/@href')[0]
        req = PAutils.HTTPRequest(photoPageUrl)
        photoPage = HTML.ElementFromString(req.text)
        unlockedPhotos = photoPage.xpath('//div[@class="my-gallery"]/a/@href')
        for unlockedPhoto in unlockedPhotos:
            if 'http' not in unlockedPhoto:
                art.append(PAsearchSites.getSearchBaseURL(siteNum) + unlockedPhoto)
            else:
                art.append(unlockedPhoto)
    except:
        pass

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
