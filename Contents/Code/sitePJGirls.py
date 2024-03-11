import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="thumb video"]'):
        titleNoFormatting = searchResult.xpath('./h2')[0].text_content().title().strip()
        curID = PAutils.Encode(searchResult.xpath('./a/@href')[0])
        releaseDate = parse(searchResult.xpath('./a/div/span[2]')[0].text_content().strip()).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [PJGirls] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//title')[0].text_content().split('- porn video')[0].strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="text"]/p')[0].text_content().strip()

    # Studio
    metadata.studio = 'PJGirls'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="info"]/h3[1]')[0].text_content().strip()
    if date:
        date_object = datetime.strptime(date, '%B %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="detailTagy clear"]/a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="info"]/h3[3]/a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        try:
            actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.get('href')
            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            actorPhotoURL = actorPage.xpath('//div[@class="image"]/img/@src')[0]
            if 'http' not in actorPhotoURL:
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL
        except:
            pass

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@class="videoObal"]/img/@src',
        '/div[@class="thumb mini"]/a/@href'
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            if not poster.startswith('http'):
                poster = PAsearchSites.getSearchBaseURL(siteNum) + poster

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
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
