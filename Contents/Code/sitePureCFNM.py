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
        # Info passed on to update fxn
        titleNoFormatting = searchResult.xpath('.//span[@class="update_title"]')[0].text_content().strip()
        titleNoFormatting = titleNoFormatting.replace('/','_').replace('?','&')
        Log(titleNoFormatting)
        releaseDate = parse(searchResult.xpath('.//span[@class="update_date"]')[0].text_content().strip()).strftime('%Y-%m-%d')
        Log(releaseDate)
        # Fake Unique CurID
        curID = titleNoFormatting
        summary = searchResult.xpath('.//span[@class="latest_update_description"]')[0].text_content().strip()
        summary = summary.replace('/','_').replace('?','&')
        Log(summary)
        actorList = []
        actors = searchResult.xpath('.//span[@class="tour_update_models"]/a')
        for actorLink in actors:
            actorName = str(actorLink.text_content().strip())
            actorList.append(actorName)
        actors = ','.join(actorList)
        Log(actors)
        videoBG = searchResult.xpath('.//div[@class="update_image"]/a/img')[0].get('src')
        videoBG = videoBG.replace('/','_').replace('?','!')
        Log(videoBG)

        if searchDate:
            score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
        else:
            score = 60
        results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum) + "|" + titleNoFormatting + "|" + summary + "|" + releaseDate + "|" + actors + "|" + videoBG, name = titleNoFormatting + " [PureCFNM] " + releaseDate, score = score, lang = lang))
    return results

def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE METADATA CALLED*******')

    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'PureCFNM'

    # Title
    try:
        metadata.title = str(metadata.id).split("|")[2]
        metadata.title = metadata.title.replace('_','/').replace('&','?')
    except:
        pass

    # Summary
    try:
        metadata.summary = str(metadata.id).split("|")[3]
        metadata.summary = metadata.summary.replace('_','/').replace('&','?')
    except:
        pass

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteID).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    movieGenres.addGenre("CFNM")

    # Release Date
    try:
        date = str(metadata.id).split("|")[4]
        if len(date) > 0:
            date_object = parse(date)
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year
            Log("Date from file")
    except:
        pass

    # Actors
    try:
        actors = str(metadata.id).split("|")[5]
        actors = actors.split(",")
        for actorLink in actors:
            actorName = str(actorLink.strip())
            actorPhotoURL = ""
            movieActors.addActor(actorName,actorPhotoURL)
    except:
        pass

    ### Posters and artwork ###

    # Video trailer background image
    try:
        twitterBG = str(metadata.id).split("|")[6]
        twitterBG = PAsearchSites.getSearchBaseURL(siteID) + twitterBG.replace('_','/').replace('!','?')
        art.append(twitterBG)
    except:
        pass

    j = 1
    Log("Artwork found: " + str(len(art)))
    for posterUrl in art:
        if not PAsearchSites.posterAlreadyExists(posterUrl,metadata):
            metadata.posters[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
            metadata.art[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
            j = j + 1


    return metadata