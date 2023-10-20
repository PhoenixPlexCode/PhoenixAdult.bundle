import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    words = searchData.title.lower().split(' ')
    url = PAsearchSites.getSearchBaseURL(siteNum) + '/trial/scenes/' + '-'.join(words) + '_vids.html'
    req = PAutils.HTTPRequest(url, 'HEAD')
    if req and req.ok:
        curID = PAutils.Encode(url)
        releaseDate = searchData.dateFormat() if searchData.date else ''
        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (url, PAsearchSites.getSearchSiteName(siteNum)), score=100, lang=lang))

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="grid-item"]'):
        releaseDate = titleNoFormatting = ''
        curID = PAutils.Encode(searchResult.xpath('.//a/@href')[0])

        try:
            titleNoFormatting = PAutils.parseTitle(searchResult.xpath('./a/img/@alt')[0].strip(), siteNum)
        except:
            Log("Error fetching title")

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//div[@class="movie_title"]')[0].text_content().strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="player-scene-description"]/span[contains(text(), "Description:")]/..')[0].text_content().replace('Description: ', '').strip()

    # Studio
    metadata.studio = 'Jules Jordan'

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)
    try:
        dvdName = detailsPageElements.xpath('//div[@class="player-scene-description"]//span[contains(text(), "Movie:")]/..')[0].text_content().replace('Movie:', '').replace('Feature: ', '').strip()
        metadata.tagline = dvdName
        metadata.collections.add(dvdName)
    except:
        pass

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
    else:
        try:
            date_object = parse(detailsPageElements.xpath('//div[@class="player-scene-description"]//span[contains(text(), "Date:")]/..')[0].text_content().replace('Date: ', '').strip())
        except:
            date_object = None
            Log("No date found")
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//span[contains(text(), "Categories")]/a'):
        genreName = genreLink.text_content().strip().lower()

        movieGenres.addGenre(genreName)

    # Actor(s)
    if PAsearchSites.getSearchSiteName(siteNum) == "GirlGirl":
        actors = detailsPageElements.xpath('//div[@class="item"]/span/div/a')
    else:
        actors = detailsPageElements.xpath('//div[@class="player-scene-description"]/span[contains(text(), "Starring:")]/..//a')

    if actors:
        for actorLink in actors:
            actorName = str(actorLink.text_content().strip())
            actorPhotoURL = ''

            actorPageURL = actorLink.get('href')
            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            try:
                actorPhotoURL = actorPage.xpath('//img[@class="model_bio_thumb stdimage thumbs target"]/@src0_3x')[0]
                if 'http' not in actorPhotoURL:
                    actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL
            except:
                pass

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    try:
        videoPoster = detailsPageElements.xpath('//video[@id="video-player"]/@poster')[0]
        art.append(videoPoster)
    except:
        Log("No in-page poster found")

    # Slideshow of images from the Search page
    try:
        req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + urllib.quote(metadata.title))
        searchPageElements = HTML.ElementFromString(req.text)
        for i in range(0, 7):
            try:
                posterUrl = searchPageElements.xpath('//img[contains(@id,"set-target")]/@src%d_1x' % i)[0]
                if 'http' not in posterUrl:
                    posterUrl = PAsearchSites.getSearchBaseURL(siteNum) + posterUrl

                art.append(posterUrl)
            except:
                Log("Error fetching photo from Slideshow")
    except:
        Log("Error fetching photo from Slideshow")

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        try:
            if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
                # Download image file for analysis
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
