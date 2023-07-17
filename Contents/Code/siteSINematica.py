import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="grid-item"]'):
        titleNoFormatting = searchResult.xpath('.//h5/a')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('.//h5/a@href')[0])

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())
        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@class="description"]')[0].text_content().strip()

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[@class="synopsis"]/p')[0].text_content().strip()
    except:
        pass

    # Studio
    studio = 'SINematica'
    metadata.studio = studio

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = detailsPageElements.xpath('//div[@class="studio"]/span')[1].text_content().strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)
    metadata.collections.add(studio)

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[@class="tags"]/a'):
        genreName = genreLink.text_content().strip().lower()
        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//div[@class="video-performer"]/a'):
        actorName = actorLink.text_content().strip()
        movieActors.addActor(actorName, '')

    # Release Date
    if 'porn-movie' not in sceneURL:
        date = detailsPageElements.xpath('//span[@class="publish_date"]')[0].text_content().strip()
    else:
        date = detailsPageElements.xpath('//span[@class="out_date"]')[0].text_content().replace('Year :', '').strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Director
    director = metadata.directors.new()
    try:
        movieDirector = detailsPageElements.xpath('//span[@class="director"]')[0].text_content().replace(
            'Director :', '').strip()
        director.name = movieDirector
    except:
        pass

    # Poster
    xpaths = [
        '//head/link[@rel="image_src"]/@href',
        '//a[@data-target="#inlineScreenshotsModal"]/img/@data-src'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            img = img.replace('/320/', '/1920/')
            img = img.replace('320c.jpg', '1920c.jpg')
            img = img.replace('/720/', '/1920/')
            img = img.replace('720c.jpg', '720c.jpg')

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
