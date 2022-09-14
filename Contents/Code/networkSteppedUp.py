import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.split('and')[0].strip().replace(' ', '-').lower()

    modelPageURL = '%s/models/%s.json' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded)
    searchResults = PAutils.HTTPRequest(modelPageURL).json()

    for searchResult in searchResults['pageProps']['model_contents']:
        titleNoFormatting = PAutils.parseTitle(searchResult['title'], siteNum)
        curID = PAutils.Encode(searchResult['slug'])

        date = searchResult['publish_date']
        if date:
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        displayDate = releaseDate if date else ''

        if searchData.date and displayDate:
            score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    slug = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]

    sceneURL = '%s/scenes/%s.json' % (PAsearchSites.getSearchSearchURL(siteNum), slug)
    detailsPageElements = PAutils.HTTPRequest(sceneURL).json()['pageProps']['content']

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements['title'], siteNum)

    # Summary
    metadata.summary = detailsPageElements['description']

    # Studio
    metadata.studio = 'Stepped Up Media'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = detailsPageElements['site']
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements['tags']:
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements['models_thumbs']:
        actorName = actorLink['name'].strip()
        actorPhotoURL = actorLink['thumb']

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art.append(detailsPageElements['trailer_screencap'])
    for imageType in ['extra_thumbnails', 'thumbs']:
        if imageType in detailsPageElements:
            for image in list(detailsPageElements[imageType]):
                art.append(image)

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
