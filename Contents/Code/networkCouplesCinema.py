import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = searchData.title.split(' ', 1)[0]
    if unicode(sceneID, 'UTF-8').isdigit():
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()
    else:
        sceneID = None

    if sceneID:
        url = '/post/details/' + sceneID
        req = PAutils.HTTPRequest(PAutils.fixUrl(siteNum, url))
        detailsPageElements = HTML.ElementFromString(req.text)

        curID = PAutils.Encode(url)
        titleNoFormatting = detailsPageElements.xpath('//div[contains(@class, "mediaHeader")]//span[contains(@class, "title")]/text()')[0].strip()
        studio = detailsPageElements.xpath('//span[contains(@class, "type")]/text()')[0].split('|')[0].strip()

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, ''), name='%s [%s]' % (titleNoFormatting, studio), score=100, lang=lang))
    else:
        searchData.encoded = searchData.title.replace(' ', '+')
        req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
        searchResults = HTML.ElementFromString(req.text)
        for searchResult in searchResults.xpath('//div[contains(@class, "post")]'):
            titleNoFormatting = searchResult.xpath('.//span[contains(@class, "title")]/text()')[0]
            url = searchResult.xpath('.//a[contains(@class, "media")]/@href')[0]

            studio = searchResult.xpath('.//span[contains(@class, "source")]/text()')[0]

            sceneCover = PAutils.Encode(searchResult.xpath('.//a[contains(@class, "media")]//img[contains(@class, "image")]/@src')[0])

            curID = PAutils.Encode(url)

            score = Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())
            if PAsearchSites.getSearchSiteName(siteNum).lower() == studio.lower():
                score += 50

            results.Append(MetadataSearchResult(id='%s|%d|%s|%s' % (curID, siteNum, searchData.date, sceneCover), name='%s [%s]' % (titleNoFormatting, studio), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.fixUrl(siteNum, PAutils.Decode(metadata_id[0]))
    searchDate = metadata_id[2]
    sceneCover = PAutils.Decode(metadata_id[3]) if len(metadata_id) > 3 else ''

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[contains(@class, "mediaHeader")]//span[contains(@class, "title")]/text()')[0]

    # Summary
    metadata.summary = detailsPageElements.xpath('//span[contains(@class, "description")]/text()')[0].strip()

    # Studio
    metadata.studio = detailsPageElements.xpath('//span[contains(@class, "type")]/text()')[0].split('|')[0].strip()

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add('CouplesCinema')
    metadata.collections.add(metadata.studio)

    # Release Date
    try:
        date_object = parse(searchDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    except:
        Log("Failed to parse searchDate: " + str(searchDate) + ', using release year')
        metadata.year = int(detailsPageElements.xpath('//span[contains(@class, "type")]/text()')[0].split('|')[1].strip())

    # Actors
    movieActors.clearActors()
    for actor in detailsPageElements.xpath('//div[contains(@class, "cast")]/a/text()'):
        movieActors.addActor(actor, '')

    # Posters
    art = []
    xpaths = [
        '//video/@poster',
    ]

    if sceneCover:
        art.append(sceneCover)

    PAutils.processArt(metadata, siteNum, detailsPageElements, art, xpaths)

    return metadata
