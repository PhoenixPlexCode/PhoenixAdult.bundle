import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    searchResults = HTML.ElementFromURL('https://www.girlsway.com/en/search/' + encodedTitle)

    for searchResult in searchResults.xpath('//div[@class="tlcTitle"]'):

        Log(searchResult.text_content())
        titleNoFormatting = searchResult.xpath('.//a')[0].get("title")
        curID = searchResult.xpath('.//a')[0].get("href")
        curID = curID.replace('/','_')
        Log(str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
        titleNoFormatting = titleNoFormatting + " [Girlsway]"
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results



def update(metadata,siteID,movieGenres):
    temp = str(metadata.id).split("|")[0].replace('_','/')

    url = PAsearchSites.getSearchBaseURL(siteID) + temp
    detailsPageElements = HTML.ElementFromURL(url)

    # Summary
    try:
        metadata.summary = detailsPageElements.xpath('//div[contains(@class,"sceneDesc")]')[0].text_content()[60:]
    except:
        metadata.summary = "No description"
    metadata.title = detailsPageElements.xpath('//h1[@class="title"]')[0].text_content()
    metadata.studio = "Girlsway"
    date = detailsPageElements.xpath('//div[@class="updatedDate"]')[0].text_content()[14:24]
    Log(date)
    date_object = datetime.strptime(date, '%Y-%m-%d')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year    
    
    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//div[contains(@class,"sceneColCategories")]//a')
    if len(genres) > 0:
        for genreLink in genres:
            genreName = genreLink.text_content().lower()
            movieGenres.addGenre(genreName)

    # Actors
    metadata.roles.clear()
    actors = detailsPageElements.xpath('//div[contains(@class,"sceneColActors")]//a')
    if len(actors) > 0:
        for actorLink in actors:
            role = metadata.roles.new()
            actorName = actorLink.text_content()
            role.name = actorName
            actorPageURL = "https://www.girlsway.com" + actorLink.get("href")
            actorPage = HTML.ElementFromURL(actorPageURL)
            actorPhotoURL = actorPage.xpath('//img[@class="actorPicture"]')[0].get("src")
            role.photo = actorPhotoURL
    
    # Posters/Background
    posterURL = detailsPageElements.xpath('//meta[@name="twitter:image"]')[0].get("content")
    Log("PosterURL: " + posterURL)
    metadata.art[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
    metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)    
    


    
    return metadata
