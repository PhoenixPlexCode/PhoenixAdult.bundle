import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = searchData.title.split(' ', 1)[0]

    url = PAsearchSites.getSearchSearchURL(siteNum) + sceneID
    req = PAutils.HTTPRequest(url)
    detailsPageElements = HTML.ElementFromString(req.text)

    titleNoFormatting = detailsPageElements.xpath('//div[@class="fltWrap"]/h1/span')[0].text_content().strip()
    curID = PAutils.Encode(url)
    releaseDate = detailsPageElements.xpath('//div[@class="fltRight"]')[0].text_content().replace('Release Date :', '').strip()

    score = 100

    results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [ClubFilly] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="fltWrap"]/h1/span')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[@class="description"]')[0].text_content().replace('Description:', '').strip()

    # Studio
    metadata.studio = 'ClubFilly'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="fltRight"]')[0].text_content().replace('Release Date :', '').strip()
    if date:
        date_object = datetime.strptime(date, '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.addGenre('Lesbian')

    # Actor(s)
    actorText = detailsPageElements.xpath('//p[@class="starring"]')[0].text_content().replace('Starring:', '').strip()
    actors = actorText.split(',')
    if len(actors) > 0:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.strip()
            actorPhotoURL = ''

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//ul[@id="lstSceneFocus"]/li/img/@src'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
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
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
