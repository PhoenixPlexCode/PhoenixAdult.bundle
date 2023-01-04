import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    ix = encodedTitle.find('Video')    
    res = []
    if ix >= 0:
        encodedTitle = encodedTitle[ix+8:]
        searchResults = HTML.ElementFromURL('https://www.vipissy.com/updates/?search=' + encodedTitle)
        res = searchResults.xpath('//a[contains(@href,"updates/video") and @class="image-wrapper"]')
    if ix == -1 or len(res) == 0:
        while len(res) == 0 and encodedTitle:
           try:
             searchResults = HTML.ElementFromURL('https://www.vipissy.com/updates/?search=' + encodedTitle)
             res = searchResults.xpath('//a[contains(@href,"updates/video") and @class="image-wrapper"]')
           except:
               pass
           en = encodedTitle.split('%20', 1)
           print(en)
           if len(en) > 1:
               encodedTitle = en[1]
           elif len(res) == 0:
               return results


    for searchResult in res:
        titleNoFormatting = searchResult.get("title")
        curID = searchResult.get("href")
        curID = curID.replace('/','+')
        Log(str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
        titleNoFormatting = titleNoFormatting + " [Wipissy]"
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results



def update(metadata,siteID,movieGenres):
    Log('******UPDATE CALLED*******')
    temp = str(metadata.id).split("|")[0].replace('+','/')

    site =  PAsearchSites.getSearchBaseURL(siteID)
    detailsPageElements = HTML.ElementFromURL(site + temp)

    # Summary
    metadata.studio = "Wipissy"
    paragraphs = detailsPageElements.xpath('//div[contains(@class, "show_more")]')
    metadata.summary = paragraphs[0].text_content().strip()

    title = detailsPageElements.xpath('//section/strong')[0].text_content()    
    metadata.title = title[title.find('—')+1:].strip()
    date = detailsPageElements.xpath('//section/dl/dd[contains(text(), ", 20")]')[0].text_content()
    date_object = datetime.strptime(date, '%b %d, %Y')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year
    metadata.content_rating_age = 18
 
    rating = detailsPageElements.xpath('//section/dl/dd[4]')[0].text_content().strip()
    try:
      metadata.rating = int(rating[0])
    except:
        pass

    
    # Genres
    movieGenres.clearGenres()
    # No Source for Genres, add manual
    try:
      max_tag = 0
      for it in detailsPageElements.xpath('//p[@class="tags"]/a'):
          if max_tag < 20:
            movieGenres.addGenre(it.text_content())
            max_tag += 1
    except:
        pass


    # Actors
    metadata.roles.clear()
    actors = detailsPageElements.xpath('//section/dl/dd[1]/a')
    for actorLink in actors:
         role = metadata.roles.new()
         role.name = actorLink.text_content()
         actorPageURL = actorLink.get("href")
         actorPage = HTML.ElementFromURL(site + actorPageURL)
         actorPhotoURL = actorPage.xpath('//img[contains(@alt, "Pornstar")]')
         actorPhotoURL = actorPhotoURL[0].get("src")#.split('?')[0]
         role.photo = actorPhotoURL

    # Posters/Background
    valid_names = list()
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)
    poster = detailsPageElements.xpath('//div[@id="videoplayer"]/video')[0].get('poster')
#    background = detailsPageElements.xpath('//img[contains(@src,"/videos")]')[0].get("src")
#    metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
#    posterURL = poster[:-21] + "2.jpg"
#    metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL).content, sort_order = 1)
    metadata.posters[poster] = Proxy.Preview(HTTP.Request(poster).content, sort_order = 1)

    
    return metadata

