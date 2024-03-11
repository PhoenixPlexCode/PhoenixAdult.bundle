import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@align="left"]'):
        link = searchResult.xpath('.//a[@class="update_title"]')[1]
        titleNoFormatting = link.text_content().strip()

        date = searchResult.xpath('.//span[@class="date"]')[0].text_content().strip()[6:]
        releaseDate = parse(date).strftime('%Y-%m-%d')

        curID = PAutils.Encode(link.xpath('./@href')[0])

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [Desperate Amateurs] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + '/fintour/' + sceneURL

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="title_bar"]')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="gallery_description"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Desperate Amateurs'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date_object = parse(detailsPageElements.xpath('.//td[@class="date"]')[0].text_content().strip()[6:])
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//a[starts-with(@href, "sets")]'):
        actorName = actorLink.text_content().strip()

        actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + '/fintour/' + actorLink.xpath('./@href')[0].strip()
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPage.xpath('//img[@class="thumbs"]/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    for genreLink in detailsPageElements.xpath('//a[starts-with(@href, "category")]'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Posters
    xpaths = [
        '//div[contains(@class, "gal")]//img/@src',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(img)

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': sceneURL})
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
