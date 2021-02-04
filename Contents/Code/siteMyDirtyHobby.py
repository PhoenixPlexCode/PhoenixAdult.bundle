import PAsearchSites
import PAutils

	
def search(results, lang, siteNum, searchData):
    searchResults = []

    googleResults = PAutils.getFromGoogleSearch(searchData.title, siteNum, lang='de')
    for sceneURL in googleResults:
        sceneURL = sceneURL.replace('www.mydirtyhobby.de', 'de.mydirtyhobby.com')
        if '/videos/' in sceneURL:
            searchResults.append(sceneURL)
    for sceneURL in searchResults:
        req = PAutils.HTTPRequest(sceneURL)
        detailsPageElements = HTML.ElementFromString(req.text)

        titleNoFormatting = detailsPageElements.xpath('//div[@class="page-header clearfix"]/h1')[0].text_content()

        curID = PAutils.Encode(sceneURL)

        releaseDate = parse(detailsPageElements.xpath('//div[contains(@class, "info-wrapper")]//i[contains(@class, "calendar")]')[0].text_content().strip()).strftime('%d.%m.%y')

        if searchData.date and releaseDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [MyDirtyHobby]' % titleNoFormatting, score=score, lang=lang))

    return results

def update(metadata, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)
    art = []

    # Title
    metadata.title = detailsPageElements.xpath('//div[@class="page-header clearfix"]/h1')[0].text_content().strip()

    # Summary
    summary = detailsPageElements.xpath('//div[@class="video-description col-xs-12 col-md-4"]/p')[0].text_content().strip()
    metadata.summary = summary

    # Studio
    metadata.studio = 'MyDirtyHobby'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = detailsPageElements.xpath('//dl[@class="profile-stats clearfix compact"]//a')[0].text_content().strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)
    metadata.collections.add('MyDirtyHobby')

    # Release Date
    date = detailsPageElements.xpath('//div[2]/div/div/main/div/div[2]/div[4]/div/div/div[3]/div[2]/div[2]/dl/dd[1]')[0].text_content().strip()
    if date:
        date_object = datetime.strptime(date, '%m/%d/%y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[2]/div/div/main/div/div[2]/div[4]/div/div/div[3]/div[2]/div[2]/dl/dd/a'):
        genreName = genreLink.text_content().strip().lower()
        genreName = genreName.replace(tagline,'')

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[2]/div/div/main/div/div[2]/div[4]/div/div/div[1]/div/div[2]/span/a')
    if actors:
        for actorLink in actors:
            actorName = actorLink.text_content().strip().split('exclusive')[1]
            actorPhotoURL = ''

            try:
                actorPageURL = actorLink.get('href')
                if 'http' not in actorPageURL:
                    actorPageURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPageURL

                req = PAutils.HTTPRequest(actorPageURL)
                actorPage = HTML.ElementFromString(req.text)
                actorPhotoURL = actorPage.xpath('//div[2]/div/div/main/div/div[2]/div[4]/div[1]/div[2]/div/div[1]/div/a/img/@src')[0]
                if 'http' not in actorPhotoURL:
                    actorPhotoURL = PAsearchSites.getSearchBaseURL(siteNum) + actorPhotoURL
            except:
                pass

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art = []
    xpaths = [
        '/html/body/div[2]/div/div/main/div/div[2]/div[4]/div/div/div[3]/div[1]/div/div/div/div/a/img/@src',
    ]
    for xpath in xpaths:
        for poster in detailsPageElements.xpath(xpath):
            art.append(poster)

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1 or height > width:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100 and width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass



    return metadata
