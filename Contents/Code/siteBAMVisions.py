import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@class="category_listing_wrapper_updates"]'):
        titleNoFormatting = searchResult.xpath('.//h3/a')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('.//h3/a/@href')[0])
        videoBG = PAutils.Encode(searchResult.xpath('.//img/@src0_3x')[0])

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, videoBG), name='%s [BAMVisions]' % titleNoFormatting, score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    scenePoster = PAutils.Decode(metadata_id[2])
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="item-info"]/h4/a')[0].text_content().strip()

    # Summary
    description = detailsPageElements.xpath('//p[@class="description"]')
    if description:
        metadata.summary = description[0].text_content().strip()

    # Studio
    metadata.studio = 'BAMVisions'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//ul[@class="item-meta"]/li[1]')[0].text_content().split('Release Date:')[1].strip()
    if date:
        date_object = datetime.strptime(date, '%B %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.addGenre('Anal')
    movieGenres.addGenre('Hardcore')

    # Actor(s)
    actors = detailsPageElements.xpath('//div[@class="item-info"]/h5/a')
    for actorLink in actors:
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        actorPageURL = actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        img = actorPage.xpath('//div[@class="profile-pic"]/img/@src0_3x')
        if img:
            actorPhotoURL = img[0]
            if 'http' not in actorPhotoURL:
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art.append(PAsearchSites.getSearchBaseURL(siteNum) + scenePoster)

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
