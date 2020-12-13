import PAsearchSites
import PAgenres
import PAactors
import PAextras
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):
    sceneID = None
    splited = searchTitle.split(' ')

    searchResults = []
    
    if unicode(splited[0], 'UTF-8').isdigit():
        sceneID = splited[0]
        searchTitle = searchTitle.replace(sceneID, '', 1).strip()
        sceneURL = '%s%s%s' % (PAsearchSites.getSearchSearchURL(siteNum), sceneID, '.html')
        searchResults.append(sceneURL)

    googleResults = PAutils.getFromGoogleSearch(searchTitle, siteNum)
    for result in googleResults:
        try:
            sceneID = re.search(r'(?<=-).*(?=\.)', result).group(0)
            sceneURL = '%s%s%s' % (PAsearchSites.getSearchSearchURL(siteNum), sceneID, '.html')
            if ('/update/' in result) and sceneURL not in searchResults:
                searchResults.append(sceneURL)
        except:
            pass

    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        titleDate = detailsPageElements.xpath('//title')[0].text_content().split('Released')
        titleNoFormatting = titleDate[0].strip()
        releaseDate = parse(titleDate[-1].replace('!','').strip()).strftime('%Y-%m-%d')
        curID = PAutils.Encode(sceneURL)

        score = 100

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, siteID, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    titleDate = detailsPageElements.xpath('//title')[0].text_content().split('Released')
    metadata.title = titleDate[0].strip()

    # Summary
    metadata.summary = detailsPageElements.xpath('//div[@id="Bio"]')[0].text_content().strip()

    # Studio
    metadata.studio = 'First Time Videos'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteID).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres() 
    if PAsearchSites.getSearchSiteName(siteID).lower() == "FTVGirls".lower():
        for genreName in ['Teen', 'Solo', 'Public']:
            movieGenres.addGenre(genreName)
    elif PAsearchSites.getSearchSiteName(siteID).lower() == "FTVMilfs".lower():
        for genreName in ['MILF', 'Solo', 'Public']:
            movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actorName = detailsPageElements.xpath('//h3')[0].text_content().strip()
    actorPhotoURL = detailsPageElements.xpath('//div[@id="Thumbs"]/img/@src')[0]

    movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []
    xpaths = [
        '//img[@id="Magazine"]/@src',
        '//div[@class="gallery"]//div[@class="row"]//@href',
        '//div[@class="thumbs_horizontal"]//@href',
    ]

    googleResults = PAutils.getFromGoogleSearch(actorName, siteID)
    for photoURL in googleResults:
        if ('galleries' in photoURL and 'ccbill' not in photoURL and (actorName.lower() + '-') in photoURL):
            req = PAutils.HTTPRequest(photoURL)
            photoPageElements = HTML.ElementFromString(req.text)
            for xpath in xpaths:
                for img in photoPageElements.xpath(xpath):
                    art.append(img)

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(img)

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.google.com'})
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
