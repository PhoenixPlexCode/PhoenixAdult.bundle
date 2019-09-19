import PAsearchSites
import PAgenres
def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    if searchSiteID != 9999:
        siteNum = searchSiteID
    searchPageNum = 1
    while searchPageNum <= 2:
        searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle + "/" + str(searchPageNum))

        for searchResult in searchResults.xpath('//div[@class="thumbsHolder elipsTxt"]/div[1]/div[@class="echThumb"]'):
            if len(searchResult.xpath('.//a[contains(@href,"/video")]')) > 0:
                titleNoFormatting = searchResult.xpath('.//a[contains(@href,"/video")]')[0].get("title")
                curID = searchResult.xpath('.//a[contains(@href,"/video")]')[0].get("href").replace('/','_').replace('?','!')
                subSite = searchResult.xpath('.//span[@class="faTxt"]')[0].text_content().strip()
                releaseDate = parse(searchResult.xpath('.//span[@class="faTxt"]')[1].text_content().strip()).strftime('%Y-%m-%d')
                if searchDate:
                    score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
                else:
                    score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())
                if subSite != "BangBros":
                    subSite = "/"+subSite
                results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum), name = titleNoFormatting + " [BangBros"+subSite+"] " + releaseDate, score = score, lang = lang))
        searchPageNum += 1

    return results


def update(metadata,siteID,movieGenres,movieActors):
    Log('******UPDATE CALLED*******')
    temp = str(metadata.id).split("|")[0].replace('_','/').replace('!','?')

    url = PAsearchSites.getSearchBaseURL(siteID) + temp
    detailsPageElements = HTML.ElementFromURL(url)

    # Summary
    metadata.studio = "Bang Bros"
    metadata.summary = detailsPageElements.xpath('//div[@class="vdoDesc"]')[0].text_content().strip()
    metadata.title = detailsPageElements.xpath('//h1')[0].text_content()
    releaseID = detailsPageElements.xpath('//div[@class="vdoCast"]')[1].text_content()[9:]
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteID) + releaseID)
    searchResult = searchResults.xpath('//div[@class="echThumb"]')[0]
    releaseDate = searchResult.xpath('.//span[@class="faTxt"]')[1].text_content().strip().replace("\n","")
    date_object = datetime.strptime(releaseDate, '%b %d, %Y')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year 
    metadata.tagline = detailsPageElements.xpath('//a[contains(@href,"/websites")]')[1].text_content()
    metadata.collections.clear()
    metadata.collections.add(metadata.tagline)

    # Genres
    movieGenres.clearGenres()
    genres = detailsPageElements.xpath('//div[contains(@class,"vdoTags")]//a')
    if len(genres) > 0:
        for genreLink in genres:
            genreName = genreLink.text_content().strip('\n').lower()
            movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[@class="vdoCast"]//a[contains(@href,"/model")]')
    if len(actors) > 0:
        for actorLink in actors:
            actorName = actorLink.text_content()
            actorPageURL = actorLink.get("href")
            actorPage = HTML.ElementFromURL(PAsearchSites.getSearchBaseURL(siteID) + actorPageURL)
            actorPhotoURL = "http:" + actorPage.xpath('//div[@class="profilePic_in"]//img')[0].get("src")
            movieActors.addActor(actorName,actorPhotoURL)

    # Posters/Background
    valid_names = list()
    metadata.posters.validate_keys(valid_names)
    metadata.art.validate_keys(valid_names)

    background = "http:" + detailsPageElements.xpath('//img[contains(@id,"player-overlay-image")]')[0].get("src")
    try:
        metadata.art[background] = Proxy.Preview(HTTP.Request(background).content, sort_order = 1)
    except:
        pass
    
    posters = detailsPageElements.xpath('//div[@class="WdgtPic modal-overlay"]')
    posterNum = 1
    for poster in posters:
        posterURL = "http:" + poster.xpath('.//img')[0].get("src")
        posterURL = posterURL[:-5] + "big" + posterURL[-5:]
        try:
            metadata.posters[posterURL] = Proxy.Preview(HTTP.Request(posterURL).content, sort_order = posterNum)
            posterNum += 1
        except:
            pass

    return metadata
