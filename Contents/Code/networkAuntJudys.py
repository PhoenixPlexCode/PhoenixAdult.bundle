import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@class="update_details"]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('./div/a')[0].text_content(), siteNum)
        sceneURL = searchResult.xpath('./div/a/@href')[0]

        if '_vids.html' in sceneURL.lower():
            curID = PAutils.Encode(sceneURL)

            date = searchResult.xpath('.//div[@class="cell update_date"]')
            if date[0]:
                releaseDate = datetime.strptime(date[0].text_content().strip(), '%m/%d/%Y').strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''
            displayDate = releaseDate if date else ''

            if searchData.date and displayDate:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Aunt Judy\'s] %s' % (titleNoFormatting, displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//span[@class="title_bar_hilite"]')[0].text_content().strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath('//span[@class="update_description"]')[0].text_content().strip()

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.studio = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="gallery_info"]//div[@class="cell update_date"]')
    if date[0]:
        date_object = datetime.strptime(date[0].text_content().strip(), '%m/%d/%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//span[@class="update_tags"]/a'):
        genreName = PAutils.parseTitle(genreLink.text_content().strip(), siteNum)

        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = detailsPageElements.xpath('//p/span[@class="update_models"]/a')
    for actorLink in actors:
        actorName = actorLink.text_content().strip()

        modelURL = actorLink.xpath('./@href')[0]
        req = PAutils.HTTPRequest(modelURL)
        actorPageElements = HTML.ElementFromString(req.text)

        try:
            actorPhotoURL = actorPageElements.xpath('//div[@class="cell_top cell_thumb"]//@src0_1x')[0]
            if 'http' not in actorPhotoURL:
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL
        except:
            actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    return metadata
