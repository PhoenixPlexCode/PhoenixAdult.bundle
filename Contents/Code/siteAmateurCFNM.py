import PAsearchSites
import PAgenres
import PAactors
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    if searchSiteID != 9999:
        siteNum = searchSiteID
        searchString = searchTitle .replace(" ","-").replace(",","").replace("'","").replace("?","").lower().strip() + ".html"
        Log("searchString " + searchString)
        searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + searchString)
    #modelsPageSortByLetter = PAsearchSites.getSearchSearchURL(siteNum) + searchTitle[:1] #here we get first letter of searchTitle
    #actorResults = HTML.ElementFromURL(modelsPageSortByLetter)
    #actorPage = actorResults.xpath('//a[contains(@href,"' + searchString + '")]')[0].get('href') # looking for our model
    #searchResults = HTML.ElementFromURL(actorPage) # scene search is carried out through the model page

        for searchResult in searchResults.xpath('.//div[@class="update_block"]'):
            titleNoFormatting = searchResult.xpath('.//span[@class="update_title"]')[0].text_content().strip()
            #sceneUrl = searchResult.xpath('.//a')[0].get('href')
            curID = searchResult.xpath('.//a')[0].get('href').split('?')[0]
            #scenePage = HTML.ElementFromURL(sceneUrl) # geting releaseDate from scene page
            releaseDate = parse(searchResults.xpath('.//span[@class="update_date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
            score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
            #if searchDate:
                #score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
            #else:
                #score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting + " [" + PAsearchSites.getSearchSiteName(siteNum) + "] " + releaseDate, score = score, lang = lang))
    return results

def update(metadata,siteID,movieGenres,movieActors):
    #Log('******UPDATE METADATA CALLED*******')
    #url = PAsearchSites.getSearchBaseURL(siteID) + searchString #PAsearchSites.getSearchBaseURL(siteID) + str(metadata.id).split("|")[0].replace('_','/').replace('!','_')
    #Log("scene url: " + url)
    #detailsPageElements = HTML.ElementFromURL(url)

    detailsPageElements = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + searchString + ".html")

    # Studio/Tagline/Collection
    metadata.studio = AmateurCFNM
    metadata.tagline = metadata.studio
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)

    # Date
    date = str(metadata.id).split("|")[2]
    Log('date: ' + date)
    date_object = datetime.strptime(date.strip(), '%Y-%m-%d')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Summary
    metadata.summary = detailsPageElements.xpath('//p[@class="text"]')[0].text_content()
    Log('summary: ' +  metadata.summary)

    # Posters/Background
    valid_names = list()
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)
    try:
        posters = detailsPageElements.xpath('//div[@id="video-set-details"]//video[@id="video-playback"]')
        background = posters[0].get("poster")
    except:
        background = detailsPageElements.xpath('//img[@class="poster"] | //img[@class="cover"]')[0].get('src')
    Log("background: " + background)
    metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
    metadata.posters[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//h2[@class="starring-models"]/a')
    if len(actors) > 0:
        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            actorPhotoURL = ''
            movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    movieGenres.addGenre("Glamcore")
    movieGenres.addGenre("Artistic")
    if len(actors) == 3:
        movieGenres.addGenre("Threesome")
    if len(actors) == 4:
        movieGenres.addGenre("Foursome")
    if len(actors) > 4:
        movieGenres.addGenre("Orgy")


    # TITLE
    metadata.title = detailsPageElements.xpath('//h1[@class="title"]')[0].text_content().title().strip()

    return metadata


#def update(metadata,siteID,movieGenres,movieActors):
#    Log('******UPDATE CALLED*******')
#
#    pageURL = PAsearchSites.getSearchBaseURL(siteID) + searchString
#    Log('scene url: ' + pageURL)
#    detailsPageElements = HTML.ElementFromURL(pageURL)
    # art = []
    
    # Summary
#    siteName = PAsearchSites.getSearchSiteName(siteID)
#    metadata.studio = siteName
#    try:
#        metadata.summary = detailsPageElements.xpath('//div[@class="latest_update_description"]')[0].text_content().strip()
#        metadata.title = detailsPageElements.xpath('.//span[@class="update_title"]')[0].text_content().strip()
#    except:
#        pass

    # Director
#    metadata.directors.clear()
#    director = metadata.directors.new()
#    director.name = "Charlie"

    # Collections / Tagline
#    metadata.collections.clear()
#    metadata.tagline = siteName
#    metadata.collections.add(siteName)

    # Genres
#    try:
#        genres = detailsPageElements.xpath('//dd[2]')
#        if len(genres) > 0:
#            for genreLink in genres:
#                genreName = genreLink.text_content().strip().lower()
#                Log("Genre for >" + metadata.title + "<: " + genreName)
#                movieGenres.addGenre('CFNM')
#    except:
#        pass

    # Release Date
#    try:
#        date = detailsPageElements.xpath('//span[@class="update_date"]')
#        if len(date) > 0:
#            date = date[0].text_content().strip()
#            date_object = parse(date)
#            metadata.originally_available_at = date_object
#            metadata.year = metadata.originally_available_at.year
#    except:
#        pass

    # Actors
#    movieActors.clearActors()

#    actors = detailsPageElements.xpath('//dd[1]')
#    if len(actors) > 0:
#        for actorLink in actors:
#            actorName = actorLink.xpath('.//a[1]')[0].text_content().strip()
#            actorPhotoURL = actorLink.xpath('.//a[2]//img')[0].get('src')
#            movieActors.addActor(actorName,actorPhotoURL)
#            try:
#                actorName = actorLink.xpath('.//a[3]')[0].text_content().strip()
#                actorPhotoURL = actorLink.xpath('.//a[4]//img')[0].get('src')
#                movieActors.addActor(actorName, actorPhotoURL)
#            except:
#                pass

    # Posters/Background
#    posters = HTML.ElementFromURL(detailsPageElements.xpath('//dd[1]//a')[0].get('href'))

#    for poster in posters.xpath('//a[contains(@href,"' + pageURL + '")]//img'):
#        posterUrl = poster.get('src')
#        Log("DownLoad Posters/Arts: " + posterUrl)
#        if len(posterUrl) > 0:
#            art.append(posterUrl)

#    j = 1
#    Log("Artwork found: " + str(len(art)))
#    for posterUrl in art:
#        if not PAsearchSites.posterAlreadyExists(posterUrl,metadata):
            #Download image file for analysis
#            try:
#                img_file = urllib.urlopen(posterUrl)
#                im = StringIO(img_file.read())
#                resized_image = Image.open(im)
#                width, height = resized_image.size
                #Add the image proxy items to the collection
#                if width > 1 or height > width:
                    # Item is a poster
#                    metadata.posters[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
#                if width > 100 and width > height:
#                    # Item is an art item
#                    metadata.art[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
#                j = j + 1
#            except:
#                pass


#    return metadata