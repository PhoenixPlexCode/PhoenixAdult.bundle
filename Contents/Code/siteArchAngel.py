import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[contains(@class, "item-video")]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('./div[@class="item-thumb"]/a/@title')[0], siteNum)
        curID = PAutils.Encode(searchResult.xpath('./div[@class="item-thumb"]/a/@href')[0])

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [ArchAngel]' % titleNoFormatting, score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h2')[0].text_content().strip(), siteNum)

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[@class="description"]/p')[0].text_content().strip()
    except:
        pass

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Genres
    for genreLink in detailsPageElements.xpath('//ul[@class="tags"]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="info"]/p/text()')[0].replace('Added:', '').strip()
    if date:
        date_object = datetime.strptime(date, '%B %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="info"]/p/a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//img[contains(@class, "update_thumb")]/@src0_3x',
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            if 'http' not in poster:
                poster = PAsearchSites.getSearchBaseURL(siteNum) + poster

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
