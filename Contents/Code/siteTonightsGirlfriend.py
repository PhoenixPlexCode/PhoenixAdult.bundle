import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.lower().split('and ')[0].strip().replace(' ', '-')
    for page in range(1, 5):
        req = PAutils.HTTPRequest('%s%s/?p=%d' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded, page))
        searchResults = HTML.ElementFromString(req.text)
        for searchResult in searchResults.xpath('//div[@class="panel-body"]'):
            actorList = []
            firstActor = searchResult.xpath('.//span[@class="scene-actors"]//a')[0].text_content()

            actors = searchResult.xpath('.//span[@class="scene-actors"]//a')
            for actorLink in actors:
                actorName = actorLink.text_content()
                actorList.append(actorName)
            titleNoFormatting = ', '.join(actorList)

            curID = PAutils.Encode(searchResult.xpath('.//a/@href')[0].split('?')[0])

            releaseDate = parse(searchResult.xpath('.//span[@class="scene-date"]')[0].text_content().strip()).strftime('%Y-%m-%d')

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), firstActor.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Tonight\'s Girlfriend] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

        if len(searchResults) < 9:
            break

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Actor(s)
    actorList = []
    actors = detailsPageElements.xpath('//p[@class="grey-performers"]//a')

    sceneInfo = detailsPageElements.xpath('//p[@class="grey-performers"]')[0].text_content()
    for actorLink in actors:
        actorName = actorLink.text_content()
        actorList.append(actorName)

        sceneInfo = sceneInfo.replace(actorName + ',', '').strip()
        actorPageURL = actorLink.get('href').split('?')[0]

        req = PAutils.HTTPRequest(actorPageURL)
        actorPageElements = HTML.ElementFromString(req.text)
        actorPhotoURL = 'https:' + actorPageElements.xpath('//div[contains(@class, "performer-details")]//img/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Title
    metadata.title = ', '.join(actorList)

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//p[@class="scene-description"]')[0].text_content().strip()
    except:
        pass

    # Studio
    metadata.studio = 'Naughty America'

    # Tagline and Collection(s)
    tagline = 'Tonight\'s Girlfriend'
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    try:
        sceneDate = metadata_id[2]
        if sceneDate:
            date_Object = parse(sceneDate)
            metadata.originally_available_at = date_Object
            metadata.year = metadata.originally_available_at.year
    except:
        pass

    # rest of actors (male actors without pages on the site)
    maleActors = sceneInfo.split(',')
    for maleActor in maleActors:
        actorName = maleActor.strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    genres = ['Girlfriend Experience', 'Pornstar', 'Hotel', 'Pornstar Experience']
    if (len(actors) + len(maleActors)) == 3:
        genres.append('Threesome')
        if len(actors) == 2:
            genres.append('BGG')
        else:
            genres.append('BBG')

    for genreLink in genres:
        genreName = genreLink

        movieGenres.addGenre(genreName)

    # Posters/Background
    posterUrl = 'https:' + detailsPageElements.xpath('//img[@class="playcard"]/@src')[0]
    art.append(posterUrl)
    art.append(posterUrl.split('scene/image')[0].split('scene/horizontal')[0] + 'scene/vertical/390x590cdynamic.jpg')

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                images.append(image)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    posterExists = True
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    if not posterExists:
        for idx, image in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                images.append(image)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if height > width:
                    # Item is a poster
                    metadata.posters[art[idx - 1]] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    if not posterExists:
        for idx, image in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[art[idx - 1]] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
