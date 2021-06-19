import PAsearchSites
import PAutils

supported_lang = ['en']


def search(results, lang, siteNum, searchData):
    shootID = None
    for parts in searchData.title.split():
        if unicode(parts, 'UTF-8').isdigit():
            shootID = parts
            break

    Log('shoot id %s' % shootID)
    if shootID:
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + '/r/Q/' + shootID
        Log('Scene URL %s' % sceneURL)
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        titleNoFormatting = detailsPageElements.xpath('//h1')[0].text_content().strip()[:-1]
        curID = PAutils.Encode(sceneURL)

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='[%s] %s [%s] %s' % (shootID, titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), ""), score=100, lang="en"))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content().strip()

    # Summary
    summary = detailsPageElements.xpath('//div[contains(@class, "about-section__text")]/p/text()')[0].strip()
    metadata.summary = summary

    # Studio
    metadata.studio = 'StasyQ'

    # Tagline and Collection(s)
    metadata.collections.clear()
    metadata.collections.add('StasyQ')


    # Posters
    art = []
    xpaths = [
        '//div[@class="js-release-gallery "]//a/@href',
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

