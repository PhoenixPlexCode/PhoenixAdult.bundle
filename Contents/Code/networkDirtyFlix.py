import site
import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchPage = PAsearchSites.getSearchSearchURL(siteNum)
    req = PAutils.HTTPRequest(searchPage)
    searchResults = HTML.ElementFromString(req.text)
    siteKey = 0
    titleXPath = ''

    for key, value in titleDB.items():
        if key.lower() == PAsearchSites.getSearchSiteName(siteNum).replace(' ', '').lower():
            titleXPath = value
            break

    for key, value in siteDB.items():
        if key.lower() == PAsearchSites.getSearchSiteName(siteNum).replace(' ', '').lower():
            siteKey = value[0]
            sitePages = value[1]
            break

    dirtyFlixTour1 = 'http://dirtyflix.com/index.php/main/show_one_tour/%d' % siteKey
    req = PAutils.HTTPRequest(dirtyFlixTour1)
    tourPageElements1 = HTML.ElementFromString(req.text)

    dirtyFlixTour2 = 'http://dirtyflix.com/index.php/main/show_one_tour/%d/2' % siteKey
    req = PAutils.HTTPRequest(dirtyFlixTour2)
    tourPageElements2 = HTML.ElementFromString(req.text)

    for idx in range (2, sitePages):
        for searchResult in searchResults.xpath('//div[@class="movie-block"]'):
            titleNoFormatting = PAutils.parseTitle(searchResult.xpath(titleXPath)[0].text_content().strip(), siteNum)

            movieID = searchResult.xpath('.//li/img/@src')[0]
            m = re.search(r'(?<=tour_thumbs/).*(?=\/)', movieID)
            if m:
                curID = PAutils.Encode(m.group(0))

            try:
                tourPageElements = tourPageElements1.xpath('//div[@class="thumbs-item"][.//*[contains(@src, "%s")]]' % m.group(0))[0]
                date = tourPageElements.xpath('.//span[@class="added"]')[0].text_content().strip()
            except:
                try:
                    tourPageElements = tourPageElements2.xpath('//div[@class="thumbs-item"][.//*[contains(@src, "%s")]]' % m.group(0))[0]
                    date = tourPageElements.xpath('.//span[@class="added"]')[0].text_content().strip()
                except:
                    date = ''

            if date:
                releaseDate = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
            else:
                releaseDate = searchData.dateFormat() if searchData.date else ''

            score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d|%s|%s' % (curID, siteNum, releaseDate, PAutils.Encode(searchPage)), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

            if int(score) == 80:
                break
        else:
            searchPage = '%s%d' % (PAsearchSites.getSearchSearchURL(siteNum), idx)
            req = PAutils.HTTPRequest(searchPage)
            searchResults = HTML.ElementFromString(req.text)
            continue
        break

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    movieID = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    searchPageURL = PAutils.Decode(metadata_id[3])

    req = PAutils.HTTPRequest(searchPageURL)
    detailsPageElements = HTML.ElementFromString(req.text).xpath('//div[@class="movie-block"][.//*[contains(@src, "%s")]]' % movieID)[0]

    # Title
    for key, value in titleDB.items():
        if key.lower() == PAsearchSites.getSearchSiteName(siteNum).replace(' ', '').lower():
            titleXPath = value
            break

    metadata.title = PAutils.parseTitle(detailsPageElements.xpath(titleXPath)[0].text_content().strip(), siteNum)

    # Summary
    for key, value in summaryDB.items():
        if key.lower() == PAsearchSites.getSearchSiteName(siteNum).replace(' ', '').lower():
            summaryXPath = value
            break

    metadata.summary = detailsPageElements.xpath(summaryXPath)[0].text_content().strip()

    # Studio
    metadata.studio = 'Dirty Flix'

    # Collections / Tagline
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    genres = []
    for key, value in genresDB.items():
        if key.lower() == PAsearchSites.getSearchSiteName(siteNum).replace(' ', '').lower():
            genres = value
            break

    for genreName in genres:
        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = []
    for key, value in sceneActorsDB.items():
        for item in value:
            if item.lower() == movieID.lower():
                actors.append(key)
                break

    for actor in actors:
        actorName = actor.strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art.append(detailsPageElements.xpath('.//img/@src')[0])

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
                if width > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > height:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


genresDB = {
    'TrickYourGF': ['Girlfriend'],
    'MakeHimCuckold': ['Cuckold'],
    'SheIsNerdy': ['Glasses', 'Nerd'],
    'TrickyAgent': ['Agent'],
}


titleDB = {
    'TrickYourGF': './/a[contains(@class, "link")]',
    'MakeHimCuckold': './/a[contains(@class, "link")]',
    'SheIsNerdy': './/a[contains(@class, "title")]',
    'TrickyAgent': './/h3',
}


summaryDB = {
    'TrickYourGF': './/div[@class="description"]',
    'MakeHimCuckold': './/div[@class="description"]',
    'SheIsNerdy': './/div[@class="description"]',
    'TrickyAgent': './/div[@class="text"]',
}


siteDB = {
    'TrickYourGF': [7, 4],
    'MakeHimCuckold': [9, 5],
    'SheIsNerdy': [10, 12],
    'TrickyAgent': [11, 4],
}


sceneActorsDB = {
    'Alaina Dawson': ['crygf009'],
    'Amalia Davis': ['wnc1560'],
    'Carmen Fox': ['wnc833'],
    'Darcy Dark': ['wnc1590'],
    'Elin Holm': ['wnc1453'],
    'Gisha Forza': ['wrygf1442'],
    'Hanna Rey': ['wnc1550'],
    'Iris Kiss': ['snc165', 'wnc1637'],
    'Jenny Manson': ['wtag1324'],
    'Kira Stone': ['snc171'],
    'Milka': ['snc214'],
    'Molly Manson': ['crygf013'],
    'Monica Rise': ['crygf011'],
    'Rebecca Rainbow': ['wrygf1201'],
    'Rita': ['wtag1232'],
    'Veronika Fare': ['wnc1315'],
}
