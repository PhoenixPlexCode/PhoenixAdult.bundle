import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(parts[0], 'UTF-8').isdigit():
        sceneID = parts[0]
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()

    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + sceneID
    req = PAutils.HTTPRequest(sceneURL)
    searchResult = HTML.ElementFromString(req.text)

    titleNoFormatting = searchResult.xpath('//h1[contains(@class, "title")]')[0].text_content()
    curID = PAutils.Encode(sceneURL)
    searchID = sceneURL.rsplit('/')[-1].split('-')[0]
    subSite = searchResult.xpath('//a[@aria-label="model-profile"]')[0].text_content().strip()
    releaseDate = searchData.dateFormat() if searchData.date else ''

    if sceneID and sceneID == searchID:
        score = 100
    elif searchData.date:
        score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
    else:
        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

    results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [ManyVids/%s]' % (titleNoFormatting, subSite), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = metadata.id.split('|')
    sceneDate = metadata_id[2]
    sceneURL = PAutils.Decode(metadata_id[0])

    videoURL = 'https://www.manyvids.com/bff/store/video/%s' % sceneURL.rsplit('/')[-1].split('-')[0]
    videoPageElements = PAutils.HTTPRequest(videoURL).json()['data']

    # Title
    metadata.title = PAutils.parseTitle(videoPageElements['title'].strip(), siteNum)

    # Summary
    metadata.summary = videoPageElements['description'].strip()

    # Studio
    metadata.studio = 'ManyVids'

    # Tagline and Collection(s)
    tagline = videoPageElements['model']['displayName']
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in videoPageElements['tagList']:
        genreName = genreLink['label'].strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
    actor = videoPageElements['model']
    actorName = actor['displayName']
    actorPhotoURL = actor['avatar']

    movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art.append(videoPageElements['screenshot'])

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
