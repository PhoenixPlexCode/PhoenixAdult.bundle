import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    url = '%s/%s.html' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.title.replace(' ', ''))
    req = PAutils.HTTPRequest(url)

    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[contains(@class, "item-video")]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('./div[@class="item-thumb"]//a/@title')[0], siteNum)
        curID = PAutils.Encode(searchResult.xpath('./div[@class="item-thumb"]//a/@href')[0])
        actorURL = PAutils.Encode(url)

        releaseDate = searchData.dateFormat() if searchData.date else ''

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s|%s' % (curID, siteNum, releaseDate, actorURL), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    actorURL = PAutils.Decode(metadata_id[3])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h3')[0].text_content().strip(), siteNum)

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[@class="videoDetails clear"]/p')[0].text_content().strip()
    except:
        pass

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Genres
    for genreLink in detailsPageElements.xpath('//ul[./li[contains(., "Tags:")]]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    req = PAutils.HTTPRequest(actorURL)
    actorPageElements = HTML.ElementFromString(req.text)
    actorName = actorPageElements.xpath('//h3')[0].text_content().strip()
    actorPhotoURL = actorPageElements.xpath('//div[@class="profile-pic"]/img/@src0_3x')[0]
    if not actorPhotoURL.startswith('http'):
        actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL
    movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//meta[contains(@name, "twitter:image")]/@content'
    ]

    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            if 'http' not in poster:
                poster = PAsearchSites.getSearchBaseURL(siteNum) + poster

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
