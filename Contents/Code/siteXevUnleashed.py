import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    directURL = '%s/updates/%s.html' % (PAsearchSites.getSearchBaseURL(siteNum), slugify(searchData.title.replace('\'', '')))
    req = PAutils.HTTPRequest(directURL)

    if req.ok:
        detailsPageElements = HTML.ElementFromString(req.text)
        titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//span[@class="update_title"]')[0].text_content().strip(), siteNum)
        curID = PAutils.Encode(directURL)
        date = detailsPageElements.xpath('//span[@class="availdate"]/br/preceding-sibling::text()')

        if date:
            releaseDate = parse(date[0].strip()).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if searchData.date and displayDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    url = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded
    req = PAutils.HTTPRequest(url)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@class="updateItem"]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//h4')[0].text_content().strip(), siteNum)
        sceneURL = searchResult.xpath('.//@href')[0]
        curID = PAutils.Encode(sceneURL)
        date = searchResult.xpath('.//p/span')

        if date:
            releaseDate = parse(date[0].text_content().strip()).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if searchData.date and displayDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        if sceneURL.lower() != directURL:
            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//span[@class="update_title"]')[0].text_content().strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//span[@class="latest_update_description"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'Xev Unleashed'

    # Collection(s)
    metadata.collections.add(metadata.studio)

    # Release Date
    date = detailsPageElements.xpath('//span[@class="availdate"]/br/preceding-sibling::text()')
    if date:
        date_object = datetime.strptime(date[0].strip(), '%m/%d/%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//span[@class="update_tags"]/a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    movieActors.addActor('Xev Bellringer', 'https://xevunleashed.com/content//contentthumbs/00/01/1-set-2x.jpg')

    if 'princess leia' in detailsPageElements.xpath('//meta[@name="keywords"]/@content')[0].lower():
        movieActors.addActor('Princess Leia', '')

    # Posters
    xpaths = [
        '//div[@class="update_image"]//img/@src0_4x'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if 'http' not in img:
                img = '%s/%s' % (PAsearchSites.getSearchBaseURL(siteNum), img)

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
