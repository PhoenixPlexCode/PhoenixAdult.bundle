import PAsearchSites
import PAutils


def getReleaseDateAndDisplayDate(detailsPageElements, searchData=None):
    releaseDate = ''

    try:
        date = detailsPageElements.xpath('//li[contains(., "Released:")]/text()')[0].strip()
    except:
        date = ''

    if date and not date == 'unknown':
        try:
            releaseDate = datetime.strptime(date, '%b %d %Y').strftime('%Y-%m-%d')
        except:
            releaseDate = ''
    elif searchData:
        releaseDate = searchData.dateFormat() if searchData.date else ''

    displayDate = releaseDate if date else ''

    return (releaseDate, displayDate)


def search(results, lang, siteNum, searchData):
    searchResults = []
    siteResults = []
    temp = []
    directID = False
    count = 0

    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]

        if int(sceneID) > 100:
            searchData.title = searchData.title.replace(sceneID, '', 1).strip()
            movieURL = '%s/%s' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID)
            searchResults.append(movieURL)
            directID = True

    if not directID:
        searchData.encoded = searchData.title.replace('&', '').replace('\'', '').replace(',', '').replace('#', '').replace(' ', '+')
        searchURL = '%s%s' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded)
        req = PAutils.HTTPRequest(searchURL, headers={'Referer': 'http://www.data18.empirestores.co'})
        searchPageElements = HTML.ElementFromString(req.text)

        for searchResult in searchPageElements.xpath('//small[not(contains(., "Sex Toy"))]//parent::div'):
            resultType = searchResult.xpath('.//@href')[0].rsplit('-')[-1].replace('.html', '').replace('ray', 'Blu-Ray').title()
            urlID = searchResult.xpath('.//@href')[0].split('/')[1]
            movieURL = '%s/%s' % (PAsearchSites.getSearchBaseURL(siteNum), urlID)

            if movieURL not in searchResults:
                titleNoFormatting = PAutils.parseTitle(searchResult.xpath('./a')[0].text_content().strip(), siteNum)
                curID = PAutils.Encode(movieURL)
                siteResults.append(movieURL)

                releaseDate, displayDate = getReleaseDateAndDisplayDate('', searchData)

                if sceneID == urlID:
                    score = 100
                elif searchData.date and displayDate:
                    score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
                else:
                    score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                if score > 70:
                    sceneURL = PAutils.Decode(curID)
                    req = PAutils.HTTPRequest(sceneURL)
                    detailsPageElements = HTML.ElementFromString(req.text)

                    # Find date on movie specific page
                    releaseDate, displayDate = getReleaseDateAndDisplayDate(detailsPageElements, searchData)

                    # Studio
                    try:
                        studio = detailsPageElements.xpath('//li[contains(., "Studio:")]/a/text()')[0].strip()
                    except:
                        studio = ''

                    if sceneID == urlID:
                        score = 100
                    elif searchData.date and displayDate:
                        score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
                    else:
                        score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                    if score == 80:
                        count += 1
                        temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] [%s] %s' % (titleNoFormatting, studio, resultType, displayDate), score=score, lang=lang))
                    else:
                        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] [%s] %s' % (titleNoFormatting, studio, resultType, displayDate), score=score, lang=lang))

                    # Split Scenes
                    scenes = []
                    sceneTitles = []
                    try:
                        availableScenes = detailsPageElements.xpath('//div[@class="row"][.//h3]')

                        for scene in availableScenes:
                            if scene.xpath('.//a/text()')[0] not in sceneTitles:
                                sceneTitles.append(scene.xpath('.//a/text()')[0])
                                scenes.append(scene)

                        for sceneNum, scene in enumerate(scenes, 1):
                            actorNames = ', '.join(scene.xpath('.//div/a/text()')).strip()

                            if len(availableScenes) > len(scenes):
                                photoIdx = sceneNum * 2 - 1
                            else:
                                photoIdx = sceneNum - 1

                            if not actorNames:
                                actorNames = scene.xpath('.//a/text()')[0].strip()

                            if score == 80:
                                count += 1
                                temp.append(MetadataSearchResult(id='%s|%d|%s|%d|%d' % (curID, siteNum, releaseDate, sceneNum, photoIdx), name='%s[%s]/#%d[%s][%s] %s' % (titleNoFormatting, resultType, sceneNum, actorNames, studio, displayDate), score=score, lang=lang))
                            else:
                                results.Append(MetadataSearchResult(id='%s|%d|%s|%d|%d' % (curID, siteNum, releaseDate, sceneNum, photoIdx), name='%s[%s]/#%d[%s][%s] %s' % (titleNoFormatting, resultType, sceneNum, actorNames, studio, displayDate), score=score, lang=lang))
                    except:
                        pass
                else:
                    if score == 80:
                        count += 1
                        temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, resultType, displayDate), score=score, lang=lang))
                    else:
                        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, resultType, displayDate), score=score, lang=lang))

        googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
        for movieURL in googleResults:
            cleanURL = movieURL.rsplit('/', 1)[0]
            if ('movies' in movieURL and '.html' not in movieURL and cleanURL not in searchResults and cleanURL not in siteResults):
                searchResults.append(cleanURL)

    for movieURL in searchResults:
        req = PAutils.HTTPRequest(movieURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        urlID = re.sub(r'.*/', '', movieURL)
        titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1/text()')[0].strip(), siteNum)
        curID = PAutils.Encode(movieURL)

        releaseDate, displayDate = getReleaseDateAndDisplayDate(detailsPageElements, searchData)

        if sceneID == urlID:
            score = 100
        elif searchData.date and displayDate:
            score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        # Studio
        try:
            studio = detailsPageElements.xpath('//li[contains(., "Studio:")]/a/text()')[0].strip()
        except:
            studio = ''

        if score == 80:
            count += 1
            temp.append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))
        else:
            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, studio, displayDate), score=score, lang=lang))

        # Split Scenes
        scenes = []
        sceneTitles = []
        try:
            availableScenes = detailsPageElements.xpath('//div[@class="row"][.//h3]')

            for scene in availableScenes:
                if scene.xpath('.//a/text()')[0] not in sceneTitles:
                    sceneTitles.append(scene.xpath('.//a/text()')[0])
                    scenes.append(scene)

            for sceneNum, scene in enumerate(scenes, 1):
                actorNames = ', '.join(scene.xpath('.//div/a/text()')).strip()

                if len(availableScenes) > len(scenes):
                    photoIdx = sceneNum * 2 - 1
                else:
                    photoIdx = sceneNum - 1

                if not actorNames:
                    actorNames = scene.xpath('.//a/text()')[0].strip()

                if score == 80:
                    count += 1
                    temp.append(MetadataSearchResult(id='%s|%d|%s|%d|%d' % (curID, siteNum, releaseDate, sceneNum, photoIdx), name='%s/#%d[%s][%s] %s' % (titleNoFormatting, sceneNum, actorNames, studio, displayDate), score=score, lang=lang))
                else:
                    results.Append(MetadataSearchResult(id='%s|%d|%s|%d|%d' % (curID, siteNum, releaseDate, sceneNum, photoIdx), name='%s/#%d[%s][%s] %s' % (titleNoFormatting, sceneNum, actorNames, studio, displayDate), score=score, lang=lang))
        except:
            pass

    for result in temp:
        if count > 1 and result.score == 80:
            results.Append(MetadataSearchResult(id=result.id, name=result.name, score=79, lang=lang))
        else:
            results.Append(MetadataSearchResult(id=result.id, name=result.name, score=result.score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    splitScene = False
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    if len(metadata_id) > 3:
        sceneNum = int(metadata_id[3])
        sceneIndex = int(metadata_id[4])
        Log('Split Scene: %d' % sceneNum)
        splitScene = True

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1/text()')[0].strip(), siteNum)
    if splitScene:
        metadata.title = '%s [Scene %d]' % (metadata.title, sceneNum)

    # Summary
    try:
        if '\n' in detailsPageElements.xpath('//div[@class="container"][.//h2]//parent::p')[0].text_content():
            summary = '\n'.join([line.text_content().strip() for line in detailsPageElements.xpath('//div[@class="container"][.//h2]//parent::p')])
        else:
            summary = detailsPageElements.xpath('//div[@class="container"][.//h2]//parent::p')[0].text_content().strip()
    except:
        summary = ''
    metadata.summary = summary

    # Director(s)
    directorElement = detailsPageElements.xpath('//div[./a[@name="cast"]]//li[./*[contains(., "Director")]]/a/text()')
    for directorName in directorElement:
        director = metadata.directors.new()
        name = directorName.strip()
        director.name = name

    # Producer(s)
    producerElement = detailsPageElements.xpath('//div[./a[@name="cast"]]//li[./*[contains(., "Producer")]]/text()')
    for producerName in producerElement:
        producer = metadata.producers.new()
        name = producerName.strip()
        producer.name = name

    # Studio
    try:
        studio = detailsPageElements.xpath('//li[contains(., "Studio:")]/a/text()')[0].strip()
    except:
        studio = ''

    metadata.studio = studio

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add(studio)
    try:
        tagline = re.sub(r'\(.*\)', '', detailsPageElements.xpath('//h2/a[@label="Series"]/text()')[0].strip().split('"')[1]).strip()
        tagline = PAutils.parseTitle(tagline, siteNum)

        metadata.tagline = tagline
        metadata.collections.add(tagline)
    except:
        if splitScene:
            metadata.collections.add(PAutils.parseTitle(detailsPageElements.xpath('//h1/text()')[0], siteNum).strip())

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    else:
        releaseDate, displayDate = getReleaseDateAndDisplayDate(detailsPageElements)
        if releaseDate:
            date_object = datetime.strptime(releaseDate, '%Y-%m-%d')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//li//a[@label="Category"]'):
        genreName = genreLink.text_content().strip()
        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = []
    if splitScene:
        scenes = detailsPageElements.xpath('//div[@class="row"][.//h3]')[sceneIndex]
        actors = scenes.xpath('.//div/a')

        # Fallback
        if not actors:
            actors = detailsPageElements.xpath('//div[contains(., "Starring")][1]/a')
    else:
        actors = detailsPageElements.xpath('//div[contains(., "Starring")][1]/a')

    for actorLink in actors:
        actorName = actorLink.text_content().split('(')[0].strip()
        try:
            actorPhotoURL = detailsPageElements.xpath('//div[contains(., "Starring")]//img[contains(@title, "%s")]/@src' % actorName)[0]
        except:
            actorPhotoURL = ''

        if actorName:
            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@class="boxcover-container"]/a/img/@src',
        '//div[@class="boxcover-container"]/a/@href'
    ]

    try:
        for xpath in xpaths:
            art.append(detailsPageElements.xpath(xpath)[0])
    except:
        pass

    try:
        if splitScene:
            splitScenes = '//div[@class="row"][.//div[@class="row"]][.//a[@rel="scenescreenshots"]][%d]//a/@href' % (sceneIndex + 1)
            art.extend(detailsPageElements.xpath(splitScenes))
        else:
            scenes = '//div[@class="row"][.//div[@class="row"]][.//a[@rel="scenescreenshots"]]//div[@class="row"]//a/@href'
            art.extend(detailsPageElements.xpath(scenes))
    except:
        pass

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.data18.empirestores.co'})
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
