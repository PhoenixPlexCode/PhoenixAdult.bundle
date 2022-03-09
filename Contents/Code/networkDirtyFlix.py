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
    'Aggie': ['wrygf726', 'wtag728'],
    'Aimee Ryan': ['pfc070'],
    'Alaina Dawson': ['crygf009'],
    'Alexis Crash': ['wrygf499'],
    'Alexis Crystal': ['danc129'],
    'Alice Lee': ['wrygf776', 'wtag770', 'wnc765'],
    'Alice Marshall': ['wrygf930', 'wfc929', 'wtag934', 'wnc936'],
    'Amalia Davis': ['wnc1560'],
    'Amanda Moore': ['pfc111'],
    'Amber Daikiri': ['wrygf508'],
    'Ananta Shakti': ['wtag893', 'wnc810', 'wnc888'],
    'Andrea Sun': ['darygf057'],
    'Angel Dickens': ['wfc391'],
    'Angel Piaff': ['pfc119'],
    'Angie Koks': ['wrygf911'],
    'Angie Moon': ['wtag1050'],
    'Ann Marie': ['wfc715', 'wtag719', 'wnc714'],
    'Anne Angel': ['wtag577'],
    'Annette': ['wtag579'],
    'Annika Seren': ['wrygf451'],
    'Ariadna Moon': ['wtag994'],
    'Aruna Aghora': ['wrygf900', 'wfc907', 'wtag955', 'wtag908'],
    'Ashley Woods': ['dafc140'],
    'Carmen Fox': ['wnc833', 'wfc863', 'wtag892'],
    'Cassidy Klein': ['cfc005'],
    'Chloe Blue': ['wrygf526'],
    'Christi Cats': ['wrygf553', 'wtag584'],
    'Darcy Dark': ['wnc1590'],
    'Denisa Peterson': ['pfc056'],
    'Donna Keller': ['wfc408'],
    'Dushenka': ['wfc701', 'wtag700', 'wnc699'],
    'Elin Holm': ['wnc1453'],
    'Elisaveta Gulobeva': ['wfc926', 'wtag922'],
    'Ellie': ['pfc129'],
    'Emily Thorne': ['wtag1163'],
    'Emma Brown': ['wfc1089', 'wtag1102'],
    'Eva': ['wrygf865'],
    'Eveline Neill': ['pfc123'],
    'Evelyn Cage': ['wrygf651', 'wtag644'],
    'Foxy Di': ['wrygf886', 'wrygf828', 'wtag859', 'wnc821'],
    'Foxy Katrina': ['wfc866', 'wtag871', 'wnc872'],
    'Francheska': ['wfc406'],
    'Gina Gerson': ['wrygf622', 'wtag617', 'wnc690'],
    'Gisha Forza': ['wrygf1442'],
    'Gloria Miller': ['wrygf738', 'wnc735'],
    'Glorie': ['darygf052'],
    'Grace Young': ['wfc380'],
    'Grace': ['wfc960'],
    'Hanna Rey': ['wnc1550'],
    'Inga Zolva': ['wrygf747', 'wtag767', 'wnc879'],
    'Iris Kiss': ['snc165', 'wnc1637'],
    'Isabel Stern': ['wfc1075'],
    'Iva Zan': ['wrygf536', 'wtag558'],
    'Izi Ashley': ['wfc978', 'wtag980', 'wnc97'],
    'Jane Fox': ['wtag1235'],
    'Jenny Love': ['wrygf634', 'wfc607', 'wtag601'],
    'Jenny Manson': ['wtag1324', 'wfc1302'],
    'Jessica Malone': ['wrygf1078', 'wtag1101', 'wnc1086'],
    'Jessica Rox': ['prygf138', 'pfc137'],
    'Jessy Nikea': ['wfc374'],
    'Kari Sweet': ['prygf135', 'pfc134'],
    'Katty West': ['wtag1181'],
    'Katya': ['wtag1181', 'wnc758'],
    'Kendra Cole': ['hrygf002'],
    'Kiara Knight': ['crygf002'],
    'Kimberly Mansell': ['wrygf528'],
    'Kira Parvati': ['wtag777'],
    'Kira Stone': ['snc171'],
    'Lena Love': ['wfc600', 'wtag580'],
    'Lia Chalizo': ['wfc373'],
    'Lina Arian Joy': ['wfc954'],
    'Lina Napoli': ['wrygf760', 'wtag772', 'wnc752'],
    'Lindsey Olsen': ['wfc589', 'wtag598'],
    'Liona Levi': ['wrygf663', 'wtag660'],
    'Lita': ['wfc902'],
    'Liza Kolt': ['wtag741', 'wnc732'],
    'Lizaveta Kay': ['wrygf733'],
    'Maggie Gold': ['pfc057'],
    'Margarita C': ['wfc940', 'wnc941'],
    'Maribel': ['wfc367'],
    'Mazy Teen': ['pfc069'],
    'Megan Promesita': ['pfc104'],
    'Melissa Benz': ['wfc1276'],
    'Mia Hilton': ['pfc065'],
    'Mia Reese': ['wtag887'],
    'Michelle Can': ['wfc1392'],
    'Mila Gimnasterka': ['wfc1100'],
    'Milka Feer': ['snc214'],
    'Mirta': ['wfc919'],
    'Molly Manson': ['crygf013'],
    'Monica Rise': ['crygf011'],
    'Nataly Gold': ['wtag594'],
    'Natalya C': ['wtag649'],
    'Nesti': ['wfc696'],
    'Norah Nova': ['cfc008'],
    'Oliva Grace': ['wrygf991', 'wtag996'],
    'Petia': ['pfc062'],
    'Petra Larkson': ['pfc141'],
    'Rahyndee James': ['cfc003'],
    'Raquel Rimma': ['wtag1134'],
    'Rebecca Rainbow': ['wrygf1201', 'wtag1193'],
    'Renata Fox': ['wfc1215'],
    'Rita Jalace': ['wrygf633', 'wtag643', 'wnc740'],
    'Rita Milan': ['wrygf870', 'wfc968', 'wtag961'],
    'Rita': ['wtag1232'],
    'Rosa Mentoni': ['wfc932'],
    'Sabrina Moor': ['wfc869', 'wtag995'],
    'Salomja A': ['wtag803'],
    'Sara Redz': ['wtag804', 'wnc800'],
    'Selena Stuart': ['wrygf798', 'wnc801'],
    'Sherry E': ['wtag570'],
    'Shirley Harris': ['wrygf485'],
    'Shrima Malati': ['wrygf993', 'wtag997'],
    'Sofi Goldfinger': [''],
    'Sofy Soul': ['wtag1252'],
    'Soni': ['wrygf648', 'wtag610'],
    'Sonya Sweet': ['wfc1198', 'wtag1204'],
    'Stacy Snake': ['wrygf427'],
    'Stefanie Moon': ['wfc1107', 'wtag1122'],
    'Stella Flex': ['wfc1431'],
    'Sunny Alika': ['wfc1123'],
    'Sunny Rise': ['wfc403'],
    'Sweet Cat': ['wfc403', 'danc115'],
    'Tais Afinskaja': ['wfc497'],
    'Taissia Shanti': ['wfc953', 'wtag955'],
    'Taniella': ['wtag675'],
    'Tarja King': ['danc125'],
    'Timea Bella': ['danc124'],
    'Tonya Nats': ['wfc539'],
    'Veronika Fare': ['wnc1315'],
    'Vika Lita': ['wfc1480'],
    'Vika Volkova': ['wtag1036'],
    'Violette Pink': ['danc111'],
    'Zena Little': ['dafc139', 'danc110'],
}
