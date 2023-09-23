import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@id="left-area"]/article'):
        titleNoFormatting = searchResult.xpath('.//h2[@class="entry-title"]/a')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('.//h2[@class="entry-title"]/a/@href')[0])
        releaseDate = parse(searchResult.xpath('.//span[@class="published"]')[0].text_content().strip()).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [LittleCaprice] %s ' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    galleryPageElements = HTML.ElementFromString(req.text)
    detailsPageElements = galleryPageElements

    # Try to get the video page instead of gallery page (video page contains more useful info than gallery page)
    videoPageElements = None
    try:
        req2 = PAutils.HTTPRequest(galleryPageElements.xpath('//a[@class="et_pb_button button"]/@href')[1])
        videoPageElements = HTML.ElementFromString(req2.text)
        detailsPageElements = videoPageElements
    except:
        pass

    # Studio
    metadata.studio = 'LittleCaprice'

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="desc-text"]')[0].text_content().strip()

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="project-tags"]/div[@class="list"]/a') + galleryPageElements.xpath('//div[@class="project-tags"]/div[@class="list"]/a'):
        genreName = genreLink.text_content().lower()

        movieGenres.addGenre(genreName)

    # Tagline and Collection(s)
    attributes = detailsPageElements.xpath('//div[@id="main-project-content"]/@class')[0].strip().split()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    if 'category_buttmuse' in attributes:
        tagline = 'Buttmuse'
    elif 'category_caprice-divas' in attributes:
        tagline = 'Caprice Divas'
    elif 'category_nasstyx' in attributes:
        tagline = 'NasstyX'
    elif 'category_povdreams' in attributes:
        tagline = 'POVDreams'
    elif 'category_streetfuck' in attributes:
        tagline = 'Streetfuck'
    elif 'category_superprivatex' in attributes:
        tagline = 'SuperprivateX'
    elif 'category_wecumtoyou' in attributes:
        tagline = 'Wecumtoyou'
    elif 'category_xpervo' in attributes:
        tagline = 'Xpervo'
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Title
    title = detailsPageElements.xpath('//div[@class="project-details"]//h1')[0].text_content().strip()
    # Remove site/series name prefix from title
    if title.lower().startswith(tagline.lower()):
        title = title[len(tagline):]
    metadata.title = title

    # Release Date
    date = detailsPageElements.xpath('//div[@class="relese-date"]')[0].text_content().strip().split('Release:')[1]
    if date:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actor(s)
    actors = detailsPageElements.xpath('//div[@class="project-models"]//a')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            if actorName == 'LittleCaprice':
                actorName = 'Little Caprice'

            actorPhotoURL = ''
            try:
                actorPageURL = actorLink.get('href')
                req = PAutils.HTTPRequest(actorPageURL)
                actorPage = HTML.ElementFromString(req.text)

                actorPhotoURL = actorPage.xpath('//img[@class="img-poster"]/@src')[0]
                if 'http' not in actorPhotoURL:
                    actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL
            except:
                pass

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    try:
        detailsPageOGImage = detailsPageElements.xpath('//meta[@property="og:image"]/@content')[0]
        art.append(detailsPageOGImage)
    except:
        pass

    try:
        galleryPageOGImage = galleryPageElements.xpath('//meta[@property="og:image"]/@content')[0]
        art.append(galleryPageOGImage)
    except:
        pass

    for galleryPhoto in galleryPageElements.xpath('//div[@class="gallery spotlight-group"]/img/@src'):
        try:
            if not galleryPhoto.startswith('http'):
                galleryPhoto = PAsearchSites.getSearchBaseURL(siteNum) + galleryPhoto

            art.append(galleryPhoto)
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
