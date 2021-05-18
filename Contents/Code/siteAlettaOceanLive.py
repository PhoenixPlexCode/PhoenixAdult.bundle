import PAsearchSites
import PAutils

def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum))
    searchPageElements = HTML.ElementFromString(req.text)
    pages = {PAsearchSites.getSearchSearchURL(siteNum)}
    pages.update(searchPageElements.xpath('//div[@class="global_pagination"]/ul/li/a/@href'))
    for link in pages:
        req = PAutils.HTTPRequest(link)
        searchPageElements = HTML.ElementFromString(req.text)
        searchResult = searchPageElements.xpath('//div[contains(@class,"movie-set-list-item")][contains(.,"%s")]' % searchData.title.title())
        if searchResult:
            break        
    if not searchResult:
        return
    searchResult = searchResult[0]
    sceneID = PAutils.Encode(link)
    titleNoFormatting = PAutils.parseTitle(searchResult.xpath('./a/div/div/div/div[2]/text()')[0], siteNum)
    date = searchResult.xpath('./a/div/div/div/div[1]/text()')[0]
    releaseDate = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
    if searchData.date:
        score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
    else:
        score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())
    results.Append(MetadataSearchResult(id='%s|%d|%s' % (sceneID, siteNum, titleNoFormatting), name='%s %s [%s]' % (titleNoFormatting, releaseDate, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))
    return results


def update(metadata, lang, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneID = PAutils.Decode(metadata_id[0])
    title = metadata_id[2].strip().title()
    #For AlettaOceanLive
    if siteNum == 1024:
        req = PAutils.HTTPRequest(sceneID)
        searchPageElements = HTML.ElementFromString(req.text)
        searchResult = searchPageElements.xpath('//div[contains(@class,"movie-set-list-item")][contains(.,"%s")]' % title)[0]

        # Title
        metadata.title = title

        # Studio
        metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

        # Tagline and Collection(s)
        metadata.collections.clear()
        metadata.collections.add(metadata.studio)

        # Release Date
        date = searchResult.xpath('./a/div/div/div/div[1]/text()')[0]
        date_object = datetime.strptime(date, '%m/%d/%Y').strftime('%Y-%m-%d')
        metadata.originally_available_at = parse(date_object)
        metadata.year = metadata.originally_available_at.year

        # Genres
        movieGenres.clearGenres()
        movieActors.clearActors()

        # Actors
        movieActors.addActor('Aletta Ocean', '')

        # Posters
        art = []
        photoBaseURL = 'https://alettaoceanlive.com/tour/categories/photos_1_d.html'
        regex = re.compile(r'(?<=url\()[^\)]*')
        #Art URL
        art.append(regex.search(searchResult.xpath('@style')[0]).group())
        #Poster URL
        req = PAutils.HTTPRequest(photoBaseURL)
        photoPageElements = HTML.ElementFromString(req.text)
        pages = set(photoPageElements.xpath('//div[@class="global_pagination"]/ul/li/a/@href'))
        for link in pages:
            req = PAutils.HTTPRequest(link)
            searchPageElements = HTML.ElementFromString(req.text)
            searchResult = searchPageElements.xpath('//div[contains(@class, "photo-set-list-item")][contains(.,"%s")]/@style' % (title))
            if searchResult:
                break
            Log("Checking next page")
        searchResult = searchResult[0]
        art.append(regex.search(searchResult).group())

        for idx, posterUrl in enumerate(art, 1):
            if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
                # Download image file for analysis
                try:
                    image = PAutils.HTTPRequest(posterUrl)
                    im = StringIO(image.content)
                    resized_image = Image.open(im)
                    width, height = resized_image.size
                    # Add the image proxy items to the collection
                    if height > width:
                        # Item is a poster
                        metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                    if width > height:
                        # Item is an art item
                        metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                except:
                    pass
        Log("returning")
        return metadata