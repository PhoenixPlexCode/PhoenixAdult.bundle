import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.title.replace(' ', '+'))
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[contains(@class, "item-video")]'):
        titleNoFormatting = searchResult.xpath('.//a/@title')[0]
        curID = PAutils.Encode(searchResult.xpath('.//a/@href')[0])
        date = searchResult.xpath('.//div[@class="more-info-div"]')[0].text_content().split('|')
        releaseDate = parse(date[-1].strip()).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    if siteNum == 977:
        title = detailsPageElements.xpath('//*[@class="video-player"]//h3[@class="section-title"]')[0].text_content().strip()
    elif siteNum == 1564:
        title = detailsPageElements.xpath('//*[@class="video-player"]//h1[@class="section-title"]')[0].text_content().strip()
    else:
        title = detailsPageElements.xpath('//*[@class="video-player"]//h2[@class="section-title"]')[0].text_content().strip()
    metadata.title = PAutils.parseTitle(title, siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="update-info-block"]')[1].text_content().replace('Description:', '', 1).strip()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)
    if (976 <= siteNum <= 978) or siteNum == 1564:
        metadata.studio = 'ExploitedX'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="update-info-row"]')[0].text_content().replace('Released:', '', 1).strip()
    if date:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//ul[@class="tags"]//li//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[contains(@class, "models-list-thumbs")]//li'):
        actorName = actorLink.xpath('.//span/text()')[0]
        actorPhotoURL = actorLink.xpath('.//img//@src0_3x')[0]
        if not actorPhotoURL.startswith('http'):
            actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

        if siteNum == 977 and actorName == 'Twins':
            movieActors.addActor('Joey White', actorPhotoURL)
            movieActors.addActor('Sami White', actorPhotoURL)
        else:
            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@class="player-thumb"]//img/@src0_1x'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if not img.startswith('http'):
                img = PAsearchSites.getSearchBaseURL(siteNum) + img
            art.append(img)

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
