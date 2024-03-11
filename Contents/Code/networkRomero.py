import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[contains(@class, "half")]|//article[contains(@class, "post")]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//h2')[0].text_content().strip(), siteNum)

        sceneURL = searchResult.xpath('.//a/@href')[0]
        if not sceneURL.startswith('http'):
            sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
        curID = PAutils.Encode(sceneURL)

        try:
            date = searchResult.xpath('.//h2')[1].text_content().strip().split('&nbsp')[-1]
        except:
            try:
                date = searchResult.xpath('.//div[@class="entry-date"]')[0].text_content().strip()
            except:
                date = ''

        if date:
            releaseDate = parse(date).strftime('%Y-%m-%d')
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
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//meta[@itemprop="name"]/@content|//h1/text()')[0].split('|')[0].split('- Free Video')[0].strip(), siteNum)

    # Summary
    summary = ''
    if (1797 <= siteNum <= 1798):
        paragraphs = detailsPageElements.xpath('//div[@id="fullstory"]/p')
    else:
        paragraphs = detailsPageElements.xpath('//div[@class="cont"]/p|//div[@class="cont"]//div[@id="fullstory"]/p|//div[@class="zapdesc"]//div[not(contains(., "Including"))][.//br]')
    for paragraph in paragraphs:
        text = paragraph.text_content().strip()
        if text and not text == '\xc2\xa0':
            summary = summary + text + '\n'

    metadata.summary = summary.strip()

    # Studio
    metadata.studio = 'Romero Multimedia'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//meta[@property="article:published_time"]/@content')[0].split('T')[0].strip()
    if not date and sceneDate:
        date = sceneDate

    if date:
        date_object = datetime.strptime(date, '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="Cats"]//a/text()|//div[@class="zapdesc"]/div/div/div[contains(., "Including:")]/text()'):
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[contains(@class, "tagsmodels")][./img[@alt="model icon"]]//a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Director
    directorLink = detailsPageElements.xpath('//div[contains(@class, "director")]//a/text()')
    if directorLink:
        directorName = directorLink[0].strip()

        movieActors.addDirector(directorName, '')

    # Posters
    xpaths = [
        '//img[(contains(@class, "alignnone") and contains(@class, "size-full") or contains(@class, "size-medium")) and (not(contains(@class, "wp-image-4512") or contains(@class, "wp-image-492")))]/@src',
        '//div[@class="iehand"]/a/@href',
        '//a[contains(@class, "colorbox-cats")]/@href',
        '//div[@class="gallery"]//a/@href',
    ]

    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            o = urlparse.urlparse(poster, 'http')
            link = urlparse.parse_qs(o.query)
            if 'src' in link:
                poster = link['src'][0]

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
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and idx > 1:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
