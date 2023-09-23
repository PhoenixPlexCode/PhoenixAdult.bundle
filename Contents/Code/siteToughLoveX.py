import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.replace(' ', '_').lower()
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@class="col-sm-3"]'):
        titleNoFormatting = searchResult.xpath('.//h5')[0].text_content().strip()
        sceneURL = searchResult.xpath('.//a/@href')[0]
        curID = PAutils.Encode(sceneURL)

        date = searchResult.xpath('.//div[@class="pull-right"][./i[@class="fa fa-calendar"]]')
        if date:
            parseDate = date[0].text_content().strip()
            parseDate = re.sub(r'(st|nd|rd|th)', '', parseDate)
            releaseDate = datetime.strptime(parseDate, '%d %b %Y').strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if searchData.date and displayDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="description"]//p')[0].text_content().strip()

    # Studio
    metadata.studio = 'Radical Cash'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    genres = detailsPageElements.xpath('//dd[2]')
    for genreLink in detailsPageElements.xpath('//dd[2]'):
        genreName = genreLink.text_content().strip().lower()

        movieGenres.addGenre(genreName)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actor(s)

    actors = detailsPageElements.xpath('//dd[1]')
    for actorLink in actors:
        actorName = actorLink.xpath('.//a[1]')[0].text_content().strip()
        actorPhotoURL = actorLink.xpath('.//a[2]//img/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

        try:
            actorName = actorLink.xpath('.//a[3]')[0].text_content().strip()
            actorPhotoURL = actorLink.xpath('.//a[4]//img/@src')[0]
            movieActors.addActor(actorName, actorPhotoURL)
        except:
            pass

    # Director
    directorName = 'Charles Dera'
    movieActors.addDirector(directorName, '')

    # Posters
    req = PAutils.HTTPRequest(detailsPageElements.xpath('//dd[1]//a/@href')[0])
    posters = HTML.ElementFromString(req.text)
    for poster in posters.xpath('//a[contains(@href, "%s")]//img/@src' % sceneURL):
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
