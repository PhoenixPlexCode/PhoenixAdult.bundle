import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="item"]'):
        titleNoFormatting = searchResult.xpath('.//h4//a')[0].text_content().strip()
        curID = PAutils.Encode('https:' + searchResult.xpath('.//a/@href')[0])
        actors = searchResult.xpath('.//div[@class="item-featured"]//a')
        firstActor = actors[0].text_content().strip().title()

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s in %s [Screwbox]' % (firstActor, titleNoFormatting), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="item-details-right"]//h1')[0].text_content().strip().title()

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//p[@class="shorter"]')[0].text_content().strip()
    except:
        pass

    # Studio
    metadata.studio = 'Screwbox'

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Release Date
    date = detailsPageElements.xpath('//ul[@class="more-info"]//li[2]')[0].text_content().replace('RELEASE DATE:', '').strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//ul[@class="more-info"]//li[3]//a'):
        genreName = genreLink.text_content().title()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//ul[@class="more-info"]//li[1]//a'):
        actorName = actorLink.text_content().strip().title()

        actorPageURL = 'http:' + actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPageElements = HTML.ElementFromString(req.text)
        actorPhotoURL = actorPageElements.xpath('//img[contains(@class, "model_bio_thumb")]')[0].get("src0_1x")

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters/Background
    try:
        background = detailsPageElements.xpath('//div[@class="fakeplayer"]//img/@src0_1x')[0]
    except:
        background = detailsPageElements.xpath('//div[@class="fakeplayer"]//img/@src0_1x')[0]

    art.append(background)

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
