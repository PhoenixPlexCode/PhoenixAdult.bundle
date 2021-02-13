import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[contains(@class, "item-video")]'):
        titleNoFormatting = searchResult.xpath('./div[1]/a/@title')[0].strip()
        curID = PAutils.Encode('http:' + searchResult.xpath('./div[1]/a/@href')[0])

        if searchData.date:
            releaseDate = searchData.dateFormat()
        else:
            releaseDate = ''

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    searchData.encoded = searchData.title.lower().replace(' ', '-')
    directURL = PAsearchSites.getSearchSearchURL(siteNum).replace('/search.php?query=', '/trailers/') + searchData.encoded + '.html'

    directResults = [directURL]
    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        if '/trailers/' in sceneURL and sceneURL not in searchResults:
            directResults.append(sceneURL)

    for sceneURL in directResults:
        try:
            req = PAutils.HTTPRequest(sceneURL)
            detailsPageElements = HTML.ElementFromString(req.text)

            titleNoFormatting = detailsPageElements.xpath('//h1 | //h3')[0].text_content().strip()
            curID = PAutils.Encode(sceneURL)

            date = detailsPageElements.xpath('//div[contains(@class, "videoInfo")]/p/text()')
            if date:
                releaseDate = parse(date[0].strip()).strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''

            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))
        except:
            pass

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h3')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "videoDetails")]//p')[0].text_content().strip()

    # Studio
    metadata.studio = "Hussie Pass" if PAsearchSites.getSearchSiteName(siteNum) == "Hussie Pass" else 'BellaPass'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[contains(@class, "featuring")]//a[contains(@href, "/categories/")]'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[contains(@class, "featuring")]//a[contains(@href, "/models/")]')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content().strip()

            actorPageURL = actorLink.get('href')
            if actorPageURL.startswith('//'):
                actorPageURL = 'https:' + actorPageURL
            elif not actorPageURL.startswith('http'):
                actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPageURL

            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPage.xpath('//div[@class="profile-pic"]/img/@src0_3x')[0]

            movieActors.addActor(actorName, actorPhotoURL)

    # Release Date
    date = detailsPageElements.xpath('//div[contains(@class, "videoInfo")]/p/text()')
    if date:
        releaseDate = parse(date[0].strip()).strftime('%Y-%m-%d')
    else:
        releaseDate = sceneDate.dateFormat() if sceneDate else ''
    if releaseDate:
        date_object = parse(releaseDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Posters
    art = []
    setID = detailsPageElements.xpath('//img[contains(@class, "thumbs")]/@id | //div[contains(@class, "item-thumb")]//img/@id')[0]

    imgs = detailsPageElements.xpath('//img[contains(@class, "thumbs")]/@src0_3x | //div[contains(@class, "item-thumb")]//img/@src0_3x')
    for img in imgs:
        art.append(PAsearchSites.getSearchBaseURL(siteNum) + img)

    # Search Page
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + metadata.title.replace(' ', '+'))
    searchPageElements = HTML.ElementFromString(req.text)
    cnt = searchPageElements.xpath('//img[@id="%s"]/@cnt' % setID)
    if cnt:
        for i in range(int(cnt[0])):
            img = searchPageElements.xpath('//img[@id="%s"]/@src%d_3x' % (setID, i))
            if img:
                art.append(PAsearchSites.getSearchBaseURL(siteNum) + img[0])

    # Photo page
    req = PAutils.HTTPRequest(sceneURL.replace('/trailers/', '/preview/'))
    photoPageElements = HTML.ElementFromString(req.text)
    for image in photoPageElements.xpath('//img[@id="%s"]/@src0_3x' % setID):
        art.append(PAsearchSites.getSearchBaseURL(siteNum) + image)

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
