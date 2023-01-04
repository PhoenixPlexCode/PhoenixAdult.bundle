import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    searchList = searchTitle.split(' ')
    res = []
    while len(res) == 0 and searchList:
        squery = '&query[]='.join(searchList)
        try:
#           print('https://www.wetandpissy.com/advanced-search/?search=search&condition=AND&query[]=' + squery)
           searchResults = HTML.ElementFromURL('https://www.wetandpissy.com/advanced-search/?search=search&condition=AND&query[]=' + squery)
           res = searchResults.xpath('//span[@class="title-movie"]/a[contains(@href,"videos/video")]')
        except:
            pass
        searchList.pop(0)
        if not searchList and len(res) == 0:
            return results


    for searchResult in res:
        titleNoFormatting = searchResult.text_content()
        curID = searchResult.get("href")
        curID = curID.replace('/','+')
        Log(str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
        titleNoFormatting = titleNoFormatting + " [WetAndPissy]"
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results



def update(metadata,siteID,movieGenres):
    Log('******UPDATE CALLED*******')
    temp = str(metadata.id).split("|")[0].replace('+','/')

#    site =  PAsearchSites.getSearchBaseURL(siteID)
    detailsPageElements = HTML.ElementFromURL(temp)

    # Summary
    metadata.studio = "WetAndPissy"
    paragraphs = detailsPageElements.xpath('//div[@class="movie-description"]')
    metadata.summary = paragraphs[0].text_content().strip()

    title = detailsPageElements.xpath('//div[@class="box-with-movies"]/section/div/h2')[0].text_content().split('in', 2)
    metadata.title = title[1].strip()
    date = detailsPageElements.xpath('//span[@class="date-movie"]/b')[0].text_content()
    date_object = datetime.strptime(date, '%b %d, %Y')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year
    metadata.content_rating_age = 18
 
    rating = detailsPageElements.xpath('//span[@id="current_rate"]')[0].text_content().split('/',2)
    try:
      metadata.rating = int(2*float(rating[0]))
    except:
        pass

    
    # Genres
    movieGenres.clearGenres()
    # No Source for Genres, add manual
    try:
      max_tag = 0
      for it in detailsPageElements.xpath('//div[@class="tags-box"]/ul/li/a'):
          if max_tag < 20:
            movieGenres.addGenre(it.text_content())
            max_tag += 1
    except:
        pass


    # Actors
    metadata.roles.clear()
    actors = detailsPageElements.xpath('//span[@class="model-movie"]/b/a')
    for actorLink in actors:
         role = metadata.roles.new()
         role.name = actorLink.text_content()
         actorPageURL = actorLink.get("href")
         actorPage = HTML.ElementFromURL(actorPageURL)
         actorPhotoURL = actorPage.xpath('//div[@class="image-wrapper-profile"]/img')
         actorPhotoURL = actorPhotoURL[0].get("src")
         role.photo = actorPhotoURL

    # Posters/Background
    valid_names = list()
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)
    poster = detailsPageElements.xpath('//video[@id="video"]')[0].get('poster')
#    background = detailsPageElements.xpath('//img[contains(@src,"/videos")]')[0].get("src")
#    metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
#    posterURL = poster[:-21] + "2.jpg"
#    metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL).content, sort_order = 1)
    metadata.posters[poster] = Proxy.Preview(HTTP.Request(poster).content, sort_order = 1)

    
    return metadata

