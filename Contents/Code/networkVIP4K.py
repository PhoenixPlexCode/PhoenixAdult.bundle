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

        siteName = directPageElements.xpath('//a[@class="player-additional__site ph_register"]')
        if siteName:
            subSite = siteName[0].text_content().strip()
        else:
            subSite = PAsearchSites.getSearchSiteName(siteNum)

        curID = PAutils.Encode(sceneURL)

        date = directPageElements.xpath('//span[@class="player-additional__text"]')
        if date:
            releaseDate = parse(date[0].text_content().strip()).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        if not subSite.lower() == PAsearchSites.getSearchSiteName(siteNum).lower():
            score = score - 1

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [VIP4K/%s] %s' % (titleNoFormatting, subSite, displayDate), score=score, lang=lang))
    elif 'search' in PAsearchSites.getSearchSearchURL(siteNum):
        searchURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded
        req = PAutils.HTTPRequest(searchURL)
        searchResults = HTML.ElementFromString(req.text)

        for searchResult in searchResults.xpath('//div[@class="item__description"]'):
            titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//a[@class="item__title"]')[0].text_content(), siteNum)
            sceneURL = '%s%s' % (PAsearchSites.getSearchBaseURL(siteNum), searchResult.xpath('.//a[@class="item__title"]/@href')[0])

            siteName = searchResult.xpath('.//a[@class="item__site"]')
            if siteName:
                subSite = siteName[0].text_content().strip()
            else:
                subSite = PAsearchSites.getSearchSiteName(siteNum)

            curID = PAutils.Encode(sceneURL)
            releaseDate = searchData.dateFormat() if searchData.date else ''

            if searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            if not subSite.lower() == PAsearchSites.getSearchSiteName(siteNum).lower():
                score = score - 1

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [VIP4K/%s] %s' % (titleNoFormatting, subSite, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    title = PAutils.parseTitle(detailsPageElements.xpath('//title')[0].text_content().split('|')[-1].strip(), siteNum)
    metadata.title = PAutils.parseTitle(title, siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="player-description__text"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'VIP4K'

    # Tagline and Collection(s)
    tagline = detailsPageElements.xpath('//a[@class="player-additional__site ph_register"]')[0].text_content().strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//span[@class="player-additional__text"]')
    if date:
        date_object = parse(date[0].text_content().strip())
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//a[@class="player-description__model model ph_register"]'):
        actorName = actorLink.xpath('.//div[@class="model__name"]')[0].text_content().strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    genres = PAutils.getDictValuesFromKey(genresDB, tagline)
    for genreLink in detailsPageElements.xpath('//div[@class="tags"]/a'):
        genreName = genreLink.text_content().replace('#', '').strip()

        genres.append(genreName)

    for genreName in genres:
        movieGenres.addGenre(genreName)

    # Posters
    xpaths = [
        '//div[@class="player-item__block"]//img/@data-src',
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
    'Stuck 4k': ['Stuck'],
    'Tutor 4k': ['Tutor'],
    'Sis': ['Step Sister'],
    'Shame 4k': ['MILF'],
    'Mature 4k': ['GILF'],
    'Pie 4K': ['Creampie'],
}
