import re
import sys
import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchAll,searchSiteID):
    searchList = searchTitle.split(' ')
    res = []
    while len(res) == 0 and searchList:
        squery = '&query[]='.join(searchList)
        try:
#           print('https://www.peeonher.com/advanced-search/?search=search&condition=AND&query[]=' + squery)
           searchResults = HTML.ElementFromURL('https://www.peeonher.com/advanced-search/?search=search&condition=AND&query[]=' + squery)
           res = searchResults.xpath('//div[@class="item"]')
        except:
            pass
        searchList.pop(0)
        if not searchList and len(res) == 0:
            return results


    for searchResult in res:
        titleNoFormatting = searchResult.xpath('.//span[@class="desc"]/strong')[0].text_content()
        curID = searchResult.xpath('.//a[contains(@href,"/updates/")]')[0].get("href")
        curID = curID.replace('/','+')
        Log(str(curID))
        lowerResultTitle = str(titleNoFormatting).lower()
        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
        titleNoFormatting = titleNoFormatting + " [PeeOnHer]"
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
    return results



def update(metadata,siteID,movieGenres):
    Log('******UPDATE CALLED*******')
    temp = str(metadata.id).split("|")[0].replace('+','/')

    site =  PAsearchSites.getSearchBaseURL(siteID)
    detailsPageElements = HTML.ElementFromURL(site + temp)

    # Summary
    metadata.studio = "PissOnHer"
    paragraphs = detailsPageElements.xpath('//div[@class="update_box"]//div[@class="con_left"]')
    metadata.summary = paragraphs[0].text_content().strip()

    title = detailsPageElements.xpath('//div[@id="page"]//h1')[0].text_content().split('with', 2)
    metadata.title = title[0].strip()
    try:
      date = detailsPageElements.xpath('//div[@class="sub_sub_con"][2]')[0].text_content().splitlines()[-1].strip()
      date = re.sub(r'(\d)(st|nd|rd|th)', r'\1', date)
      date_object = datetime.strptime(date, '%d %B %Y')
      metadata.originally_available_at = date_object
      metadata.year = metadata.originally_available_at.year
    except:
        pass
    metadata.content_rating_age = 18
 
    # Genres
    movieGenres.clearGenres()
    # No Source for Genres, add manual
    try:
      max_tag = 0
      for it in detailsPageElements.xpath('//div[@class="sub_sub_con"][2]/a'):
          if max_tag < 20:
            movieGenres.addGenre(it.text_content())
            max_tag += 1
    except:
        pass


    # Actors
    metadata.roles.clear()
    actors = detailsPageElements.xpath('//div[@class="sub_sub_con"][1]/a')
    for actorLink in actors:
         role = metadata.roles.new()
         role.name = actorLink.text_content()
         role.photo = actorLink.xpath('./img')[0].get("src")

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

