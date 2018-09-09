import re
import random
import urllib
import urllib2 as urllib
import urlparse
import json
from datetime import datetime
from PIL import Image
from cStringIO import StringIO

VERSION_NO = '2.2018.09.08.1'

def any(s):
    for v in s:
        if v:
            return True
    return False

def Start():
    HTTP.ClearCache()
    HTTP.CacheTime = CACHE_1MINUTE*20
    HTTP.Headers['User-agent'] = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)'
    HTTP.Headers['Accept-Encoding'] = 'gzip'

def capitalize(line):
    return ' '.join([s[0].upper() + s[1:] for s in line.split(' ')])

def tagAleadyExists(tag,metadata):
    for t in metadata.genres:
        if t.lower() == tag.lower():
            return True
    return False

def posterAlreadyExists(posterUrl,metadata):
    for p in metadata.posters.keys():
        Log(p.lower())
        if p.lower() == posterUrl.lower():
            Log("Found " + posterUrl + " in posters collection")
            return True

    for p in metadata.art.keys():
        if p.lower() == posterUrl.lower():
            return True
    return False
searchSites = [None] * 54
searchSites[1] = ["Blacked com","Blacked","https://www.blacked.com","https://www.blacked.com/search?q="]
searchSites[0] = ["Blackedraw com","BlackedRaw","https://www.blackedraw.com","https://www.blackedraw.com/search?q="]
searchSites[2] = ["Brazzers.com","Brazzers","http://www.brazzers.com","http://www.brazzers.com/search/all/?q="]
searchSites[4] = ["Blacked","Blacked","https://www.blacked.com","https://www.blacked.com/search?q="]
searchSites[3] = ["Blackedraw","BlackedRaw","https://www.blackedraw.com","https://www.blackedraw.com/search?q="]
searchSites[5] = ["My Friends Hot Mom","My Friends Hot Mom","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[6] = ["My First Sex Teacher","My First Sex Teacher","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[7] = ["Seduced By A Cougar","Seduced By A Cougar","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[8] = ["My Daughters Hot Friend","My Daughters Hot Friend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[9] = ["My Wife is My Pornstar","My Wife is My Pornstar","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[10] = ["Tonights Girlfriend Class","Tonights Girlfriend Class","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[11] = ["Wives on Vacation","Wives on Vacation","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[12] = ["My Sisters Hot Friend","My Sisters Hot Friend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[13] = ["Naughty Weddings","Naughty Weddings","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[14] = ["Dirty Wives Club","Dirty Wives Club","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[15] = ["My Dads Hot Girlfriend","My Dads Hot Girlfriend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[16] = ["My Girl Loves Anal","My Girl Loves Anal","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[17] = ["Lesbian Girl on Girl","Lesbian Girl on Girl","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[18] = ["Naughty Office","Naughty Office","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[19] = ["I have a Wife","I have a Wife","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[20] = ["Naughty Bookworms","Naughty Bookworms","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[21] = ["Housewife 1 on 1","Housewife 1 on 1","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[22] = ["My Wifes Hot Friend","My Wifes Hot Friend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[23] = ["Latin Adultery","Latin Adultery","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[24] = ["Ass Masterpiece","Ass Masterpiece","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[25] = ["2 Chicks Same Time","2 Chicks Same Time","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[26] = ["My Friends Hot Girl","My Friends Hot Girl","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[27] = ["Neighbor Affair","Neighbor Affair","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[28] = ["My Girlfriends Busty Friend","My Girlfriends Busty Friend","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[29] = ["Naughty Athletics","Naughty Athletics","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[30] = ["My Naughty Massage","My Naughty Massage","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[31] = ["Fast Times","Fast Times","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[32] = ["The Passenger","The Passenger","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[33] = ["Milf Sugar Babes Classic","Milf Sugar Babes Classic","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[34] = ["Perfect Fucking Strangers Classic","Perfect Fucking Strangers Classic","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[35] = ["Asian 1 on 1","Asian 1 on 1","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[36] = ["American Daydreams","American Daydreams","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[37] = ["SoCal Coeds","SoCal Coeds","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[38] = ["Naughty Country Girls","Naughty Country Girls","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[39] = ["Diary of a Milf","Diary of a Milf","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[40] = ["Naughty Rich Girls","Naughty Rich Girls","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[41] = ["My Naughty Latin Maid","My Naughty Latin Maid","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[42] = ["Naughty America","Naughty America","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[43] = ["Diary of a Nanny","Diary of a Nanny","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[44] = ["Naughty Flipside","Naughty Flipside","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[45] = ["Live Party Girl","Live Party Girl","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[46] = ["Live Naughty Student","Live Naughty Student","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[47] = ["Live Naughty Secretary","Live Naughty Secretary","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[48] = ["Live Gym Cam","Live Gym Cam","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[49] = ["Live Naughty Teacher","Live Naughty Teacher","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[50] = ["Live Naughty Milf","Live Naughty Milf","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[51] = ["Live Naughty Nurse","Live Naughty Nurse","https://tour.naughtyamerica.com","https://tour.naughtyamerica.com/search?term="]
searchSites[52] = ["Vixen","Vixen","https://www.vixen.com","https://www.vixen.com/search?q="]
searchSites[53] = ["Girlsway","Girlsway","https://www.girlsway.com","https://www.girlsway.com/en/search/"]
def getSearchBaseURL(siteID):
    return searchSites[siteID][2]
def getSearchSearchURL(siteID):
    return searchSites[siteID][3]
def getSearchFilter(siteID):
    return searchSites[siteID][0]
def getSearchSiteName(siteID):
    return searchSites[siteID][1]
def getSearchSiteIDByFilter(searchFilter):
    searchID = 0
    for sites in searchSites:
        if sites[0].lower() in searchFilter.lower().replace("."," "):
            return searchID
        searchID += 1
    return 9999
def getSearchSettings(mediaTitle):
    mediaTitle = mediaTitle.replace(".", " ")
    mediaTitle = mediaTitle.replace(" - ", " ")
    mediaTitle = mediaTitle.replace("-", " ")
    # Search Site ID or -1 is all
    searchSiteID = None
    # Date/Actor or Title
    searchType = None
    # What to search for
    searchTitle = None
    # Date search
    searchDate = None
    # Actors search
    searchActors = None

    # Remove Site from Title
    searchSiteID = getSearchSiteIDByFilter(mediaTitle)
    Log("^^^^^^^" + str(searchSiteID))
    if searchSiteID != 9999:
        Log("^^^^^^^ Shortening Title")
        if mediaTitle[:len(searchSites[searchSiteID][0])].lower() == searchSites[searchSiteID][0].lower():
            searchTitle = mediaTitle[len(searchSites[searchSiteID][0])+1:]
        else:
            searchTitle = mediaTitle
    else:
        searchTitle = mediaTitle

    #Search Type
    if unicode(searchTitle[:4], 'utf-8').isnumeric():
        if unicode(searchTitle[5:7], 'utf-8').isnumeric():
            if unicode(searchTitle[8:10], 'utf-8').isnumeric():
                searchType = 1
                searchDate = searchTitle[0:10].replace(" ","-")
                searchTitle = searchTitle[11:]
            else:
                searchType = 0
        else:
            searchType = 0
    else:
        searchType = 0

    return [searchSiteID,searchType,searchTitle,searchDate]

    

class EXCAgent(Agent.Movies):
    name = 'PhoenixAdult'
    languages = [Locale.Language.English]
    accepts_from = ['com.plexapp.agents.localmedia']
    primary_provider = True

    def search(self, results, media, lang):
        title = media.name
        if media.primary_metadata is not None:
            title = media.primary_metadata.title
        title = title.replace('"','').replace("'","").replace(":","")
        Log('*******MEDIA TITLE****** ' + str(title))

        # Search for year
        year = media.year
        if media.primary_metadata is not None:
            year = media.primary_metadata.year

        Log("Getting Search Settings for: " + title)
        searchSettings = getSearchSettings(title)
        if searchSettings[0] == 9999:
            searchAll = True
        else:
            searchAll = False
            searchSiteID = searchSettings[0]
            if searchSiteID == 3:
                searchSiteID = 0
            if searchSiteID == 4:
                searchSiteID = 1
        searchTitle = searchSettings[2]
        Log("Site ID: " + str(searchSettings[0]))
        Log("Search Title: " + searchSettings[2])
        if searchSettings[1]:
            searchByDateActor = True
            searchDate = searchSettings[3]
            Log("Search Date: " + searchSettings[3])
        else:
            searchByDateActor = False

        encodedTitle = urllib.quote(searchTitle)
        Log(encodedTitle)

        siteNum = 0
        for searchSite in searchSites:
            ###############
            ## Blacked and Blacked Raw Search
            ###############
            if siteNum == 0 or siteNum == 1:
                if searchAll or searchSiteID == 0 or searchSiteID == 1:
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle)
                    for searchResult in searchResults.xpath('//article[@class="videolist-item"]'):
                        
                        
                        Log(searchResult.text_content())
                        titleNoFormatting = searchResult.xpath('.//h4[@class="videolist-caption-title"]')[0].text_content()
                        Log("Result Title: " + titleNoFormatting)
                        curID = searchResult.xpath('.//a[@class="videolist-link ajaxable"]')[0].get('href')
                        curID = curID.replace('/','_')
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//div[@class="videolist-caption-date"]')[0].text_content()

                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))


            ###############
            ## Brazzers
            ###############
            if siteNum == 2:
                if searchAll or searchSiteID == 2:
                    searchResults = HTML.ElementFromURL('http://www.brazzers.com/search/all/?q=' + encodedTitle)
                    for searchResult in searchResults.xpath('//h2[contains(@class,"scene-card-title")]//a'):
                        Log(str(searchResult.get('href')))
                        titleNoFormatting = searchResult.get('title')
                        curID = searchResult.get('href').replace('/','_')
                        lowerResultTitle = str(titleNoFormatting).lower()
                        score = 100 - Util.LevenshteinDistance(title.lower(), titleNoFormatting.lower())
                        
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting + " [Brazzers]", score = score, lang = lang))
                            
            ###############
            ## Naughty America
            ###############
            if siteNum == 5:
                if searchAll or (searchSiteID >= 5 and searchSiteID <= 51): 
                    searchString = encodedTitle.replace(" ","+")
                    if not searchAll:
                        searchString = searchString + "+in+" + getSearchSiteName(searchSiteID).replace(" ","+")
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + searchString)
                    for searchResult in searchResults.xpath('//div[@class="scene-item"]'):
                        titleNoFormatting = searchResult.xpath('.//a')[0].get("title")
                        Log("Result Title: " + titleNoFormatting)
                        curID = searchResult.xpath('.//a')[0].get('href')
                        curID = curID[31:-26]
                        curID = curID.replace('/','_')
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//p[@class="entry-date"]')[0].text_content()

                        Log("CurID" + str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        searchString = searchString.replace("+"," ")
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchString.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%b %d, %y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [NA, " + releasedDate +"]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))

            siteNum += 1
            ###############
            ## Vixen
            ###############
            if siteNum == 52:
                if searchAll or searchSiteID == 52:
                    searchResults = HTML.ElementFromURL(getSearchSearchURL(siteNum) + encodedTitle)
                    for searchResult in searchResults.xpath('//article[@class="videolist-item"]'):
                        
                        
                        Log(searchResult.text_content())
                        titleNoFormatting = searchResult.xpath('.//h4[@class="videolist-caption-title"]')[0].text_content()
                        Log("Result Title: " + titleNoFormatting)
                        curID = searchResult.xpath('.//a[@class="videolist-link ajaxable"]')[0].get('href')
                        curID = curID.replace('/','_')
                        Log("ID: " + curID)
                        releasedDate = searchResult.xpath('.//div[@class="videolist-caption-date"]')[0].text_content()

                        Log(str(curID))
                        lowerResultTitle = str(titleNoFormatting).lower()
                        if searchByDateActor != True:
                            score = 102 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                        else:
                            searchDateCompare = datetime.strptime(searchDate, '%Y-%m-%d').strftime('%B %d, %y')
                            score = 102 - Util.LevenshteinDistance(searchDateCompare.lower(), releasedDate.lower())
                        titleNoFormatting = titleNoFormatting + " [" + searchSites[siteNum][1] + ", " + releasedDate + "]"
                        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting, score = score, lang = lang))
                
            ###############
            ## Girlsway
            ###############
            if siteNum == 53:
                if searchAll or searchSiteID == 53:
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
                
        results.Sort('score', descending=True)

    def update(self, metadata, media, lang):

        Log('******UPDATE CALLED*******')
        
        siteID = int(str(metadata.id).split("|")[1])
        Log(str(siteID))
        ##############################################################
        ##                                                          ##
        ##   Blacked                                                ##
        ##                                                          ##
        ##############################################################
        if siteID == 1:
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Blacked"
            paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph
            metadata.title = detailsPageElements.xpath('//h1[@id="castme-title"]')[0].text_content()
            date = detailsPageElements.xpath('//span[@class="player-description-detail"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            metadata.genres.clear()
            # No Source for Genres, add manual
            metadata.genres.add("Interracial")
            metadata.genres.add("Hardcore")
            metadata.genres.add("Heterosexual")


            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//p[@id="castme-subtitle"]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL("https://www.blacked.com"+actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="thumb-img"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//div[@class="swiper-slide"]')
            background = detailsPageElements.xpath('//img[contains(@class,"player-img")]')[0].get("src")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)

            posterNum = 1
            for posterCur in posters:
                posterURL = posterCur.xpath('.//img[@class="swiper-content-img"]')[0].get("src")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1

        ##############################################################
        ##                                                          ##
        ##   Blacked Raw                                            ##
        ##                                                          ##
        ##############################################################
        if siteID == 0:
            Log('******UPDATE CALLED*******')
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Blacked Raw"
            paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph
            metadata.title = detailsPageElements.xpath('//div[@id="castme-title"]')[0].text_content()
            date = detailsPageElements.xpath('//span[@class="right"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            metadata.genres.clear()
            # No Source for Genres, add manual
            metadata.genres.add("Interracial")
            metadata.genres.add("Hardcore")
            metadata.genres.add("Heterosexual")


            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//span[@id="castme-subtitle"]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(getSearchBaseURL(siteID)+actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="thumb-img"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//div[@class="swiper-slide"]')
            background = detailsPageElements.xpath('//img[contains(@class,"player-img")]')[0].get("src")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
            posterNum = 1
            for posterCur in posters:
                posterURL = posterCur.xpath('.//img[@class="swiper-content-img"]')[0].get("src")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1
        
        
        ##############################################################
        ##                                                          ##
        ##   Brazzers                                               ##
        ##                                                          ##
        ##############################################################
        if siteID == 2:
            Log('******UPDATE CALLED*******')
            zzseries = False
            metadata.studio = 'Brazzers'
            temp = str(metadata.id).split("|")[0].replace('_','/')
            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            paragraph = detailsPageElements.xpath('//p[@itemprop="description"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph[:-10]
            tagline = detailsPageElements.xpath('//span[@class="label-text"]')[0].text_content()
            if tagline == 'ZZ Series':
                zzseries = False
            metadata.tagline = str(tagline)
            metadata.collections.add(tagline)
            metadata.title = detailsPageElements.xpath('//h1')[0].text_content()

            # Genres
            metadata.genres.clear()
            genres = detailsPageElements.xpath('//div[contains(@class,"tag-card-container")]//a')
            genreFilter=[]
            if Prefs["excludegenre"] is not None:
                Log("exclude")
                genreFilter = Prefs["excludegenre"].split(';')

            genreMaps=[]
            genreMapsDict = {}

            if Prefs["tagmapping"] is not None:
                genreMaps = Prefs["tagmapping"].split(';')
                for mapping in genreMaps:
                    keyVal = mapping.split("=")
                    genreMapsDict[keyVal[0]] = keyVal[1].lower()
            else:
                genreMapsDict = None

            if len(genres) > 0:
                for genreLink in genres:
                    genreName = genreLink.text_content().strip('\n').lower()
                    if any(genreName in g for g in genreFilter) == False:
                        if genreMapsDict is not None:
                            if genreName in genreMapsDict:
                                if not tagAleadyExists(genreMapsDict[genreName],metadata):
                                    metadata.genres.add(capitalize(genreMapsDict[genreName]))
                            else:
                                if not tagAleadyExists(genreName,metadata):
                                    metadata.genres.add(capitalize(genreName))
                        else:
                            metadata.genres.add(capitalize(genreName))

            if not zzseries:
                date = detailsPageElements.xpath('//aside[contains(@class,"scene-date")]')[0].text_content()
                date_object = datetime.strptime(date, '%B %d, %Y')
                metadata.originally_available_at = date_object
                metadata.year = metadata.originally_available_at.year
            else:
                for wrapper in detailsPageElements.xpath('//div[@class="release-card-wrap"]'):
                    Log('wrapper')
                    cardTitle = wrapper.xpath('.//div[@class="card-image"]//a')[0].get('title')
                    Log(cardTitle)
                    if cardTitle.lower() == metadata.title.lower():
                        Log('match')
                        date = detailsPageElements.xpath('..//time')[0].text_content()
                        date_object = datetime.strptime(date, '%B %d, %Y')
                        metadata.originally_available_at = date_object
                        metadata.year = metadata.originally_available_at.year 
                        metadata.roles.clear()
                        metadata.collections.clear()
                        starring = wrapper.xpath('.//div[@class="model-names"]//a')
                        for member in starring:
                            role = metadata.roles.new()
                            role.actor = member.get('title').strip()
                            metadata.collections.add(member.get('title').strip())
                        p = wrapper.xpath('.//div[@class="card-image"]//img')[0].get('src')
                        Log(p)
                        metadata.posters[p] = Proxy.Preview(HTTP.Request(p, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
                            
            # Starring/Collection
            # Create a string array to hold actors
            maleActors=[]
            
            # Refresh the cache every 50th query
            if('cache_count' not in Dict):
                Dict['cache_count'] = 0
                Dict.Save()
            else:
                cache_count = float(Dict['cache_count'])
                
            
            if('actors' not in Dict):
                Log('******NOT IN DICT******')
                maleActorHtml = None
                #maleActorHtml = HTML.ElementFromURL('http://www.data18.com/sys/get3.php?t=2&network=1&request=/sites/brazzers/')

                # Add missing actors
                Dict.Save()
            else:
                Log('******IN DICT******')
                maleActors = Dict['actors']

            if Prefs['excludeactor'] is not None:
                addActors = Prefs['excludeactor'].split(';')
                for a in addActors:
                    maleActors.append(a)
        
            #starring = None
            if not zzseries:
                metadata.roles.clear()
                #metadata.collections.clear()
                #starring = detailsPageElements.xpath('//p[contains(@class,"related-model")]//a')
                starring = detailsPageElements.xpath('//div[@class="model-card"]//a')
                memberSceneActorPhotos = detailsPageElements.xpath('//img[contains(@class,"lazy card-main-img")]')
                memberSceneActorPhotos_TotalNum = len(memberSceneActorPhotos)
                memberTotalNum = len(starring)/2
                Log('----- Number of Actors: ' +str(memberTotalNum) + ' ------')
                Log('----- Number of Photos: ' +str(memberSceneActorPhotos_TotalNum) + ' ------')
                
                memberNum = 0
                for memberCard in starring:
                    # Check if member exists in the maleActors list as either a string or substring
                    #if any(member.text_content().strip() in m for m in maleActors) == False:
                        role = metadata.roles.new()
                        # Add to actor and collection
                        #role.name = "Test"
                        role.role = "Porn Star"
                        memberName = memberCard.xpath('//h2[contains(@class,"model-card-title")]//a')[memberNum]
                        memberPhoto = memberCard.xpath('//img[@class="lazy card-main-img" and @alt="'+memberName.text_content().strip()+'"]')[0].get('data-src')
                        role.name = memberName.text_content().strip()
                        memberNum = memberNum + 1
                        memberNum = memberNum % memberTotalNum
                        Log('--------- Photo   ---------- : ' + memberPhoto)
                        role.photo = "http:" + memberPhoto.replace("model-medium.jpg","model-small.jpg")
                        metadata.collections.add(memberName.text_content().strip())

                detailsPageElements.xpath('//h1')[0].text_content()

            #Posters
            if not zzseries:
                i = 1
                background = "http:" + detailsPageElements.xpath('//*[@id="trailer-player"]/img')[0].get('src')
                Log("BG DL: " + background)
                metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
                for poster in detailsPageElements.xpath('//a[@rel="preview"]'):
                    posterUrl = "http:" + poster.get('href').strip()
                    thumbUrl = "http:" + detailsPageElements.xpath('//img[contains(@data-src,"thm")]')[i-1].get('data-src')
                    if not posterAlreadyExists(posterUrl,metadata):            
                        #Download image file for analysis
                        img_file = urllib.urlopen(posterUrl)
                        im = StringIO(img_file.read())
                        resized_image = Image.open(im)
                        width, height = resized_image.size
                        #posterUrl = posterUrl[:-6] + "01.jpg"
                        #Add the image proxy items to the collection
                        if(width > 1):
                            # Item is a poster
                            
                            metadata.posters[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = i)
                        if(width > 100):
                            # Item is an art item
                            metadata.art[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = i+1)
                        i = i + 1
                
        ##############################################################
        ##                                                          ##
        ##   Naughty America                                        ##
        ##                                                          ##
        ##############################################################        
        if siteID >= 5 and siteID <= 51:
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Naughty America"
            #paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            #paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = detailsPageElements.xpath('//p[@class="synopsis_txt"]')[0].text_content()
            site = detailsPageElements.xpath('//a[@class="site-title grey-text"]')[0].text_content()
            metadata.title = " in " + site
            date = detailsPageElements.xpath('//p[@class="scenedate"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%b %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            # Actors
            metadata.roles.clear()
            titleActors = ""
            actors = detailsPageElements.xpath('//a[@class="scene-title grey-text"]')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    titleActors = titleActors + actorName + " & "
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL(actorPageURL)
                    actorPhotoURL = "http:" + actorPage.xpath('//img[@class="performer-pic"]')[0].get("src")
                    role.photo = actorPhotoURL
                titleActors = titleActors[:-3]
                metadata.title = titleActors + metadata.title

            # Genres
            metadata.genres.clear()
            genres = detailsPageElements.xpath('//a[@class="cat-tag"]')
            if len(genres) > 0:
                for genre in genres:
                    metadata.genres.add(genre.text_content())


            # Posters/Background
            valid_names = list()
            metadata.posters.validate_keys(valid_names)
            metadata.art.validate_keys(valid_names)
            posters = detailsPageElements.xpath('//a[contains(@class,"scene-image")]')
            background = "http:" + detailsPageElements.xpath('//video')[0].get("poster")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)

            posterNum = 1
            for posterCur in posters:
                posterURL = "http:" + posterCur.get("href")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1


        ##############################################################
        ##                                                          ##
        ##   Vixen                                                  ##
        ##                                                          ##
        ##############################################################
        if siteID == 52:
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.studio = "Vixen"
            paragraph = detailsPageElements.xpath('//span[@class="moreless js-readmore"]')[0].text_content()
            paragraph = paragraph.replace('&13;', '').strip(' \t\n\r"').replace('\n','').replace('  ','') + "\n\n"
            metadata.summary = paragraph
            metadata.title = detailsPageElements.xpath('//h1[@id="castme-title"]')[0].text_content()
            date = detailsPageElements.xpath('//span[@class="player-description-detail"]//span')[0].text_content()
            date_object = datetime.strptime(date, '%B %d, %Y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
                
            
            # Genres
            metadata.genres.clear()
            # No Source for Genres, add manual

            metadata.genres.add("Hardcore")
            metadata.genres.add("Heterosexual")
            metadata.genres.add("Boy Girl")
            metadata.genres.add("Caucasian Men")
            metadata.genres.add("Glamcore")

            # Actors
            metadata.roles.clear()
            actors = detailsPageElements.xpath('//p[@id="castme-subtitle"]//a')
            if len(actors) > 0:
                for actorLink in actors:
                    role = metadata.roles.new()
                    actorName = actorLink.text_content()
                    role.name = actorName
                    actorPageURL = actorLink.get("href")
                    actorPage = HTML.ElementFromURL("https://www.vixen.com"+actorPageURL)
                    actorPhotoURL = actorPage.xpath('//img[@class="thumb-img"]')[0].get("src")
                    role.photo = actorPhotoURL

            # Posters/Background
            posters = detailsPageElements.xpath('//div[@class="swiper-slide"]')
            background = detailsPageElements.xpath('//img[contains(@class,"player-img")]')[0].get("src")
            metadata.art[background] = Proxy.Preview(HTTP.Request(background, headers={'Referer': 'http://www.google.com'}).content, sort_order = 1)
            posterNum = 1
            for posterCur in posters:
                posterURL = posterCur.xpath('.//img[@class="swiper-content-img"]')[0].get("src")
                metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL, headers={'Referer': 'http://www.google.com'}).content, sort_order = posterNum)
                posterNum = posterNum + 1

        ##############################################################
        ##                                                          ##
        ##   Girlsway                                               ##
        ##                                                          ##
        ##############################################################
        if siteID == 53:
            temp = str(metadata.id).split("|")[0].replace('_','/')

            url = getSearchBaseURL(siteID) + temp
            detailsPageElements = HTML.ElementFromURL(url)

            # Summary
            metadata.summary = detailsPageElements.xpath('//div[contains(@class,"sceneDesc")]')[0].text_content()[60:]
            metadata.title = detailsPageElements.xpath('//h1[@class="title"]')[0].text_content()
            metadata.studio = "Girlsway"
            date = detailsPageElements.xpath('//div[@class="updatedDate"]')[0].text_content()[14:24]
            Log(date)
            date_object = datetime.strptime(date, '%Y-%m-%d')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year    
            
            # Genres
            metadata.genres.clear()
            genres = detailsPageElements.xpath('//div[contains(@class,"sceneColCategories")]//a')
            if len(genres) > 0:
                for genreLink in genres:
                    genreName = genreLink.text_content().lower()
                    metadata.genres.add(capitalize(genreName))

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