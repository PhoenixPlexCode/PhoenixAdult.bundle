import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[contains(@class, "main-content")]//div[@class="-g-vc-grid"]'):
        titleNoFormatting = searchResult.xpath('./div[@class="-g-vc-item-title"]//a/@title')[0]
        subSite = searchResult.xpath('./div[@class="-g-vc-item-channel"]//a/@title')[0]
        curID = PAutils.Encode(searchResult.xpath('./div[@class="-g-vc-item-title"]//a/@href')[0])
        date = searchResult.xpath('./div[@class="-g-vc-item-date"]')[0].text_content().strip()
        releaseDate = parse(date).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [LetsDoeIt/%s] %s' % (titleNoFormatting, subSite, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Studio
    metadata.studio = 'Porndoe Premium'

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@class="-mvd-heading"]')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@class="-mvd-description"]')[0].text_content().strip()

    # Tagline and Collection(s)
    tagline = detailsPageElements.xpath('//div[@class="-mvd-grid-actors"]/span/a')[0].text_content().strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    for genreLink in detailsPageElements.xpath('//span[@class="-mvd-list-item"]/a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="-mvd-grid-stats"]')[0].text_content().strip()
    if date:
        date = date.split('•')[-1].strip()
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="-mvd-grid-actors"]/span/a[@title]'):
        actorName = ''
        actorPhotoURL = ''

        actorPageURL = actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        actorName = actorPage.xpath('//div[@class="-aph-heading"]//h1')[0].text_content().strip()
        try:
            actorPhotoURL = actorPage.xpath('//div[@class="-api-poster-item"]//img/@src')[0]
            if 'http' not in actorPhotoURL:
                actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL
        except:
            pass

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//picture[@class="-vcc-picture"]//img/@src',
        '//div[@class="swiper-wrapper"]/div/a/div/@data-bg'
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            art.append(poster)

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
