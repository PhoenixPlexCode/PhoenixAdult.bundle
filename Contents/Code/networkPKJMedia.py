import PAsearchSites
import PAutils

def search(results, lang, siteNum, searchData):
    searchResults = []
    searchData.encoded = searchData.title.replace(' ', '+')
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchPageElements = HTML.ElementFromString(req.text)

    for searchResult in searchPageElements.xpath('//div[contains(@class, "video-section")]/div/div'):
        titleNoFormatting = searchResult.xpath('//div[contains(@class, "post-header")]/h3/a/text()')[0]
        titleNoFormatting = PAutils.parseTitle(titleNoFormatting, siteNum)
        sceneURL = searchResult.xpath('//div[contains(@class, "post-header")]/h3/a/@href')[0]
        curID = PAutils.Encode(sceneURL)

        if sceneURL not in searchResults:
            searchResults.append(sceneURL)
            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=80, lang=lang))


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[contains(@class, "video-details")]/div/h1/text()')[0]

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "post-entry")]/p/text()')[0]

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Genres
    genres = PAutils.getDictValuesFromKey(genresDB, PAsearchSites.getSearchSiteName(siteNum))
    for genreName in genres:
        movieGenres.addGenre(genreName)

    # Actor(s)
    movieActors.clearActors()
    actorName = detailsPageElements.xpath('//div[contains(@class, "post-entry")]/div/span[2]/a/text()')[0]
    actorPhotoURL = ''

    movieActors.addActor(actorName, actorPhotoURL)

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