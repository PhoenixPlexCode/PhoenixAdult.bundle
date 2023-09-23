import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = searchData.title.split(' ', 1)[0]
    try:
        sceneTitle = searchData.encoded.split(' ', 1)[1]
    except:
        sceneTitle = ''

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + sceneID)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="video-details"]'):
        titleNoFormatting = searchResult.xpath('//h2[@class="h2 m-0"]')[0].text_content()
        curID = searchData.title.lower().replace(' ', '-')
        subSite = searchResult.xpath('//a[@class="username "]')[0].text_content().strip()
        releaseDate = searchData.dateFormat() if searchData.date else ''

        if sceneTitle:
            score = 100 - Util.LevenshteinDistance(sceneTitle.lower(), titleNoFormatting.lower())
        else:
            score = 90

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [ManyVids/%s]' % (titleNoFormatting, subSite), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneDate = metadata_id[2]
    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + metadata_id[0]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)
    videoURL = 'https://video-player-bff.estore.kiwi.manyvids.com/videos/%s' % metadata_id[0].split('-')[0]
    videoPageElements = PAutils.HTTPRequest(videoURL).json()

    # Title
    metadata.title = PAutils.parseTitle(videoPageElements['title'].strip(), siteNum)

    # Summary
    try:
        paragraphs = videoPageElements['description']
        summary = paragraphs[0].text_content().strip()
        if len(paragraphs) > 1:
            for paragraph in paragraphs:
                if summary == '':
                    summary = paragraph.text_content()
                else:
                    summary = summary + '\n\n' + paragraph.text_content()
        if not re.search(r'.$(?<=(!|\.|\?))', summary.strip()):
            summary = summary.strip() + '.'
    except:
        summary = ''

    metadata.summary = summary.strip()

    # Studio
    metadata.studio = 'ManyVids'

    # Tagline and Collection(s)
    tagline = detailsPageElements.xpath('//a[contains(@class, "username ")]')[0].text_content().strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in videoPageElements['tags']:
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    movieActors.clearActors()
    actorName = detailsPageElements.xpath('//a[contains(@class, "username ")]')[0].text_content()
    actorPhotoURL = ''

    try:
        actorPhotoURL = detailsPageElements.xpath('//div[@class="pr-2"]/a/img')[0].get('src')
    except:
        pass

    movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@id="rmpPlayer"]/@data-video-screenshot'
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
