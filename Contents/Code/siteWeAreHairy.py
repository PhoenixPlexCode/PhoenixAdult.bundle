import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="results"]/ul/li'):
        titleNoFormatting = searchResult.xpath('.//p[@class="title"]/a')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('.//div[@class="top"]/p/a/@href')[0])
        releaseDate = parse(searchResult.xpath('.//p[@class="short"]')[0].text_content().replace('Added:', '').strip()).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [We Are Hairy] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//title')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="desc"]/div[1]/p')[0].text_content().strip()

    # Studio
    metadata.studio = 'We Are Hairy'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//span[@class="added"]/time')[0].text_content().strip()
    if date:
        date_object = datetime.strptime(date, '%b %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="tagline"]/p/a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    movieGenres.addGenre('Hairy Girls')
    movieGenres.addGenre('Hairy Pussy')

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="meet"]/a/img'):
        actorName = actorLink.get('alt').replace('WeAreHairy.com', '').strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Director(s)
    try:
        directors = detailsPageElements.xpath('//div[@class="desc"]/div[2]/p')
        for directorLink in directors:
            directorName = directorLink.text_content().strip()

            movieActors.addDirector(directorName, '')
    except:
        pass

    # Posters
    xpaths = [
        '//div[@class="moviemain"]/div[1]/a/img/@src'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if not img.startswith('http'):
                img = 'https:' + img

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
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
