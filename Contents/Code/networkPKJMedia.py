import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@class="video-section"]/div/div'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('//div[@class="post-header"]/h3/a/text()')[0], siteNum)
        curID = PAutils.Encode(searchResult.xpath('//div[@class="post-header"]/h3/a/@href')[0])
        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="video-details"]/div/h1/text()')[0].strip()

    # Summary
    try:
        summary = detailsPageElements.xpath('//div[@class="post-entry"]/p/text()')
    except:
        summary = detailsPageElements.xpath('//div[@class="post-entry"]/p/span/text()')

    if summary:
        metadata.summary = summary[0].strip()

    # Studio
    metadata.studio = 'PKJ Media'

    # Tagline and Collection(s)
    metadata.tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.collections.add(metadata.tagline)

    # Genres
    genres = PAutils.getDictValuesFromKey(genresDB, PAsearchSites.getSearchSiteName(siteNum))
    for genreName in genres:
        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="post-entry"]/div/span[2]/a'):
        actorName = actorLink.text_content().strip()

        movieActors.addActor(actorName, '')

    # Posters
    art.append(detailsPageElements.xpath('//video/@poster')[0])

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


genresDB = {
    'MyPOVFam': ['Pov', 'Family'],
    'PervertedPOV': ['Pov'],
    'RawWhiteMeat': ['Interracial'],
}
