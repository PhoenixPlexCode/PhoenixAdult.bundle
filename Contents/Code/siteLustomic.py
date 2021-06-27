import PAsearchSites
import PAutils
from dateutil.relativedelta import relativedelta


def search(results, lang, siteNum, searchData):
    url = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded
    req = PAutils.HTTPRequest(url)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//img[@alt="Video Preview"]/following-sibling::p'):
        titleNoFormatting = searchResult.xpath('//img[@alt="Video Preview"]/following-sibling::p')[0].text_content().strip()
        curID = PAutils.Encode(url)
        
        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())
        
        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [Lustomic]' % titleNoFormatting, score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    Log(metadata)
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    Log(sceneURL)
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//img[@alt="Video Preview"]/following-sibling::p')[0].text_content().strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//img[@alt="Video Description"]/following-sibling::div')[0].text_content().strip()

    # Studio
    metadata.studio = 'Lustomic'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//p[contains(text(),"Starring")]/span')[0].text_content().split(';')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actor in actors:
            actorName = actor.strip()
            actorPhotoURL = ''

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []
    xpaths = [
        '//a[contains(@href,"video_preview_images")]/@href'
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
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
