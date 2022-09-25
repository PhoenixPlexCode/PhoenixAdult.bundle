import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    sceneURL = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]

        if int(sceneID) > 10:
            searchData.title = searchData.title.replace(sceneID, '', 1).strip()
            sceneURL = '%s/en/videos/%s' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID)

    if sceneURL:
        req = PAutils.HTTPRequest(sceneURL)
        directPageElements = HTML.ElementFromString(req.text)
        titleNoFormatting = PAutils.parseTitle(directPageElements.xpath('//title')[0].text_content().split('|')[-1].strip(), siteNum)

        curID = PAutils.Encode(sceneURL)
        releaseDate = searchData.dateFormat() if searchData.date else ''

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))
    elif 'search' in PAsearchSites.getSearchSearchURL(siteNum):
        searchURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded
        req = PAutils.HTTPRequest(searchURL)
        searchResults = HTML.ElementFromString(req.text)

        for searchResult in searchResults.xpath('//div[@class="thumb"]'):
            titleNoFormatting = PAutils.parseTitle(searchResult.xpath('//span[@class="desc"]')[0].text_content(), siteNum)
            sceneURL = '%s%s' % (PAsearchSites.getSearchBaseURL(siteNum) + searchResult.xpath('.//a/@href')[0])

            curID = PAutils.Encode(sceneURL)
            releaseDate = searchData.dateFormat() if searchData.date else ''

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Huge Media/%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    title = detailsPageElements.xpath('//title')[0].text_content().replace('’', '\'').split('|')[-1].strip()
    metadata.title = PAutils.parseTitle(title, siteNum)

    # Summary
    for key, value in summaryDB.items():
        if key.lower() == PAsearchSites.getSearchSiteName(siteNum).lower():
            metadata.summary = detailsPageElements.xpath(value[0])[0].text_content().strip()
            break

    # Studio
    metadata.studio = 'Huge Media'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actors
    movieActors.clearActors()
    actors = []
    for key, value in actorsDB.items():
        if key.lower() == PAsearchSites.getSearchSiteName(siteNum).lower():
            actors = detailsPageElements.xpath(value[0])
            break

    if actors and ',' in actors[0].text_content():
        actors = actors[0].text_content().split(',')

    match = re.findall(r'[A-Z]\w+\s[A-Z]\w+', metadata.summary)
    if match:
        actors.extend(match)

    for actorLink in actors:
        actorName = actorLink
        if not isinstance(actorName, str):
            try:
                actorName = actorName.text_content()
            except:
                pass
        actorName = actorName.strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    movieGenres.clearGenres()
    genres = []

    for key, value in genresDB.items():
        if key.lower() == tagline.lower():
            genres.extend(value)
            break

    for genreLink in detailsPageElements.xpath('//a[@class="item_tag"]'):
        genreName = genreLink.text_content().replace('#', '').strip()

        genres.append(genreName)

    for genreName in genres:
        movieGenres.addGenre(genreName)

    # Posters

    xpaths = [
        '//picture[@class="episode__cover-img"]//source[@type="image/jpeg"]/@data-srcset',
        '//div[@class="player_watch"]//source[@type="image/jpeg"]/@data-srcset',
        '//div[@class="player-item__block"]//source[@type="image/jpeg"]/@data-srcset',
        '//div[@class="player-item__preview-container"]//source[@type="image/jpeg"]/@data-srcset',
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if 'http:' not in img:
                img = 'http:' + img

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
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


genresDB = {
    'Stuck4k': ['Stuck'],
    'Tutor4k': ['Tutor', 'MILF'],
    'Sis.Porn': ['Step Sister'],
    'Shame4k': ['MILF'],
    'Mature4k': ['GILF'],
}


summaryDB = {
    'Stuck4k': ['//span[@class="player-info__text-area"]'],
    'Mature4k': ['//span[@class="player-info__text-area"]'],
    'Daddy4k': ['//div[@class="video-full__desc"]/p'],
    'Black4k': ['//div[@class="desc_frame"]/p'],
    'Hunt4k': ['//div[@class="wrap_player_desc"]/p'],
    'Old4k': ['//div[@class="wrap_player_desc"]/p'],
    'Tutor4k': ['//span[@class="episode-about__text text"]'],
    'Sis.Porn': ['//div[@class="player-item__text"]'],
    'Shame4k': ['//div[@class="player-info__text"]'],
    'Fist4k': ['//div[@class="player-item__text text text--sm"]'],
    'Rim4k': ['//div[@class="player-item__text text text--sm"]'],
}


actorsDB = {
    'Mature4k': ['//a[contains(@class, "hid2")]/div[@class="item-info__text"]'],
    'Daddy4k': ['//a[contains(@class, "publisher")]//span[@class="video-info-item__value"]'],
    'Black4k': ['//div[@class="cat_player"]/a'],
    'Old4k': ['//div[@class="cat_player"]/a'],
    'Sis.Porn': ['//div[@class="player-item__row"][./div[contains(., "Name:")]]//span'],
    'Fist4k': ['//div[@class="player-item__about"]//li[.//svg[@class="ico ico--star"]]/div[@class="item-info__text"]'],
    'Rim4k': ['//div[@class="player-item__about"]//li[.//svg[@class="ico ico--star"]]/div[@class="item-info__text"]'],
}
