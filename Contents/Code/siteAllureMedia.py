import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    # Amateur Allure
    if siteNum == 564:
        for searchResult in searchResults.xpath('//div[@class="update_details"]'):
            titleNoFormatting = searchResult.xpath('.//div[@class="update_title"]/a')[0].text_content().strip()
            releaseDate = parse(searchResult.xpath('.//div[@class="update_date"]')[0].text_content().replace('Added:', '').strip()).strftime('%Y-%m-%d')
            curID = PAutils.Encode(searchResult.xpath('.//a[1]/@href')[0])

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            if len(titleNoFormatting) > 29:
                titleNoFormatting = titleNoFormatting[:32] + '...'

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    # Swallow Salon
    if siteNum == 565:
        for searchResult in searchResults.xpath('//div[@class="update_details"]'):
            titleNoFormatting = searchResult.xpath('./a[2]')[0].text_content().strip()
            releaseDate = parse(searchResult.xpath('.//div[@class="cell update_date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
            curID = PAutils.Encode(searchResult.xpath('./a[2]/@href')[0])

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            if len(titleNoFormatting) > 29:
                titleNoFormatting = titleNoFormatting[:32] + '...'

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//title')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//span[@class="update_description"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Allure Media'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[contains(@class, "update_date")]')[0].text_content().strip()
    if not date:
        try:
            date = str(detailsPageElements.xpath('.//div[@class="cell update_date"]/comment()')[0]).strip()
            date = date[date.find('OFF') + 4:date.find('D', date.find('OFF') + 4)].strip()
        except:
            pass

    if date:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//span[@class="update_tags"]//a'):
        genreName = genreLink.text_content().strip('\n').lower()

        movieGenres.addGenre(genreName)
    movieGenres.addGenre('Amateur')

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="backgroundcolor_info"]//span[@class="update_models"]/a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        actorPageURL = actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        img = actorPage.xpath('//div[@class="cell_top cell_thumb"]/img/@src')
        if img:
            actorPhotoURL = img[0]
            if not actorPhotoURL.startswith('http'):
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

        movieActors.addActor(actorName, actorPhotoURL)

    # Manually Add Actors
    actors = [
        'Adriana Chechik',
        'Alexa Grace',
        'Alice Green',
        'Alina Li',
        'Amanda Aimes',
        'Ava Taylor',
        'Belle Knox',
        'Belle Noire',
        'Cadence Lux',
        'Claire Heart',
        'Devon Green',
        'Emily Grey',
        'Emma Hix',
        'Evangeline',
        'Faith',
        'Hadley',
        'Holly Michaels',
        'Jane Wilde'
        'Kennedy Leigh',
        'Kenzie Reeves',
        'Kimber Woods',
        'Layla London',
        'Lexi Mansfield',
        'Lilly Banks',
        'Linda Lay',
        'Lucy Tyler',
        'Melissa Moore',
        'Nadine Sage',
        'Naomi Woods',
        'Remy LaCroix',
        'Samantha Sin',
        'Stella May',
        'Talia Tyler',
        'Taylor Renae',
        'Veronica Rodriguez',
        'Zoe Voss',
    ]
    for actorName in actors:
        if actorName in metadata.title or actorName in metadata.summary:
            movieActors.addActor(actorName, '')

    # Posters
    try:
        bigScript = detailsPageElements.xpath('//script[contains(text(), "df_movie")]')[0].text_content()
        alpha = bigScript.find('useimage = "') + 12
        omega = bigScript.find('";', alpha)
        background = bigScript[alpha:omega]
        if 'http' not in background:
            background = PAsearchSites.getSearchBaseURL(siteNum) + background
        art.append(background)
    except:
        pass

    # Slideshow of images from the Search page
    try:
        bigScript = detailsPageElements.xpath('//script[contains(text(), "df_movie")]')[0].text_content()
        alpha = bigScript.find('setid:"') + 7
        omega = bigScript.find('",', alpha)
        setID = bigScript[alpha:omega]
        req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + urllib.quote(metadata.title))
        searchPageElements = HTML.ElementFromString(req.text)
        posterUrl = searchPageElements.xpath('//img[@id="set-target-%s"]/@src' % setID)[0]
        if 'http' not in posterUrl:
            posterUrl = PAsearchSites.getSearchBaseURL(siteNum) + posterUrl
        art.append(posterUrl)

        for i in range(0, 7):
            try:
                posterUrl = searchPageElements.xpath('//img[@id="set-target-%s"]/@src%d_1x' % (setID, i))[0]
                if 'http' not in posterUrl:
                    posterUrl = PAsearchSites.getSearchBaseURL(siteNum) + posterUrl
                art.append(posterUrl)
            except:
                pass
    except:
        pass

    # Photos page
    photoPageURL = None
    photoPageURL = detailsPageElements.xpath('//div[@class="cell content_tab"]/a[text()="Photos"]/@href')[0]
    req = PAutils.HTTPRequest(photoPageURL)
    photoPageElements = HTML.ElementFromString(req.text)
    bigScript = photoPageElements.xpath('//script[contains(text(), "var ptx")]')[0].text_content()
    try:
        ptx1600starts = bigScript.find('1600')
        ptx1600ends = bigScript.find('togglestatus', ptx1600starts)
        ptx1600 = bigScript[ptx1600starts:ptx1600ends]
        photos = []
        imageCount = ptx1600.count('ptx["1600"][')
        for i in range(1, imageCount + 1):
            alpha = ptx1600.find('{src: "', omega) + 7
            omega = ptx1600.find('"', alpha)
            posterUrl = ptx1600[alpha:omega]
            if 'http' not in posterUrl:
                posterUrl = PAsearchSites.getSearchBaseURL(siteNum) + posterUrl
            if i == 5:
                actorPhotoURL = posterUrl
            photos.append(posterUrl)
        for x in range(10):
            art.append(photos[random.randint(1, imageCount)])
    except:
        pass

    # Vidcaps page
    try:
        ptxjpgstarts = bigScript.find('ptx["jpg"] = {};')
        ptxjpgends = bigScript.find('togglestatus', ptxjpgstarts)
        ptxjpg = bigScript[ptxjpgstarts:ptxjpgends]
        vidcaps = []
        imageCount = ptxjpg.count('ptx["jpg"][')
        for i in range(1, imageCount + 1):
            alpha = ptxjpg.find('{src: "', omega) + 7
            omega = ptxjpg.find('"', alpha)
            posterUrl = ptxjpg[alpha:omega]
            if 'http' not in posterUrl:
                posterUrl = PAsearchSites.getSearchBaseURL(siteNum) + posterUrl
            if i == 5:
                actorPhotoURL = posterUrl
            vidcaps.append(posterUrl)
        for x in range(10):
            art.append(vidcaps[random.randint(1, imageCount)])
    except:
        pass

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                referer = photoPageURL if photoPageURL else sceneURL
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': referer})
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
