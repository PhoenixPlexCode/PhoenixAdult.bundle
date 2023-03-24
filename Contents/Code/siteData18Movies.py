import PAsearchSites
import PAutils
import siteData18Scenes


def search(results, lang, siteNum, searchData):
    searchResults = []
    siteResults = []
    temp = []
    count = 0

    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]

        if int(sceneID) > 100:
            searchData.title = searchData.title.replace(sceneID, '', 1).strip()
            movieURL = '%s/movies/%s' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID)
            searchResults.append(movieURL)

    searchData.encoded = searchData.title.replace('\'', '').replace(',', '').replace('& ', '').replace('#', '')
    searchURL = '%s%s&key2=%s' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded, searchData.encoded)
    req = PAutils.HTTPRequest(searchURL, headers={'Referer': 'https://www.data18.com'}, cookies={'data_user_captcha': '1'})
    searchPageElements = HTML.ElementFromString(req.text)

    searchPages = re.search(r'(?<=pages:\s).*(?=])', req.text)
    if searchPages:
        numSearchPages = int(searchPages.group(0))
        if numSearchPages > 10:
            numSearchPages = 10
    else:
        numSearchPages = 1

    for idx in range(0, numSearchPages):
        for searchResult in searchPageElements.xpath('//a'):
            movieURL = searchResult.xpath('./@href')[0].split('-')[0]

            if ('/movies/' in movieURL and movieURL not in searchResults):
                urlID = re.sub(r'.*/', '', movieURL)

                try:
                    studio = searchResult.xpath('.//i')[0].text_content().strip()
                except:
                    studio = ''

                titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//p[@class="gen12 bold"]')[0].text_content(), siteNum)
                curID = PAutils.Encode(movieURL)

                if '...' in titleNoFormatting:
                    searchResults.append(movieURL)
                else:
                    siteResults.append(movieURL)

                    try:
                        date = searchResult.xpath('.//span[@class="gen11"]/text()')[0].strip()
                    except:
                        date = ''

                    if date and not date == 'unknown':
                        releaseDate = datetime.strptime(date, "%B, %Y").strftime('%Y-%m-%d')
                    else:
                        releaseDate = searchData.dateFormat() if searchData.date else ''
                    displayDate = releaseDate if date else ''

                    if sceneID == urlID:
                        score = 100
                    elif searchData.date and displayDate:
                        score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
                    else:
                        score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                    if score > 70:
                        sceneURL = PAutils.Decode(curID)
                        req = PAutils.HTTPRequest(sceneURL, cookies={'data_user_captcha': '1'})
                        detailsPageElements = HTML.ElementFromString(req.text)

                        # Studio
                        try:
                            studio = detailsPageElements.xpath('//b[contains(., "Network")]//following-sibling::b')[0].text_content().strip()
                        except:
                            try:
                                studio = detailsPageElements.xpath('//b[contains(., "Studio")]//following-sibling::b')[0].text_content().strip()
                            except:
                                try:
                                    studio = detailsPageElements.xpath('//p[contains(., "Site:")]//following-sibling::a[@class="bold"]')[0].text_content().strip()
                                except:
                                    studio = ''

                        if score == 80:
                            count += 1
                            temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))
                        else:
                            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))

                        # Split Scenes
                        sceneCount = detailsPageElements.xpath('//div[@id="relatedscenes"]//span')[0].text_content().split(' ')[0].strip()
                        if sceneCount.isdigit():
                            sceneCount = int(sceneCount)
                        else:
                            sceneCount = 0

                        for sceneNum in range(1, sceneCount + 1):
                            section = "Scene " + str(sceneNum)
                            scene = PAutils.Encode(detailsPageElements.xpath('//a[contains(., "%s")]/@href' % (section))[0])

                            if score == 80:
                                count += 1
                                temp.append(MetadataSearchResult(id='%s|%d|%s|%s|%d' % (scene, siteNum, releaseDate, titleNoFormatting, sceneNum), name='%s [%s][%s] %s' % (titleNoFormatting, section, studio, displayDate), score=score, lang=lang))
                            else:
                                results.Append(MetadataSearchResult(id='%s|%d|%s|%s|%d' % (scene, siteNum, releaseDate, titleNoFormatting, sceneNum), name='%s [%s][%s] %s' % (titleNoFormatting, section, studio, displayDate), score=score, lang=lang))
                    else:
                        if score == 80:
                            count += 1
                            temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))
                        else:
                            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))

        if numSearchPages > 1 and not idx + 1 == numSearchPages:
            searchURL = '%s%s&key2=%s&next=1&page=%d' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded, searchData.encoded, idx + 1)
            req = PAutils.HTTPRequest(searchURL, headers={'Referer': 'https://www.data18.com'}, cookies={'data_user_captcha': '1'})
            searchPageElements = HTML.ElementFromString(req.text)

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for movieURL in googleResults:
        movieURL = movieURL.split('-')[0].replace('http:', 'https:')
        if ('/movies/' in movieURL and '.html' not in movieURL and movieURL not in searchResults and movieURL not in siteResults):
            searchResults.append(movieURL)

    for movieURL in searchResults:
        req = PAutils.HTTPRequest(movieURL, cookies={'data_user_captcha': '1'})
        detailsPageElements = HTML.ElementFromString(req.text)
        urlID = re.sub(r'.*/', '', movieURL)

        if not detailsPageElements:
            Log('Possible IP BAN: Retry on VPN')
            break

        # Studio
        try:
            studio = detailsPageElements.xpath('//b[contains(., "Studio") or contains(., "Network")]//following-sibling::a')[0].text_content().strip()
        except:
            try:
                studio = detailsPageElements.xpath('//b[contains(., "Studio") or contains(., "Network")]//following-sibling::b')[0].text_content().strip()
            except:
                try:
                    studio = detailsPageElements.xpath('//p[contains(., "Site:")]//following-sibling::a[@class="bold"]')[0].text_content().strip()
                except:
                    studio = ''

        titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)
        curID = PAutils.Encode(movieURL)

        try:
            date = detailsPageElements.xpath('//@datetime')[0].strip()
        except:
            date = ''

        if date and not date == 'unknown':
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        displayDate = releaseDate if date else ''

        if sceneID == urlID:
            score = 100
        elif searchData.date and displayDate:
            score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        if score == 80:
            count += 1
            temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))
        else:
            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))

        # Split Scenes
        sceneCount = detailsPageElements.xpath('//div[@id="relatedscenes"]//span')[0].text_content().split(' ')[0].strip()

        if sceneCount.isdigit():
            sceneCount = int(sceneCount)
        else:
            sceneCount = 0

        for sceneNum in range(1, sceneCount + 1):
            section = "Scene " + str(sceneNum)
            scene = PAutils.Encode(detailsPageElements.xpath('//a[contains(., "%s")]/@href' % (section))[0])

            if score == 80:
                count += 1
                temp.append(MetadataSearchResult(id='%s|%d|%s|%s|%d' % (scene, siteNum, releaseDate, titleNoFormatting, sceneNum), name='%s [%s][%s] %s' % (titleNoFormatting, section, studio, displayDate), score=score, lang=lang))
            else:
                results.Append(MetadataSearchResult(id='%s|%d|%s|%s|%d' % (scene, siteNum, releaseDate, titleNoFormatting, sceneNum), name='%s [%s][%s] %s' % (titleNoFormatting, section, studio, displayDate), score=score, lang=lang))

    for result in temp:
        if count > 1 and result.score == 80:
            results.Append(MetadataSearchResult(id=result.id, name=result.name, score=79, lang=lang))
        else:
            results.Append(MetadataSearchResult(id=result.id, name=result.name, score=result.score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL, cookies={'data_user_captcha': '1'})
    detailsPageElements = HTML.ElementFromString(req.text)

    if not detailsPageElements:
        Log('Possible IP BAN: Retry on VPN')
        return metadata

    if len(metadata_id) > 3:
        Log('Switching to Data18Scenes')
        siteData18Scenes.update(metadata, lang, siteNum, movieGenres, movieActors, art)
        return metadata

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content(), siteNum)

    # Summary
    summary = detailsPageElements.xpath('//div[@class="gen12"]//div[contains(., "Description")]')[1].text_content().split('---')[-1].split('Description -')[-1].strip()
    if len(summary) > 1:
        metadata.summary = summary

    # Studio
    try:
        studio = detailsPageElements.xpath('//b[contains(., "Network")]//following-sibling::b')[0].text_content().strip()
    except:
        try:
            studio = detailsPageElements.xpath('//b[contains(., "Studio")]//following-sibling::b')[0].text_content().strip()
        except:
            try:
                studio = detailsPageElements.xpath('//p[contains(., "Site:")]//following-sibling::a[@class="bold"]')[0].text_content().strip()
            except:
                studio = ''

    if studio:
        metadata.studio = studio

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)
    try:
        tagline = detailsPageElements.xpath('//p[contains(., "Movie Series")]//a[@title]')[0].text_content().strip()
        metadata.collections.add(tagline)
    except:
        tagline = ''
    metadata.tagline = tagline

    # Release Date
    try:
        date_object = parse(detailsPageElements.xpath('//@datetime')[0].strip())
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    except:
        if sceneDate:
            date_object = parse(sceneDate)
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year
        else:
            pass

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//p[./b[contains(., "Categories")]]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//b[contains(., "Cast")]//following::div//a[contains(@href, "/pornstars/")]//img')
    actors.extend(detailsPageElements.xpath('//b[contains(., "Cast")]//following::div//img[contains(@data-original, "user")]'))
    actors.extend(detailsPageElements.xpath('//h3[contains(., "Cast")]//following::div[@style]//img'))
    for actorLink in actors:
        actorName = actorLink.xpath('./@alt')[0].strip()
        try:
            actorPhotoURL = actorLink.xpath('./@data-src')[0].strip()
        except:
            break

        actorPhotoURL = ''
        movieActors.addActor(actorName, actorPhotoURL)

    # Director
    metadata.directors.clear()
    director = metadata.directors.new()
    try:
        directorName = detailsPageElements.xpath('//p[./b[contains(., "Director")]]')[0].text_content().split(':')[-1].split('-')[0].strip()
        if not directorName == 'Unknown':
            director.name = directorName
    except:
        pass

    # Posters
    photos = []
    xpaths = [
        '//a[@id="enlargecover"]//@href',
        '//img[@id="backcoverzone"]//@src',
        '//img[@id="imgposter"]//@src',
        '//img[contains(@src, "th8")]/@src',
        '//img[contains(@data-original, "th8")]/@data-original',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(img)

    try:
        galleries = detailsPageElements.xpath('//div[@id="galleriesoff"]//div')
        movieID = re.sub(r'.*/', '', sceneURL)

        for gallery in galleries:
            galleryID = gallery.xpath('./@id')[0].replace('gallery', '')
            photoViewerURL = ("%s/sys/media_photos.php?movie=%s&pic=%s" % (PAsearchSites.getSearchBaseURL(siteNum), movieID[1:], galleryID))
            req = PAutils.HTTPRequest(photoViewerURL)
            photoPageElements = HTML.ElementFromString(req.text)

            for xpath in xpaths:
                for img in photoPageElements.xpath(xpath):
                    photos.append(img.replace('/th8', '').replace('-th8', ''))

        for x in range(10):
            art.append(photos[random.randint(1, len(photos))])
    except:
        pass

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                try:
                    image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://i.dt18.com'})
                except:
                    image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'https://www.data18.com'})
                images.append(image)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    posterExists = True
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    if not posterExists:
        for idx, image in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[art[idx - 1]] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
