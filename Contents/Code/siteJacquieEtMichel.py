import PAsearchSites
import PAgenres
import PAactors
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle + '.html')
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@class="col-lg-3 col-md-4 col-sm-6 col-xs-6 video-item" and @data-get-thumbs-url]'):
        titleNoFormatting = searchResult.xpath('.//p[@class="title-video"]')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('./a/@href')[0])
        releaseDate = parse(searchResult.xpath('.//div[@class="infos-video"]/p')[0]
                            .text_content().replace('Added on', '').strip()).strftime('%Y-%m-%d')

        if searchDate:
            score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    # SceneId search
    sceneIdURL = PAsearchSites.getSearchBaseURL(siteNum) + '/en/videos/show/'+ encodedTitle
    sceneReq = PAutils.HTTPRequest(sceneIdURL)
    sceneSearchResults = HTML.ElementFromString(sceneReq.text)

    sceneTitleNoFormatting = sceneSearchResults.xpath('//div[@class="video-player"]/h1')[0].text_content().strip()
    sceneCurID = PAutils.Encode(sceneIdURL)
    sceneReleaseDate = parse(sceneSearchResults.xpath('//span[@class="publication"]')[0].text_content().strip())

    if sceneTitleNoFormatting and sceneCurID and sceneReleaseDate:
        results.Append(MetadataSearchResult(id='%s|%d' % (sceneCurID, siteNum), name='%s [%s] %s' % (sceneTitleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), sceneReleaseDate), score=score, lang=lang))

    return results


def update(metadata, siteID, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteID) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="video-player"]/h1')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="video-description"]/p')[0].text_content().strip()

    # Studio
    metadata.studio = 'Jacquie Et Michel TV'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteID)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    movieGenres.clearGenres()
    for genre in detailsPageElements.xpath('//span[@class="categories"]//strong'):
        genreName = genre.text_content().replace(',','').strip()
        if genreName == 'Sodomy':
            genreName = 'Anal'
        movieGenres.addGenre(genreName)

    movieGenres.addGenre('French porn')

    # Release Date
    date = parse(detailsPageElements.xpath('//span[@class="publication"]')[0].text_content().strip())
    metadata.originally_available_at = date
    metadata.year = metadata.originally_available_at.year

    # Poster
    art = []
    art.append(detailsPageElements.xpath('//img[@id="video-player-poster"]/@data-src')[0].split(',')[-1].strip().split(' ')[0])

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.google.com'})
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
