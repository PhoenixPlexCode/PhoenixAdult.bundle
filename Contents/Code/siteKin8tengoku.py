import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    directURL = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()

    if sceneID:
        directURL = '%s/moviepages/%s/index.html' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID)
        req = PAutils.HTTPRequest(directURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//p[@class="sub_title"]|//p[@class="sub_title_vip"]')[0].text_content().split('/')[0].strip(), siteNum)
        curID = PAutils.Encode(directURL)

        date = detailsPageElements.xpath('//tr[./*[contains(., "Date")]]//td[@class="movie_table_td2"]')
        if date:
            releaseDate = parse(date[0].text_content().strip()).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        score = 100

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    searchData.encoded = searchData.title.replace(' ', '+')
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@class="movie_list"]'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + searchResult.xpath('.//div[@class="movielisttext03"]/a/@href')[0]

        if not directURL == sceneURL:
            titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//div[@class="movielisttext02"]')[0].text_content().strip(), siteNum)
            curID = PAutils.Encode(sceneURL)

            releaseDate = searchData.dateFormat() if searchData.date else ''

            score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//p[@class="sub_title"]|//p[@class="sub_title_vip"]')[0].text_content().split('/')[0].strip(), siteNum)

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Release Date
    date = detailsPageElements.xpath('//tr[./*[contains(., "Date")]]//td[@class="movie_table_td2"]')
    if date:
        date_object = datetime.strptime(date[0].text_content().strip(), '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//tr[./*[contains(., "Category")]]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//tr[./*[contains(., "Model")]]//a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
    ]

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
