import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()

        directURL = '%s/%s/%s.html' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID, slugify(searchData.title))

        req = PAutils.HTTPRequest(directURL)

        if req.ok:
            detailsPageElements = HTML.ElementFromString(req.text)
            titleNoFormatting = PAutils.parseTitle(detailsPageElements.xpath('//h1[@class="description"]/text()')[0].strip(), siteNum)
            curID = PAutils.Encode(directURL)

            date = detailsPageElements.xpath('//div[@class="release-date"]/text()')
            if date:
                releaseDate = datetime.strptime(date[0].strip(), '%b %d, %Y').strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''

            displayDate = releaseDate if date else ''

            score = 100

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[contains(@class, "item-grid")]/div[@class="grid-item"]'):
        try:
            if siteNum == 815 or siteNum == 1337 or siteNum == 1776 or siteNum == 1800:
                # Modification for JAYs POV, SpankMonster, Hot Wife Fun
                titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//img[contains(@class, "img-full-fluid")]/@title')[0].strip(), siteNum)
                curID = PAutils.Encode(searchResult.xpath('.//article[contains(@class, "scene-update")]/a/@href')[0])
            elif siteNum == 1766 or siteNum == 1779 or siteNum == 1790 or siteNum == 1792:
                # Modification for Bizarre Entertainment, Jonathan Jordan XXX, Smut Factor, Step House XXX
                titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//a[@class="scene-title"]/p/text()')[0].split(' | ', 1)[0].strip(), siteNum)
                curID = PAutils.Encode(searchResult.xpath('.//a[@class="scene-title"]/@href')[0])
            else:
                titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//a[@class="scene-title"]/h6/text()')[0].strip(), siteNum)
                curID = PAutils.Encode(searchResult.xpath('.//a[@class="scene-title"]/@href')[0])

            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))
        except:
            pass

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1[@class="description"]/text()')[0].strip(), siteNum)

    # Summary
    summary = detailsPageElements.xpath('//div[@class="synopsis"]/p/text()')
    if summary:
        metadata.summary = summary[0].strip()

    # Studio
    metadata.studio = 'Adult Empire Cash'

    # Tagline and Collection(s)
    tagline = detailsPageElements.xpath('//div[@class="studio"]//span/text()')[1].strip()
    metadata.tagline = tagline
    metadata.collections.add(metadata.tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="release-date"]/text()')
    if date:
        date_object = datetime.strptime(date[0].strip(), '%b %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreName in detailsPageElements.xpath('//div[@class="tags"]//a/text()'):
        movieGenres.addGenre(genreName)

    # Actor(s)
    for actorLinkHeadshot in detailsPageElements.xpath('//div[@class="video-performer"]//img'):
        actorNameHeadshot = actorLinkHeadshot.get('title')
        actorPhotoURL = actorLinkHeadshot.get('data-bgsrc')

        movieActors.addActor(actorNameHeadshot, actorPhotoURL)

    for actorLink in detailsPageElements.xpath('//div[contains(@class, "video-performer-container")][2]/a'):
        actorName = actorLink.text_content().strip()

        movieActors.addActor(actorName, '')

    # Director
    directorElement = detailsPageElements.xpath('//div[@class="director"]/text()')
    if directorElement:
        directorName = directorElement[0].strip()

        movieActors.addDirector(directorName, '')

    # Posters
    for poster in detailsPageElements.xpath('//div[@id="dv_frames"]//img/@src'):
        img = poster.replace('/320/', '/1280/')
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
                if width > 10:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata
