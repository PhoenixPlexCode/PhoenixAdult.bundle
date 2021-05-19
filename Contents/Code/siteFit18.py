import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    actorName = searchData.title.lower()
    baseURL = PAsearchSites.getSearchSearchURL(siteNum) + actorName.replace(' ', '-') + '/'
    count = 0
    while True:
        count += 1
        searchURL = baseURL + "scene%d" % count
        req = PAutils.HTTPRequest(searchURL)
        if req.status_code ==  404:
            break
        searchPageElements = HTML.ElementFromString(req.text)

        titleNoFormatting = PAutils.parseTitle(searchPageElements.xpath('//div[@class="scene-info medium-7 columns"]/h1/text()')[0], siteNum)
        curID = PAutils.Encode(searchURL)
        actor = searchPageElements.xpath('//div[@class="scene-info medium-7 columns"]/h2/a/text()')[0]
        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=80, lang=lang))


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)
    
    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="scene-info medium-7 columns"]/h1/text()')[0]

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="scene-info medium-7 columns"]/p/text()')[0]

    # Studio
    metadata.studio = 'Fit18'

    # Collections / Tagline
    metadata.collections.clear()
    metadata.tagline = metadata.studio
    metadata.collections.add(metadata.studio)

    # Genres
    movieGenres.clearGenres()
    movieGenres.addGenre("Young")
    movieGenres.addGenre("Gym")

    # Actors
    movieActors.clearActors()
    actorName = detailsPageElements.xpath('//div[@class="scene-info medium-7 columns"]/h2/a/text()')[0]
    actorPhotoURL = ''
    movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = detailsPageElements.xpath('//div[@class="columns small-12 photos"]//div/a/div/img/@src')

    Log('Artwork found: %d' % len(art))
    maxPosters = 2
    maxArt = 5
    for idx, posterUrl in enumerate(art, 1):
        if maxArt == 0 and maxPosters == 0:
            break
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
                    if maxPosters > 0 and width < height:
                        maxPosters = maxPosters - 1
                        metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    if maxArt > 0:
                        maxArt = maxArt - 1
                        metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata