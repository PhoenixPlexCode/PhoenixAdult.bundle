import PAutils
import PAsearchSites

def search(results, lang, siteNum, searchData):
    searchResults = []

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum)
    for sceneURL in googleResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        curID = PAutils.Encode(sceneURL)
        title = PAutils.parseTitle(detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//h3')[0].text_content().strip(), siteNum)
        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), title.lower())

        date = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p')[1].text_content().split('-')[1].strip()
        if date:
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releasedate = "0"
        
        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name = '%s [%s]' % (title, releaseDate), score=score, lang=lang))
        
def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//h3')[0].text_content().strip(), siteNum)

    # Summary 
    metadata.summary = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p')[-1].text_content()
    
    # Studio
    metadata.studio = "TGirl Japan" + ' Hardcore' if siteNum == 1330 else ''

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p')[1].text_content().split('-')[1].strip()
    date_object = parse(date)
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Actors
    movieActors.clearActors()
    actorLink = detailsPageElements.xpath('//div[@class="trailer_videoinfo"]//p/a')[0]
    actorName = actorLink.text_content().strip()

    actorURL = PAsearchSites.getSearchBaseURL(siteNum) + actorLink.xpath('.//@href')[0]
    req = PAutils.HTTPRequest(actorURL)
    actorPageElements = HTML.ElementFromString(req.text)
    actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPageElements.xpath('//div[@class="model_photo"]/img/@src')[0]

    movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []
    for poster in detailsPageElements.xpath('//div[@class="trailerpage_photoblock_fullsize"]//a/@href'):
        art.append(PAsearchSites.getSearchBaseURL(siteNum)+ '/tour/' + poster)
        
    Log('Artwork found: %d' % len(art))   
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            Log('74')
            try:
                Log('76')
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
                Log('88')
                pass

    return metadata
