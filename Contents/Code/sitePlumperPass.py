import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchResults = []
    sceneID = searchData.title.split(' ', 1)[0]

    if unicode(sceneID, 'UTF-8').isdigit():
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()

        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/refstat.php?lid=%s&sid=584' % sceneID
        searchResults.append(sceneURL)

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for result in googleResults:
        match = re.search(r'((?<=\dpp\/)|(?<=\dbbwd\/)|(?<=\dhsp\/)|(?<=\dbbbj\/)|(?<=\dpatp\/)|(?<=\dftf\/)|(?<=\dbgb\/))\d+(?=\/)', result)
        if match:
            sceneID = match.group(0)
            sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/refstat.php?lid=%s&sid=584' % sceneID

            if ('content' in result) and sceneURL not in searchResults:
                searchResults.append(sceneURL)

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        if ('content' in req.url):
            titleNoFormatting = detailsPageElements.xpath('//h2[@class="vidtitle"]')[0].text_content().strip().replace('\"', '')
            curID = PAutils.Encode(sceneURL)

            date = detailsPageElements.xpath('//h3[@class="releases"]//br/preceding-sibling::text()')
            if date:
                releaseDate = datetime.strptime(date[0].strip(), '%B %d, %Y').strftime('%Y-%m-%d')
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
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h2[@class="vidtitle"]')[0].text_content().strip().replace('\"', ''), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "vidinfo")]/p')[0].text_content().strip()

    # Studio
    metadata.studio = 'PlumperPass'

    # Tagline and Collection(s)
    if 'bbwd/' in req.url:
        tagline = 'BBW Dreams'
        metadata.tagline = tagline
    elif 'bbbj/' in req.url:
        tagline = 'Big Babe Blowjobs'
        metadata.tagline = tagline
    elif 'hsp/' in req.url:
        tagline = 'Hot Sexy Plumpers'
        metadata.tagline = tagline
    elif 'patp/' in req.url:
        tagline = 'Plumpers At Play'
        metadata.tagline = tagline
    elif 'ftf/' in req.url:
        tagline = 'First Time Fatties'
        metadata.tagline = tagline
    elif 'bgb/' in req.url:
        tagline = 'BBWs Gone Black'
        metadata.tagline = tagline
    else:
        tagline = metadata.studio
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    if detailsPageElements.xpath('//p[@class="tags clearfix"]/a/text()'):
        genres = detailsPageElements.xpath('//p[@class="tags clearfix"]/a/text()')
    else:
        genres = detailsPageElements.xpath('//meta[@name="keywords"]/@content')[0].split(',')
    for genreLink in genres:
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = detailsPageElements.xpath('//h3[@class="releases"]/a')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/%s' % actorLink.xpath('.//@href')[0].strip()

            req = PAutils.HTTPRequest(actorPageURL)
            actorPageElements = HTML.ElementFromString(req.text)
            actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/%s' % actorPageElements.xpath('//div[@class="row mainrow"]//img/@src')[0].strip()

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@class="movie-trailer"]//@src',
    ]

    videoImage = detailsPageElements.xpath('//div[@class="movie-big"]//script')[0].text_content()
    pattern = re.compile(r'(?<=image: ").*(?=")')
    if pattern.search(videoImage):
        imageID = pattern.search(videoImage).group(0)
        img = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/%s' % imageID

        art.append(img)

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if 'http' not in img:
                img = PAsearchSites.getSearchBaseURL(siteNum) + '/t1/%s' % img

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
