import PAsearchSites
import PAgenres
import PAactors
import PAextras
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):
    searchResults = []

    sceneID = None
    splited = searchTitle.split(' ')
    if unicode(splited[0], 'UTF-8').isdigit():
        sceneID = splited[0]
        searchTitle = searchTitle.replace(sceneID, '', 1).strip()
        sceneURL = '%s/content/%s' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID)
        searchResults.append(sceneURL)

    encodedTitle = searchTitle.replace(' ', '+')
    searchURL = '%s%s' % (PAsearchSites.getSearchSearchURL(siteNum), encodedTitle)
    req = PAutils.HTTPRequest(searchURL, headers={'Referer': 'http://www.data18.com'})
    searchPageElements = HTML.ElementFromString(req.text)

    for searchResult in searchPageElements.xpath('//div[@class="bscene genmed"]'):
        sceneURL = searchResult.xpath('.//*[contains(@href, "content")]/@href')[0]

        if sceneURL not in searchResults:
            try:
                siteName = searchResult.xpath('.//*[contains(., "Network")]')[0].text_content().replace('Network:', '').strip()
            except:
                try:
                    siteName = searchResult.xpath('.//*[contains(., "Studio")]')[0].text_content().replace('Studio:', '').strip()
                except:
                    siteName = ''

            try:
                subSite = searchResult.xpath('.//p[@class][contains(., "Site:")]')[0].text_content().replace('Site:', '').strip()
            except:
                subSite = ''

            if siteName:
                siteDisplay = '%s/%s' % (siteName, subSite) if subSite else siteName
            else:
                siteDisplay = subSite

            titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//*[contains(@href, "content")]')[1].text_content(), siteNum)

            searchResults.append(sceneURL)
            curID = PAutils.Encode(sceneURL)

            try:
                date = searchResult.xpath('.//p[@class="genmed"]')[0].text_content().strip()
                date = re.sub(r'^#(.*?)\s', '', date)
            except:
                date = ''

            if date and not date == 'unknown':
                date = date.replace('Sept', 'Sep')
                releaseDate = parse(date).strftime('%Y-%m-%d')
            else:
                releaseDate = parse(searchDate).strftime('%Y-%m-%d') if searchDate else ''
            displayDate = releaseDate if date else ''

            if searchDate and displayDate:
                score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, siteDisplay, displayDate), score=score, lang=lang))

    googleResults = PAutils.getFromGoogleSearch(searchTitle, siteNum)
    for sceneURL in googleResults:
        if ('/content/' in sceneURL and '.html' not in sceneURL and sceneURL not in searchResults):
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        try:
            siteName = detailsPageElements.xpath('//i[contains(., "Network")]//preceding-sibling::a[1]')[0].text_content().strip()
        except:
            try:
                siteName = detailsPageElements.xpath('//i[contains(., "Studio")]//preceding-sibling::a[1]')[0].text_content().strip()
            except:
                siteName = ''

        try:
            subSite = detailsPageElements.xpath('//i[contains(., "Site")]//preceding-sibling::a[1]')[0].text_content().strip()
        except:
            subSite = ''

        if siteName:
            siteDisplay = '%s/%s' % (siteName, subSite) if subSite else siteName
        else:
            siteDisplay = subSite

        titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)
        curID = PAutils.Encode(sceneURL)

        try:
            date = detailsPageElements.xpath('//span[@class][./*[contains(.., "date")]]')[0].text_content().split(':', 2)[-1].strip()
        except:
            date = ''

        if date and not date == 'unknown':
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = parse(searchDate).strftime('%Y-%m-%d') if searchDate else ''
        displayDate = releaseDate if date else ''

        if searchDate and displayDate:
            score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, siteDisplay, displayDate), score=score, lang=lang))

    return results


def update(metadata, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[@class="gen12"]/p[contains(., "Story")]')[0].text_content().split('\n', 2)[-1]
    except:
        pass

    # Studio
    try:
        metadata.studio = detailsPageElements.xpath('//i[contains(., "Network")]//preceding-sibling::a[1]')[0].text_content().strip()
    except:
        try:
            metadata.studio = detailsPageElements.xpath('//i[contains(., "Studio")]//preceding-sibling::a[1]')[0].text_content().strip()
        except:
            pass

    # Tagline and Collection(s)
    metadata.collections.clear()
    try:
        tagline = detailsPageElements.xpath('//i[contains(., "Site")]//preceding-sibling::a[1]')[0].text_content().strip()
        if not metadata.studio:
            metadata.studio = tagline
        else:
            metadata.tagline = tagline
        metadata.collections.add(tagline)
    except:
        metadata.collections.add(metadata.studio)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[./b[contains(., "Categories")]]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//li')
    if actors:
        for actorLink in actors:
            actorName = actorLink.xpath('.//a[@class="bold"]')[0].text_content().strip()
            actorPhotoURL = ''

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []
    xpaths = [
        '//img/@src',
    ]

    try:
        req = PAutils.HTTPRequest(detailsPageElements.xpath('//@href[contains(., "viewer")]')[0])
        photoPageElements = HTML.ElementFromString(req.text)
        for xpath in xpaths:
            for img in photoPageElements.xpath(xpath):
                art.append(img.replace('/th8', ''))
    except:
        img = detailsPageElements.xpath('//div[@id="moviewrap"]//@src')
        art.append(img)

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.data18.com'})
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
