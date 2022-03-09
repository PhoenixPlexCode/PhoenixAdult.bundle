import site
import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchPage = PAsearchSites.getSearchSearchURL(siteNum)
    req = PAutils.HTTPRequest(searchPage)
    searchResults = HTML.ElementFromString(req.text)
    siteKey = 0

    xPath = dictValuesFromKey(xPathDB, PAsearchSites.getSearchSiteName(siteNum))

    (siteKey, sitePages) = dictValuesFromKey(siteDB, PAsearchSites.getSearchSiteName(siteNum))

    dirtyFlixTour1 = 'http://dirtyflix.com/index.php/main/show_one_tour/%d' % siteKey
    req = PAutils.HTTPRequest(dirtyFlixTour1)
    tourPageElements1 = HTML.ElementFromString(req.text)

    dirtyFlixTour2 = 'http://dirtyflix.com/index.php/main/show_one_tour/%d/2' % siteKey
    req = PAutils.HTTPRequest(dirtyFlixTour2)
    tourPageElements2 = HTML.ElementFromString(req.text)

    for idx in range(2, sitePages):
        for searchResult in searchResults.xpath('//div[@class="movie-block"]'):
            titleNoFormatting = PAutils.parseTitle(searchResult.xpath(xPath[0])[0].text_content().strip(), siteNum)

            sceneID = searchResult.xpath('.//li/img/@src')[0]
            m = re.search(r'(?<=tour_thumbs/).*(?=\/)', sceneID)
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

            if searchData.date:
                score = score - Util.LevenshteinDistance(searchData.date, releaseDate)

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
    sceneID = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    searchPageURL = PAutils.Decode(metadata_id[3])

    req = PAutils.HTTPRequest(searchPageURL)
    detailsPageElements = HTML.ElementFromString(req.text).xpath('//div[@class="movie-block"][.//*[contains(@src, "%s")]]' % sceneID)[0]

    xPath = dictValuesFromKey(xPathDB, PAsearchSites.getSearchSiteName(siteNum))

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath(xPath[0])[0].text_content().strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath(xPath[1])[0].text_content().strip()

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
    genres = dictValuesFromKey(genresDB, PAsearchSites.getSearchSiteName(siteNum))
    for genreName in genres:
        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = dictKeyFromValues(sceneActorsDB, sceneID)
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


def dictValuesFromKey(dictDB, identifier):
    for k, values in dictDB.items():
        keys = list(k) if type(k) == tuple else [k]
        for key in keys:
            if key.lower() == identifier.replace(' ', '').lower():
                return values
    return


def dictKeyFromValues(dictDB, identifier):
    values = []
    for key, value in dictDB.items():
        for item in value:
            if item.lower() == identifier.lower():
                values.append(key)
                break
    return values


genresDB = {
    'TrickYourGF': ['Girlfriend', 'Revenge'],
    'MakeHimCuckold': ['Cuckold'],
    'SheIsNerdy': ['Glasses', 'Nerd'],
    'TrickyAgent': ['Agent', 'Casting'],
}


xPathDB = {
    ('TrickYourGF', 'MakeHimCuckold'): ['.//a[contains(@class, "link")]', './/div[@class="description"]'],
    'SheIsNerdy': ['.//a[contains(@class, "title")]', './/div[@class="description"]'],
    'TrickyAgent': ['.//h3', './/div[@class="text"]'],
}


# [Dirty Flix Tour Number, Number of Active Search Pages]
siteDB = {
    'TrickYourGF': [7, 4],
    'MakeHimCuckold': [9, 5],
    'SheIsNerdy': [10, 12],
    'TrickyAgent': [11, 4],
}


sceneActorsDB = {
    'Adina': ['darygf050'],
    'Aggie': ['wrygf726'],
    'Aimee Ryan': ['pfc070'],
    'Alaina Dawson': ['crygf009'],
    'Alexis Crash': ['wrygf499'],
    'Alice Marshall': ['wrygf930', 'wfc929'],
    'Alice Lee': ['wrygf776'],
    'Amanda Moore': ['pfc111'],
    'Ann Marie': ['wfc715'],
    'Amalia Davis': ['wnc1560'],
    'Amber Daikiri': ['wrygf508'],
    'Andrea Sun': ['darygf057'],
    'Angel Dickens': ['wfc391'],
    'Angel Piaff': ['pfc119'],
    'Angie Koks': ['wrygf911'],
    'Annika Seren': ['wrygf451'],
    'Aruna Aghora': ['wrygf900', 'wfc907'],
    'Ashley Woods': ['dafc140'],
    'Carmen Fox': ['wnc833', 'wfc863'],
    'Cassidy Klein': ['cfc005'],
    'Chloe Blue': ['wrygf526'],
    'Christi Cats': ['wrygf553'],
    'Darcy Dark': ['wnc1590'],
    'Denisa Peterson': ['pfc056'],
    'Donna Keller': ['wfc408'],
    'Dushenka': ['wfc701'],
    'Ellie': ['pfc129'],
    'Elin Holm': ['wnc1453'],
    'Elisaveta Gulobeva': ['wfc926'],
    'Emma Brown': ['wfc1089'],
    'Eva': ['wrygf865'],
    'Eveline Neill': ['pfc123'],
    'Evelyn Cage': ['wrygf651'],
    'Gina Gerson': ['wrygf622'],
    'Gisha Forza': ['wrygf1442'],
    'Gloria Miller': ['wrygf738'],
    'Glorie': ['darygf052'],
    'Grace': ['wfc960'],
    'Grace Young': ['wfc380'],
    'Foxy Di': ['wrygf886', 'wrygf828'],
    'Foxy Katrina': ['wfc866'],
    'Francheska': ['wfc406'],
    'Hanna Rey': ['wnc1550'],
    'Inga Zolva': ['wrygf747'],
    'Iris Kiss': ['snc165', 'wnc1637'],
    'Isabel Stern': ['wfc1075'],
    'Iva Zan': ['wrygf536'],
    'Izi Ashley': ['wfc978'],
    'Jenny Love': ['wrygf634', 'wfc607'],
    'Jenny Manson': ['wtag1324', 'wfc1302'],
    'Jessica Malone': ['wrygf1078'],
    'Jessica Rox': ['prygf138', 'pfc137'],
    'Jessy Nikea': ['wfc374'],
    'Kari Sweet': ['prygf135', 'pfc134'],
    'Kendra Cole': ['hrygf002'],
    'Kiara Knight': ['crygf002'],
    'Kimberly Mansell': ['wrygf528'],
    'Kira Stone': ['snc171'],
    'Lena Love': ['wfc600'],
    'Lia Chalizo': ['wfc373'],
    'Lina Arian Joy': ['wfc954'],
    'Lina Napoli': ['wrygf760'],
    'Lindsey Olsen': ['wfc589'],
    'Liona Levi': ['wrygf663'],
    'Lita': ['wfc902'],
    'Lizaveta Kay': ['wrygf733'],
    'Maggie Gold': ['pfc057'],
    'Maribel': ['wfc367'],
    'Margarita C': ['wfc940'],
    'Mazy Teen': ['pfc069'],
    'Megan Promesita': ['pfc104'],
    'Melissa Benz': ['wfc1276'],
    'Mia Hilton': ['pfc065'],
    'Michelle Can': ['wfc1392'],
    'Mila Gimnasterka': ['wfc1100'],
    'Milka Feer': ['snc214'],
    'Mirta': ['wfc919'],
    'Molly Manson': ['crygf013'],
    'Monica Rise': ['crygf011'],
    'Nesti': ['wfc696'],
    'Norah Nova': ['cfc008'],
    'Oliva Grace': ['wrygf991'],
    'Petia': ['pfc062'],
    'Petra Larkson': ['pfc141'],
    'Rahyndee James': ['cfc003'],
    'Rebecca Rainbow': ['wrygf1201'],
    'Renata Fox': ['wfc1215'],
    'Rita': ['wtag1232'],
    'Rita Jalace': ['wrygf633'],
    'Rita Milan': ['wrygf870', 'wfc968'],
    'Rosa Mentoni': ['wfc932'],
    'Sabrina Moor': ['wfc869'],
    'Selena Stuart': ['wrygf798'],
    'Shirley Harris': ['wrygf485'],
    'Shrima Malati': ['wrygf993'],
    'Soni': ['wrygf648'],
    'Sonya Sweet': ['wfc1198'],
    'Stacy Snake': ['wrygf427'],
    'Stefanie Moon': ['wfc1107'],
    'Stella Flex': ['wfc1431'],
    'Sunny Alika': ['wfc1123'],
    'Sunny Rise': ['wfc403'],
    'Tais Afinskaja': ['wfc497'],
    'Taissia Shanti': ['wfc953'],
    'Tonya Nats': ['wfc539'],
    'Veronika Fare': ['wnc1315'],
    'Vika Lita': ['wfc1480'],
    'Zena Little': ['dafc139'],
}
