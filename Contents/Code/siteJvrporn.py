import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.lower()
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    Log("searchResults: " + str(searchResults))
    titleNoFormatting = searchResults.xpath('//title')[0].text_content().split("|")[0].strip()
    Log("titleNoFormatting: " + str(titleNoFormatting))
    Log("searchData: " + str(searchData))

    curID = searchData.encoded

    score = 100

    results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + metadata_id[0]
    Log("sceneURL: " + str(sceneURL))
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)
    Log("detailsPageElements: " + str(detailsPageElements))

    # Title
    metadata.title = detailsPageElements.xpath('//title')[0].text_content().split("|")[0].strip()
    Log("metadata.title: " + str(metadata.title))

    # Summary
    metadata.summary = detailsPageElements.xpath('//pre')[0].text_content().strip()
    Log("metadata.summary: " + str(metadata.summary))

    # Studio
    metadata.studio = 'JVR Porn'

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//td[contains(@class, "tags")]//span'):
        Log("genreLink: " + str(genreLink))
        genreName = genreLink.text_content().strip()
        Log("genreName: " + str(genreName))

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//a[@class="actress"]//span'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []

    for poster in detailsPageElements.xpath('//div[contains(@id, "snapshot-gallery")]//a'):
        img = poster.get('href')
        art.append(img)

    poster = detailsPageElements.xpath('//deo-video/@cover-image')[0]
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
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
