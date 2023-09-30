import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip().replace('\'', '')

    if sceneID:
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + "/webmasters/" + re.sub(r'^0+', '', sceneID)
        req = PAutils.HTTPRequest(sceneURL)
        searchResults = HTML.ElementFromString(req.text)
        try:
            titleNoFormatting = PAutils.parseTitle(re.sub(r'^\d+', '', searchResults.xpath('//h1/text()|//h4/span/text()')[0]).strip().lower(), siteNum)
        except:
            try:
                sceneURL = '%s/tour/updates/%s-%s.html' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID, slugify(searchData.title))
                req = PAutils.HTTPRequest(sceneURL)
                searchResults = HTML.ElementFromString(req.text)
                titleNoFormatting = PAutils.parseTitle(re.sub(r'^\d+', '', searchResults.xpath('//h4/span/text()')[0]).strip().lower(), siteNum)
            except:
                try:
                    sceneURL = '%s/tour/updates/%s.html' % (PAsearchSites.getSearchBaseURL(siteNum), re.sub(r'\W', '', searchData.title))
                    req = PAutils.HTTPRequest(sceneURL)
                    searchResults = HTML.ElementFromString(req.text)
                    titleNoFormatting = PAutils.parseTitle(re.sub(r'^\d+', '', searchResults.xpath('//h1/text()|//h4/span/text()')[0]).strip().lower(), siteNum)
                except:
                    sceneURL = '%s/tour/updates/%s.html' % (PAsearchSites.getSearchBaseURL(siteNum), slugify(searchData.title))
                    req = PAutils.HTTPRequest(sceneURL)
                    searchResults = HTML.ElementFromString(req.text)
                    titleNoFormatting = PAutils.parseTitle(re.sub(r'^\d+', '', searchResults.xpath('//h1/text()|//h4/span/text()')[0]).strip().lower(), siteNum)

        curID = PAutils.Encode(sceneURL)

        releaseDate = searchData.dateFormat() if searchData.date else ''

        score = 100

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))
    else:
        # Handle 3 Types of Links: First, Last; First Only; First-Last
        try:
            searchData.encoded = re.search(r'^\S*.\S*', searchData.title).group(0).replace(' ', '').lower()

            req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded + ".html")
            searchResults = HTML.ElementFromString(req.text)

            if searchResults.xpath('//html')[0].text_content() == 'Page not found':
                raise Exception
        except:
            try:
                searchData.encoded = re.search(r'^\S*.\S*', searchData.title).group(0).replace(' ', '-').lower()

                req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded + ".html")
                searchResults = HTML.ElementFromString(req.text)

                if searchResults.xpath('//html')[0].text_content() == 'Page not found':
                    raise Exception
            except:
                searchData.encoded = re.search(r'^\S*', searchData.title).group(0).lower()

                req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded + ".html")
                searchResults = HTML.ElementFromString(req.text)
        try:
            pageResults = (int)(searchResults.xpath('//span[@class="number_item "]')[0].text_content().strip())
        except:
            pageResults = 1

        for x in range(pageResults):
            if x == 1:
                searchResults.xpath('//a[contains(@class, "in_stditem")]/@href')[1]
                req = PAutils.HTTPRequest(PAsearchSites.getSearchBaseURL(siteNum) + searchResults.xpath('//a[contains(@class, "in_stditem")]/@href')[1])
                searchResults = HTML.ElementFromString(req.text)
            for searchResult in searchResults.xpath('//div[@class="infos"]'):
                resultTitleID = searchResult.xpath('.//span[@class="video-title"]')[0].text_content().strip()

                titleNoFormatting = PAutils.parseTitle(re.sub(r'^\d+', '', resultTitleID).lower(), siteNum)

                resultID = re.sub(r'\D.*', '', resultTitleID)

                sceneURL = searchResult.xpath('.//a/@href')[0]
                curID = PAutils.Encode(sceneURL)

                date = searchResult.xpath('.//span[@class="video-date"]')[0].text_content().strip()

                if date:
                    releaseDate = parse(date).strftime('%Y-%m-%d')
                else:
                    releaseDate = searchData.dateFormat() if searchData.date else ''
                releaseDate = parse(date).strftime('%Y-%m-%d')
                displayDate = releaseDate if date else ''

                if sceneID == resultID:
                    score = 100
                elif searchData.date and displayDate:
                    score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
                else:
                    score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = ''
    if len(metadata_id) > 2:
        sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    if 'webmasters' in sceneURL:
        resultTitleID = detailsPageElements.xpath('//h1/text()')[0].strip()
    else:
        resultTitleID = detailsPageElements.xpath('//h4/span')[0].text_content().strip()

    sceneID = re.sub(r'\D.*', '', resultTitleID)
    metadata.title = PAutils.parseTitle(re.sub(r'^\d+', '', resultTitleID).strip().lower(), siteNum)

    # Summary
    try:
        if 'webmasters' in sceneURL:
            metadata.summary = detailsPageElements.xpath('//div[@class="row gallery-description"]//div')[1].text_content().strip()
        else:
            metadata.summary = detailsPageElements.xpath('//div[@class="row"]//a/@title')[0].strip()
    except:
        pass

    # Tagline and Collection(s)
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)
    metadata.collections.add(metadata.studio)

    # Actor(s)
    if 'webmasters' in sceneURL:
        actors = detailsPageElements.xpath('//spam[@class="key-words"]//a')
    else:
        actors = detailsPageElements.xpath('//h5//a')

    # Remove Actor Names from Genre List
    try:
        genres = detailsPageElements.xpath('//meta[@name="keywords"]/@content')[0].replace('Aussie Ass', '')
        genres = re.sub(r'id.\d*', '', genres, flags=re.IGNORECASE).lower()
    except:
        genres = ''

    for key, values in actorsDB.items():
        for item in values:
            if item.lower() in genres:
                genres = genres.replace(item.lower(), '')

    if actors:
        for actorLink in actors:
            actorName = actorLink.text_content().title()
            genres = genres.replace(actorName.lower(), '')

            modelURL = actorLink.xpath('./@href')[0].replace('MonteCooper', 'MonteLuxe')
            req = PAutils.HTTPRequest(modelURL)
            actorsPageElements = HTML.ElementFromString(req.text)

            try:
                img = actorsPageElements.xpath('//img[contains(@id, "set-target")]/@src')[0]
                if img:
                    if 'http' not in img:
                        actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + img
            except:
                actorPhotoURL = ''

            movieActors.addActor(actorName, actorPhotoURL)

    # Date
    date = ''
    try:
        if 'webmasters' in sceneURL:
            pageResults = (int)(actorsPageElements.xpath('//span[@class="number_item "]')[0].text_content().strip())

            if not pageResults:
                pageResults = 1

            for x in range(pageResults):
                if x == 1:
                    actorsPageElements.xpath('//a[contains(@class, "in_stditem")]/@href')[1]
                    actorPageURL = '%s/%s' % (PAsearchSites.getSearchBaseURL(siteNum), actorsPageElements.xpath('//a[contains(@class, "in_stditem")]/@href')[1])
                    req = PAutils.HTTPRequest(actorPageURL)
                    actorsPageElements = HTML.ElementFromString(req.text)

                for sceneElements in actorsPageElements.xpath('//div[@class="box"]'):
                    if sceneID in sceneElements.xpath('.//a/text()')[1]:
                        date = actorsPageElements.xpath('.//span[@class="video-date"]')[0].text_content().strip()
                        break
    except:
        pass

    if date:
        date = parse(date).strftime('%d-%m-%Y')
        date_object = datetime.strptime(date, '%d-%m-%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date = parse(sceneDate).strftime('%d-%m-%Y')
        date_object = datetime.strptime(date, '%d-%m-%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in genres.split(','):
        genreName = genreLink.strip()

        movieGenres.addGenre(genreName)

    # Posters
    xpaths = [
        '//img[contains(@alt, "content")]/@src',
        '//div[@class="box"]//img/@src',
    ]

    altURL = ''
    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if 'http' not in img:
                if 'join' in img:
                    break
                elif 'webmasters' in sceneURL:
                    img = sceneURL + "/" + img
                else:
                    img = '%s/%s' % (PAsearchSites.getSearchBaseURL(siteNum), img)
            art.append(img)
        if 'webmasters' not in sceneURL:
            altURL = PAsearchSites.getSearchBaseURL(siteNum) + "/webmasters/" + re.sub(r'^0+', '', sceneID)
            req = PAutils.HTTPRequest(altURL)
            detailsPageElements = HTML.ElementFromString(req.text)
            sceneURL = altURL

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


actorsDB = {
    'Belinda Belfast': ['belinda belfast'],
    'Charlotte Star': ['charlotte,star'],
    'Charlie Brookes': ['charlie, brookes', 'charlie'],
    'Monte Cooper': ['monte, cooper', 'monte cooper'],
}
