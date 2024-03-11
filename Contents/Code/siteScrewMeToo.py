import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.replace(' ', '+').replace('--', '+').lower()
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="fsp  bor-r relative"]/article'):
        titleNoFormatting = searchResult.xpath('.//h4')[0].text_content().strip()
        sceneURL = searchResult.xpath('.//@href')[0]
        curID = PAutils.Encode(sceneURL)

        date = searchResult.xpath('.//div[@class="fsdate absolute"]/span')[0].text_content().strip()
        if date:
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        releaseDate = parse(date).strftime('%Y-%m-%d')
        displayDate = releaseDate if date else ''

        if searchData.date and displayDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content()

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[h2]')[0].text_content().replace('Read More ...Read Less', '').strip()
    except:
        pass

    # Tagline and Collection(s)
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)
    metadata.collections.add(metadata.studio)

    # Actor(s)
    actors = detailsPageElements.xpath('//a[contains(@title, "Model Bio")]')
    if actors:
        if len(actors) == 2:
            movieGenres.addGenre('Threesome')
        if len(actors) == 3:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content()
            actorPhotoURL = ''

            modelURL = actorLink.xpath('./@href')[0]
            req = PAutils.HTTPRequest(modelURL)
            actorsPageElements = HTML.ElementFromString(req.text)

            img = actorsPageElements.xpath('//div[@class="model-contr-colone"]//@src')[0]
            if img:
                actorPhotoURL = img
                if 'http' not in actorPhotoURL:
                    actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

            movieActors.addActor(actorName, actorPhotoURL)

    fullTitle = re.search(r"(?<=content\/).*(?=\/)", sceneURL).group(0)

    # Release Date
    date = actorsPageElements.xpath('//a[contains(@href, "' + fullTitle + '")]//div[@class="fsdate absolute"]')[0].text_content().strip()

    if not date and sceneDate:
        date = sceneDate

    date = parse(date).strftime('%d-%m-%Y')

    if date:
        date_object = datetime.strptime(date, '%d-%m-%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="amp-category"]')[0].text_content().split('\n'):
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Posters
    xpaths = [
        '//div[@class="amp-vis-mobile"]//@src',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
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
