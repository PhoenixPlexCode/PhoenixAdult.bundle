import PAsearchSites
import PAextras
import PAutils


def search(results, lang, siteNum, searchData):

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//li[.//div[@class="time-infos"]]//a'):
        siteName = 'WowGirlsBlog.com'
        titleNoFormatting = searchResult.xpath('./@title')[0].strip()
        curID = PAutils.Encode(searchResult.xpath('./@href')[0])

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, siteName), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@itemprop="headline"]//span/text()')[-1].lstrip("- ").strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[contains(@class, "video-embed")]//p')[0].text_content().strip()

    # Release date
    dateObj = parse(detailsPageElements.xpath('//div[@class="post_date"]/text()')[0])
    metadata.originally_available_at = dateObj
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//div[@itemprop="keywords"]//a')
    for genre in genres:
        genreName = genre.xpath('./text()')[0].strip()
        movieGenres.addGenre(genreName)

    # Actors    
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[@itemprop="actor"]//a/text()')
    for actor in actors:
        actorName = actor.strip()
        movieActors.addActor(actorName, '')

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Posters
    art = []
    art.append(detailsPageElements.xpath('//img[contains(@class, "fp-splash")]/@src'))

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
