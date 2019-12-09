import PAsearchSites
import PAgenres
import PAactors
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    if searchSiteID != 9999:
        siteNum = searchSiteID
    searchString = searchTitle .replace(" ","-").replace(",","").replace("'","").replace("?","").lower().strip() + ".html"
    Log("searchString " + searchString)
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + searchString)
    for searchResult in searchResults.xpath('//div[@class="update_block"]'):
        titleNoFormatting = searchResult.xpath('.//span[@class="update_title"]')[0].text_content().strip()
        releaseDate = parse(searchResults.xpath('.//span[@class="update_date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
        actorResults = searchResult.xpath('.//span[@class="tour_update_models"]')[0].text_content().strip()
        Log("Actor - " + actorResults)
        curID = titleNoFormatting
        realURL = (PAsearchSites.getSearchSearchURL(siteNum) + searchString) #.replace('/','_').replace('?','!')
        Log("RealURL " + realURL)
        summary = searchResult.xpath('.//span[@class="latest_update_description"]')[0].text_content().strip()
        score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum) + "|" + realURL + "|" + releaseDate + "|" + summary + "|" + actorResults, name = titleNoFormatting + " [AmateurCFNM] " + releaseDate, score = score, lang = lang))
    return results


#def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
#    if searchSiteID != 9999:
#        siteNum = searchSiteID
#        searchString = searchTitle .replace(" ","-").replace(",","").replace("'","").replace("?","").lower().strip() + ".html"
#        Log("searchString " + searchString)
#        searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + searchString)
        #modelsPageSortByLetter = PAsearchSites.getSearchSearchURL(siteNum) + searchTitle[:1] #here we get first letter of searchTitle
    #actorResults = HTML.ElementFromURL(modelsPageSortByLetter)
    #actorPage = actorResults.xpath('//a[contains(@href,"' + searchString + '")]')[0].get('href') # looking for our model
    #searchResults = HTML.ElementFromURL(actorPage) # scene search is carried out through the model page

#        for searchResult in searchResults.xpath('//div[@class="update_block"]'):
#            titleNoFormatting = searchResult.xpath('.//span[@class="update_title"]')[0].text_content().strip()
#            actorGrab = searchResult.xpath('.//span[@class="tour_update_models"]')[0].text_content().strip() 
#            Log('actorName: ' + actorName)           
#            releaseDate = parse(searchResults.xpath('.//span[@class="update_date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
#            curID = titleNoFormatting
#            Log('CurID: ' + curID)
            #sceneUrl = searchResult.xpath('.//a')[0].get('href')
            #scenePage = HTML.ElementFromURL(sceneUrl) # geting releaseDate from scene page
#            score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
            #if searchDate:
                #score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
            #else:
                #score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
#            results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), actorName = actorGrab + name = titleNoFormatting + " [" + PAsearchSites.getSearchSiteName(siteNum) + "] " + releaseDate, score = score, lang = lang))
#        return results

def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE METADATA CALLED*******')
    url = str(metadata.id).split("|")[2].replace('_','/').replace('!','?')
    detailsPageElements = HTML.ElementFromURL(url)
    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'AmateurCFNM'
    metadata.tagline = metadata.studio
    metadata.collections.clear()
    metadata.collections.add(metadata.studio)

    # Title
    metadata.title = detailsPageElements.xpath('//span[@class="update_title"]')[0].text_content().title().strip()

    # Release Date
    try:
        date = str(metadata.id).split("|")[3]
        if len(date) > 0:
            date_object = parse(date)
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year
            Log("Date from file")
    except:
        pass

    # Summary
    try:
        metadata.summary = str(metadata.id).split("|")[4]
    except:
        pass

    # Posters/Background
    valid_names = list()
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)
    try:
        posters = url + detailsPageElements.xpath('//img[@class="small_update_thumb left thumbs stdimage"]') #//video[@id="video-playback"]
        background = posters[0].get("poster")
    except:
        background = url + detailsPageElements.xpath('//img[@class="large_update_thumb left thumbs stdimage"] | //img[@class="cover"]')[0].get('src')
    Log("background: " + background)
    metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
    metadata.posters[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)

    # Actors
    movieActors.clearActors()
    actors = metadata.summary = str(metadata.id).split("|")[5]
    if len(actors) > 0:
        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            actorPhotoURL = ''
            movieActors.addActor(actorName, actorPhotoURL)

    # Genres
    movieGenres.clearGenres()
    movieGenres.addGenre("CFNM")
    if len(actors) == 3:
        movieGenres.addGenre("Threesome")
    if len(actors) == 4:
        movieGenres.addGenre("Foursome")
    if len(actors) > 4:
        movieGenres.addGenre("Orgy")

    return metadata


#def update(metadata,siteID,movieGenres,movieActors):
#    Log('******UPDATE METADATA CALLED*******')
    #url = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteID) + searchString) #PAsearchSites.getSearchBaseURL(siteID) + str(metadata.id).split("|")[0].replace('_','/').replace('!','_')
#    url = PAsearchSites.getSearchSearchURL(siteID) + str(metadata.actorName).split("|")[0].replace(' ','-') + ".html"
#    Log("scene url: " + url)
#    detailsPageElements = HTML.ElementFromURL(url)

    #detailsPageElements = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteID) + searchString + ".html")

    # Studio/Tagline/Collection
#    metadata.studio = AmateurCFNM
#    metadata.tagline = metadata.studio
#    metadata.collections.clear()
#    metadata.collections.add(metadata.studio)

    # Date
#    date = str(metadata.id).split("|")[2]
#    Log('date: ' + date)
#    date_object = datetime.strptime(date.strip(), '%Y-%m-%d')
#    metadata.originally_available_at = date_object
#    metadata.year = metadata.originally_available_at.year

    # Summary
#    metadata.summary = detailsPageElements.xpath('//p[@class="text"]')[0].text_content()
#    Log('summary: ' +  metadata.summary)
