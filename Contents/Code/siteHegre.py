import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneURL = 'https://www.hegre.com/films/%s' % searchData.title.replace(' ', '-').lower()
    req = PAutils.HTTPRequest(sceneURL)

    if req.ok:
        searchResult = HTML.ElementFromString(req.text)
        curID = PAutils.Encode(sceneURL)
        titleNoFormatting = searchResult.xpath('//h1')[0].text_content().strip()
        date = searchResult.xpath('//span[@class="date"]')[0].text_content().strip()
        releaseDate = parse(date).strftime('%Y-%m-%d')

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=100, lang=lang))
    else:
        searchData.encoded = searchData.encoded + ('&year=' + searchData.dateFormat('%Y')) if searchData.date else searchData.encoded
        req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
        searchResults = HTML.ElementFromString(req.text)
        for searchResult in searchResults.xpath('//div[contains(@class, "item")]'):
            sceneURL = searchResult.xpath('.//a/@href')[0]
            if '/films/' in sceneURL or '/massage/' in sceneURL:
                curID = PAutils.Encode(sceneURL)
                titleNoFormatting = searchResult.xpath('.//img/@alt')[0].strip()
                date = searchResult.xpath('.//div[@class="details"]/span[last()]')[0].text_content().strip()
                releaseDate = parse(date).strftime('%Y-%m-%d')

                if searchData.date:
                    score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
                else:
                    score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//meta[@property="og:title"]/@content')[0].strip()

    # Summary
    summary = detailsPageElements.xpath('//div[@class="record-description-content record-box-content"]')[0].text_content().strip()
    metadata.summary = summary[:summary.find('Runtime')].strip()

    # Studio
    metadata.studio = 'Hegre'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//span[@class="date"]')[0].text_content().strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//a[@class="tag"]'):
        genreName = genreLink.text_content().strip().lower()

        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = detailsPageElements.xpath('//a[@class="record-model"]')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.get('title').strip()
            actorPhotoURL = actorLink.xpath('.//img/@src')[0].replace('240x', '480x')

            movieActors.addActor(actorName, actorPhotoURL)

    # Director
    directorName = 'Petter Hegre'
    directorPhoto = 'https://img.discogs.com/TafxhnwJE2nhLodoB6UktY6m0xM=/fit-in/180x264/filters:strip_icc():format(jpeg):mode_rgb():quality(90)/discogs-images/A-2236724-1305622884.jpeg.jpg'
    movieActors.addDirector(directorName, directorPhoto)

    # Posters
    art.append(detailsPageElements.xpath('//meta[@name="twitter:image"]/@content')[0].replace('board-image', 'poster-image').replace('1600x', '640x'))
    art.append(detailsPageElements.xpath('//meta[@name="twitter:image"]/@content')[0].replace('1600x', '1920x'))

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
