import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.replace(' ', '+')

    searchURL = '%s%s' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded)
    req = PAutils.HTTPRequest(searchURL)
    searchPageElements = HTML.ElementFromString(req.text)

    for searchResult in searchPageElements.xpath('//div[@class="videos-list"]/article'):
        sceneURL = searchResult.xpath('.//@href')[0]

        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//@title')[0].split("(")[0].split('–')[-1].strip(), siteNum)
        curID = PAutils.Encode(sceneURL)

        releaseDate = searchData.dateFormat() if searchData.date else ''

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [BangBros]' % (titleNoFormatting), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)
    sceneID = detailsPageElements.xpath('//article/@id')[0].split('-')[-1]

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content().split('(')[0].split('–')[-1].strip(), siteNum)

    # Summary
    summary = detailsPageElements.xpath('//div[@class="video-description"]//strong[contains(., "Description")]//following-sibling::text()')
    if summary:
        metadata.summary = summary[0].strip()

    # Studio
    metadata.studio = 'Bang Bros'

    # Tagline and Collection(s)
    tagline = detailsPageElements.xpath('//span[@class="fn"]')[0].text_content()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="video-description"]//strong[contains(., "Date")]//following-sibling::text()')
    if date:
        date_object = parse(date[0].strip())
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    genres = detailsPageElements.xpath('//*[.//@class="fa fa-tag"]/text()')
    for genreLink in genres:
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//*[.//@class="fa fa-star"]/text()'):
        actorName = actorLink.strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    actors = PAutils.getDictKeyFromValues(sceneActorsDB, sceneID)
    for actor in actors:
        actorName = actor.strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//meta[@itemprop="thumbnailUrl"]/@content',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            img = img.replace('-320x180', '')

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


sceneActorsDB = {
    'Peter Green': ['102939'],
    'Violet Gems': ['102939'],
}
