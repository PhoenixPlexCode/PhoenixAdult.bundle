import PAsearchSites
import PAgenres
import PAactors

def search(results,encodedTitle,title,searchTitle,siteNum,lang,searchByDateActor,searchDate,searchSiteID):
    if searchSiteID != 9999:
        siteNum = searchSiteID
    searchString = searchTitle.replace(" ","-").replace(",","").replace("'","").replace("?","")
    Log("searchString: " + searchString)
    if "/" not in searchString:
        searchString = searchString.replace("-","/",1)
        Log("searchString formatted")
    searchResults = HTML.ElementFromURL(PAsearchSites.getSearchSearchURL(siteNum) + searchString)

    titleNoFormatting = searchResults.xpath('//div[@class="col-12 col-md-8"]//span[contains(@class,"text-lightgray")]')[0].text_content().strip()
    Log("titleNoFormatting: " + titleNoFormatting)
    curID = searchResults.xpath('//link[@rel="canonical"]')[0].get('href').replace('/','_').replace('?','!')
    Log("curID: " + curID)
    actors = searchResults.xpath('//div[@class="col-12 col-md-8"]//a//span')
    Log("# actors: " + str(len(actors)))
    firstActor = actors[0].text_content()
    Log("firstActor: " + firstActor)
    if "mylfdom" in curID:
        subSite = "MylfDom"
    else:
        subSite = searchResults.xpath('//img[@class="lazy img-fluid"]')[0].get("data-original").split('/')[-1].replace('_logo.png','').title()
    Log("subSite: " + subSite)
    if searchDate:
        releaseDate = parse(searchDate).strftime('%Y-%m-%d')
    else:
        releaseDate = ''

    score = 100
    results.Append(MetadataSearchResult(id = curID + "|" + str(siteNum) + "|" + releaseDate , name = titleNoFormatting + " [Mylf/"+subSite+"] ", score = score, lang = lang))

    return results

def update(metadata,siteID,movieGenres,movieActors):

    url = str(metadata.id).split("|")[0].replace('_','/').replace('?','!')
    detailsPageElements = HTML.ElementFromURL(url)
    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'Mylf'

    # Title
    metadata.title = detailsPageElements.xpath('//span[contains(@class,"m_scenetitle")]')[0].text_content().strip()
    Log("title: " + metadata.title)

    # Summary
    summary = detailsPageElements.xpath('//div[contains(@class,"text-light")]')[0].text_content().strip()
    metadata.summary = summary.replace('See full video here >', '')

    #Tagline and Collection(s)
    subSite = PAsearchSites.getSearchSiteName(siteID)
    metadata.tagline = subSite
    metadata.collections.add(subSite)
    Log("subSite: " + subSite)

    # Release Date
    date = str(metadata.id).split("|")[2]
    if len(date) > 0:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
        Log("Date from file")

    # Actors
    actors = detailsPageElements.xpath('//div[@class="col-12 col-md-8"]//a')
    if len(actors) > 0:
        for actor in actors:
            actorName = actor.xpath('./span')[0].text_content().strip()
            actorPageURL = actor.get("href")
            if 'http' not in actorPageURL:
                actorPageURL = PAsearchSites.getSearchBaseURL(siteID) + actorPageURL
            actorPage = HTML.ElementFromURL(actorPageURL)
            actorPhotoURL = actorPage.xpath('//img[contains(@class,"girlthumb")]')[0].get("data-original")
            movieActors.addActor(actorName,actorPhotoURL)
            Log('actor: ' + actorName + ", " + actorPhotoURL)

    # Genres
    movieGenres.clearGenres()
    genres = ["MILF", "Mature"]
        # Based on site
    if subSite.lower() == "MylfBoss".lower():
        for genreName in ['Office', 'Boss']:
            movieGenres.addGenre(genreName)
    elif subSite.lower() == "MylfBlows".lower():
        for genreName in ['Blowjob']:
            movieGenres.addGenre(genreName)
    elif subSite.lower() == "Milfty".lower():
        for genreName in ['Cheating']:
            movieGenres.addGenre(genreName)
    # elif subSite.lower() == "Got Mylf".lower():
    #     for genreName in []:
    #         movieGenres.addGenre(genreName)
    elif subSite.lower() == "Mom Drips".lower():
        for genreName in ['Creampie']:
            movieGenres.addGenre(genreName)
    elif subSite.lower() == "Milf Body".lower():
        for genreName in ['Gym', 'Fitness']:
            movieGenres.addGenre(genreName)
    elif subSite.lower() == "Lone Milf".lower():
        for genreName in ['Solo']:
            movieGenres.addGenre(genreName)
    elif subSite.lower() == "Full Of JOI".lower():
        for genreName in ['JOI']:
            movieGenres.addGenre(genreName)
    elif subSite.lower() == "Mylfed".lower():
        for genreName in ['Lesbian', 'Girl on Girl', 'GG']:
            movieGenres.addGenre(genreName)
    elif subSite.lower() == "MylfDom".lower():
        for genreName in ['BDSM']:
            movieGenres.addGenre(genreName)
    if (len(actors) > 1) and subSite != "Mylfed":
        genres.append("Threesome")
    for genre in genres:
        movieGenres.addGenre(genre)

    ### Posters and artwork ###

    # Video trailer background image
    try:
        twitterBG = detailsPageElements.xpath('//video[@id="main-movie-player"]')[0].get('poster')
        art.append(twitterBG)
    except:
        pass

    # Photos
    photos = detailsPageElements.xpath('//div[contains(@class,"trailer-small-images")]//a')
    if len(photos) > 0:
        for photoLink in photos:
            photo = photoLink.get('href')
            if 'http' not in photo:
                photo = PAsearchSites.getSearchBaseURL(siteID) + photo
            art.append(photo)

    j = 1
    Log("Artwork found: " + str(len(art)))
    for posterUrl in art:
        if not PAsearchSites.posterAlreadyExists(posterUrl,metadata):
            #Download image file for analysis
            try:
                img_file = urllib.urlopen(posterUrl)
                im = StringIO(img_file.read())
                resized_image = Image.open(im)
                width, height = resized_image.size
                #Add the image proxy items to the collection
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Preview(HTTP.Request(posterUrl, headers={'Referer': 'http://www.google.com'}).content, sort_order = j)
                j = j + 1
            except:
                pass

    return metadata
