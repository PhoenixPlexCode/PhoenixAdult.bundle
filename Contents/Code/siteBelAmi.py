import PAsearchSites
import PAextras
import PAutils


def search(results, lang, siteNum, searchData):
    parts = searchData.title.split()

    Log("Search data: " + searchData.title)

    sceneID = unicode(parts[0])
    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + 'VideoID=' + sceneID
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)
    title = getTitle(detailsPageElements)
    releaseDate = getReleaseDate(detailsPageElements)
    results.Append(MetadataSearchResult(id='belamionline|%d|%s' % (siteNum, sceneID), name='%s [%s] %s' % (title, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=101, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    siteNum = int(metadata_id[1])
    sceneID = unicode(metadata_id[2])
    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + 'VideoID=' + sceneID
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = getTitle(detailsPageElements)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "video_detail")]//div[contains(@class, "bottom")]//p')[1].text_content().strip()

    # Studio
    metadata.studio = 'Bel Ami Online'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = getReleaseDate(detailsPageElements)
    if date:
        date_object = datetime.strptime(date, '%m/%d/%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    labels = detailsPageElements.xpath('//div[contains(@class, "video_detail")]//span[contains(@id, "ContentPlaceHolder1_LabelTags")]//a')
    if labels:
        for label in labels:
            movieGenres.addGenre(label.text_content())

    # Actor(s)
    # Use div class="right" because the actors are actually listed twice on the page
    actors = detailsPageElements.xpath('//div[contains(@class, "video_detail")]//div[contains(@class, "right")]//div[contains(@class, "actors_list")]//div[contains(@class, "actor")]//a')
    actorName = ''
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content()
            actorPhotoURL = actorLink.xpath('//img/@src')[0]

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    posterURL = 'https://freecdn.belamionline.com/Data/Contents/Content_%s/Thumbnail8.jpg' % (sceneID)
    art.append(posterURL)
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


def getReleaseDate(pageElements):
    return pageElements.xpath('//div[contains(@class, "video_detail")]//span[contains(@id, "ContentPlaceHolder1_LabelReleased")]')[0].text_content()


def getTitle(pageElements):
    return pageElements.xpath('//div[contains(@class, "video_detail")]//span[contains(@id, "ContentPlaceHolder1_LabelTitle")]')[0].text_content().strip()
