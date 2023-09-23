import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(fix_xml(req.text))

    for searchResult in searchResults.xpath('//div[@class="scene-primary-details"]'):
        titleNoFormatting = searchResult.xpath('.//h6')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('.//a/@href')[0])

        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())
        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


# trying to remove malformed parts from page to make sure xpath works
def fix_xml(text):
    text = re.sub(r'<head>.*?</head>', '', text, flags=re.DOTALL)
    text = re.sub(r'<footer.*?</footer>', '', text, flags=re.DOTALL)
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<video.*?</video>', '', text, flags=re.DOTALL)
    text = re.sub(r'<option.*?</option>', '', text, flags=re.DOTALL)
    return text.replace('&nbsp;', '')


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    req = PAutils.HTTPRequest(PAsearchSites.getSearchBaseURL(siteNum) + sceneURL)
    detailsPageElements = HTML.ElementFromString(fix_xml(req.text))

    # Title
    metadata.title = detailsPageElements.xpath('//h1[@class="description"]')[0].text_content().strip()

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[@class="synopsis"]/p')[0].text_content().strip()
    except:
        pass

    # Studio
    studio = 'SINematica'
    metadata.studio = studio

    # Tagline and Collection(s)
    tagline = detailsPageElements.xpath('//div[@class="studio"]/span')[1].text_content().strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)
    metadata.collections.add(studio)

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="tags"]/a'):
        genreName = genreLink.text_content().strip().lower()
        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLink in detailsPageElements.xpath('//div[@class="video-performer"]/a'):
        actorName = actorLink.text_content().strip()
        movieActors.addActor(actorName, '')

    # Release Date
    date = detailsPageElements.xpath('//div[@class="release-date"]')[0].text_content().replace('Released:', '').strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Poster
    xpaths = [
        '//head/link[@rel="image_src"]/@href',
        '//a[@data-target="#inlineScreenshotsModal"]/img/@data-src'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            img = img.replace('/320/', '/1920/')
            img = img.replace('320c.jpg', '1920c.jpg')
            img = img.replace('/720/', '/1920/')
            img = img.replace('720c.jpg', '720c.jpg')

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
