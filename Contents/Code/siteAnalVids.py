import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()

        try:
            sceneURL = '%s/watch/%s' % (PAsearchSites.getSearchBaseURL(siteNum), sceneID)
            curID = PAutils.Encode(sceneURL)

            req = PAutils.HTTPRequest(sceneURL)
            scenePageElements = HTML.ElementFromString(req.text)
            titleNoFormatting = scenePageElements.xpath('//h1[@class="watchpage-title"]')[0].text_content().strip()
            Log('Title: %s' % titleNoFormatting)
            releaseDate = ''
            Log('Scene found: %s | %s | %s' % (curID, titleNoFormatting, releaseDate))
            score = 100
            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate),
                                                name='%s [AnalVids] %s' % (titleNoFormatting, releaseDate), score=score,
                                                lang=lang))
        except:
            pass

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.title)
    searchResults = req.json()

    for searchResult in searchResults['terms']:
        if searchResult['type'] == 'scene':
            titleNoFormatting = PAutils.parseTitle(searchResult['name'], siteNum)

            sceneURL = searchResult['url']
            curID = PAutils.Encode(sceneURL)

            releaseDate = searchData.dateFormat() if searchData.date else ''

            if sceneID and int(sceneID) == searchResult['source_id']:
                score = 100
            elif searchData.date:
                score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
            else:
                score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [AnalVids] %s' % (titleNoFormatting, releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1[@class="watchpage-title"]')[0].text_content().strip(), siteNum)

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[@class="scene-description__row"]/dt[contains(., "Description")]/../dd')[0].text_content()
    except:
        pass

    # Studio
    metadata.studio = 'AnalVids'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = detailsPageElements.xpath('//a[@class="watchpage-studioname"]/text()')[0].strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    releaseDate = detailsPageElements.xpath('//span[@class="scene-description__detail"]//a/text()')[0]
    date_object = parse(releaseDate)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//dd/a[contains(@href, "/niche/")]')

    for genreLink in genres:
        genreName = genreLink.text_content().title()
        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//dd/a[contains(@href, "model") and not(contains(@href, "forum"))]')
    for actorLink in actors:
        actorName = actorLink.text_content()

        actorPageURL = actorLink.get('href')
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        actorPhotoURL = actorPage.xpath('//div[@class="model--avatar"]//img/@src')[0]

        movieActors.addActor(actorName, actorPhotoURL)

    # Director
    director = metadata.directors.new()
    if tagline == 'Giorgio Grandi' or tagline == 'Giorgio\'s Lab':
        director.name = 'Giorgio Grandi'
    try:
        directors = detailsPageElements.xpath('//p[@class="director"]/a')
        for dirname in directors:
            director.name = dirname.text_content().strip()
    except:
        pass

    # Posters/Background
    art.append(detailsPageElements.xpath('//div[@id="player"]/@style')[0].split('url(')[1].split(')')[0])

    for img in detailsPageElements.xpath('//div[contains(@class, "thumbs2 gallery")]//img/@src'):
        art.append(img.split('?')[0])
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
