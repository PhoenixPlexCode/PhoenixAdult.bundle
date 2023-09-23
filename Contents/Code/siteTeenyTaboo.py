import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchResults = []
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()
        searchResults.append(PAsearchSites.getSearchSearchURL(siteNum) + sceneID)

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        sceneURL = sceneURL.rsplit('/', 1)[0]
        if '/videos/' in sceneURL and sceneURL not in searchResults:
            searchResults.append(sceneURL)

    for sceneURL in searchResults:
        searchID = None
        req = PAutils.HTTPRequest(sceneURL)
        if req.ok:
            detailsPageElements = HTML.ElementFromString(req.text)

            if not detailsPageElements.xpath('//h2')[0].text_content() == 'Latest Videos':
                titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1[@class="customhcolor"]')[0].text_content().replace('-', ' ').strip(), siteNum)
                curID = PAutils.Encode(sceneURL)
                match = re.search(r'(?<=videos\/).*((?=\/)|\d)', sceneURL)
                if match:
                    searchID = match.group(0)

                date = detailsPageElements.xpath('//span[@class="date"]')
                if date:
                    releaseDate = parse(date[0].text_content().strip()).strftime('%Y-%m-%d')
                else:
                    releaseDate = searchData.dateFormat() if searchData.date else ''

                displayDate = releaseDate if date else ''

                if sceneID and sceneID == searchID:
                    score = 100
                elif searchData.date:
                    score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
                else:
                    score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1[@class="customhcolor"]')[0].text_content().replace('-', ' ').strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//h2[@class="customhcolor2"]')[0].text_content().strip()

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//h4[@class="customhcolor"]')[0].text_content().split(','):
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = re.split(r',|\sand\s', detailsPageElements.xpath('//h3')[0].text_content())
    for actorLink in actors:
        actorName = re.sub(r'\d', '', actorLink).strip().replace('&nbsp', '')
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//center/img/@src',
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
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
