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
        curID = titleNoFormatting
        releaseDate = parse(searchResults.xpath('.//span[@class="update_date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
        realURL = (PAsearchSites.getSearchSearchURL(siteNum) + searchString)
        Log("RealURL " + realURL)
        summary = searchResult.xpath('.//span[@class="latest_update_description"]')[0].text_content().strip()
        score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum) + "|" + realURL + "|" + releaseDate + "|" + summary, name = titleNoFormatting + " AmateurCFNM " + releaseDate, score = score, lang = lang))
    return results
    Log('***Results Returned****')

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


    return metadata