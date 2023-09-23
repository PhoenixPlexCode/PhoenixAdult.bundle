import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchPage = PAsearchSites.getSearchSearchURL(siteNum)
    req = PAutils.HTTPRequest(searchPage)
    searchResults = HTML.ElementFromString(req.text)

    xPath = PAutils.getDictValuesFromKey(xPathDB, PAsearchSites.getSearchSiteName(siteNum))
    scenes = PAutils.getDictValuesFromKey(sceneActorsDB, searchData.title)
    (siteKey, sitePages) = PAutils.getDictValuesFromKey(siteDB, PAsearchSites.getSearchSiteName(siteNum))

    dirtyFlixTour1 = 'http://dirtyflix.com/index.php/main/show_one_tour/%d' % siteKey
    req = PAutils.HTTPRequest(dirtyFlixTour1)
    tourPageElements1 = HTML.ElementFromString(req.text)

    dirtyFlixTour2 = 'http://dirtyflix.com/index.php/main/show_one_tour/%d/2' % siteKey
    req = PAutils.HTTPRequest(dirtyFlixTour2)
    tourPageElements2 = HTML.ElementFromString(req.text)

    re_sceneid = re.compile(r'(?<=tour_thumbs/).*(?=\/)')
    for idx in range(2, sitePages):
        for searchResult in searchResults.xpath('//div[@class="movie-block"]'):
            titleNoFormatting = PAutils.parseTitle(searchResult.xpath(xPath[0])[0].text_content().strip(), siteNum)

            sceneID = 0
            m = re_sceneid.search(searchResult.xpath('.//li/img/@src')[0])
            if m:
                sceneID = m.group(0)
                curID = PAutils.Encode(sceneID)

            try:
                tourPageElements = tourPageElements1.xpath('//div[@class="thumbs-item"][.//*[contains(@src, "%s")]]' % m.group(0))[0]
                date = tourPageElements.xpath('.//span[@class="added"]')[0].text_content().strip()
            except:
                try:
                    tourPageElements = tourPageElements2.xpath('//div[@class="thumbs-item"][.//*[contains(@src, "%s")]]' % m.group(0))[0]
                    date = tourPageElements.xpath('.//span[@class="added"]')[0].text_content().strip()
                except:
                    date = ''

            try:
                if date:
                    releaseDate = datetime.strptime(date, '%Y-%m-%d').strftime('%Y-%m-%d')
                else:
                    releaseDate = searchData.dateFormat() if searchData.date else ''
            except:
                releaseDate = ''

            if sceneID in scenes:
                score = 100
            else:
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

    xPath = PAutils.getDictValuesFromKey(xPathDB, PAsearchSites.getSearchSiteName(siteNum))

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath(xPath[0])[0].text_content().strip(), siteNum)

    # Summary
    metadata.summary = detailsPageElements.xpath(xPath[1])[0].text_content().strip()

    # Studio
    metadata.studio = 'Dirty Flix'

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    genres = PAutils.getDictValuesFromKey(genresDB, PAsearchSites.getSearchSiteName(siteNum))
    for genreName in genres:
        movieGenres.addGenre(genreName)

    # Actor(s)
    actors = PAutils.getDictKeyFromValues(sceneActorsDB, sceneID)
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
    'Trick Your GF': ['Girlfriend', 'Revenge'],
    'Make Him Cuckold': ['Cuckold'],
    'She Is Nerdy': ['Glasses', 'Nerd'],
    'Tricky Agent': ['Agent', 'Casting'],
}


xPathDB = {
    ('Trick Your GF', 'Make Him Cuckold'): ['.//a[contains(@class, "link")]', './/div[@class="description"]'],
    'She Is Nerdy': ['.//a[contains(@class, "title")]', './/div[@class="description"]'],
    'Tricky Agent': ['.//h3', './/div[@class="text"]'],
}


# [Dirty Flix Tour Number, Number of Active Search Pages]
siteDB = {
    'Trick Your GF': [7, 4],
    'Make Him Cuckold': [9, 5],
    'She Is Nerdy': [10, 12],
    'Tricky Agent': [11, 4],
}


sceneActorsDB = {
    'Adele Hotness': ['snc162'],
    'Adina': ['darygf050'],
    'Aggie': ['wrygf726', 'wtag728'],
    'Aimee Ryan': ['pfc070'],
    'Akira Drago': ['snc185'],
    'Alaina Dawson': ['crygf009'],
    'Alex Swon': ['snc141'],
    'Alexa Black': ['snc139'],
    'Alexis Crash': ['wrygf499'],
    'Alexis Crystal': ['danc129'],
    'Alice Kelly': ['snc143'],
    'Alice Lee': ['wrygf776', 'wtag770', 'wnc765'],
    'Alice Marshall': ['wrygf930', 'wfc929', 'wtag934', 'wnc936'],
    'Alice Paradise': ['wnc1665'],
    'Alien Fox': ['wnc1625', 'wnc1555'],
    'Alita Angel': ['snc099'],
    'Amalia Davis': ['wnc1560'],
    'Amanda Moore': ['pfc111'],
    'Amber Daikiri': ['wrygf508'],
    'Ami Calienta': ['snc084'],
    'Ananta Shakti': ['wtag893', 'wnc810', 'wnc888'],
    'Andrea Sun': ['darygf057'],
    'Angel Dickens': ['wfc391'],
    'Angel Piaff': ['pfc119'],
    'Angela Vidal': ['wnc1439'],
    'Angie Koks': ['wrygf911'],
    'Angie Moon': ['wtag1050'],
    'Ann Marie': ['wfc715', 'wtag719', 'wnc714'],
    'Anna Krowe': ['snc107'],
    'Anne Angel': ['wtag577'],
    'Annette': ['wtag579'],
    'Annika Seren': ['wrygf451'],
    'April Storm': ['wnc1455'],
    'Ariadna Moon': ['wtag994'],
    'Ariana Shaine': ['wnc1487'],
    'Aruna Aghora': ['wrygf900', 'wfc907', 'wtag955', 'wtag908'],
    'Ashley Woods': ['dafc140'],
    'Aurora Sky': ['snc129'],
    'Azumi Liu': ['snc170'],
    'Baby Mamby': ['snc199'],
    'Bell Knock': ['snc073'],
    'Bella Gray': ['wnc1668', 'afnc004'],
    'Bella Mur': ['wnc1517'],
    'Bernie Svintis': ['irnc009'],
    'Black Angel': ['wnc1597'],
    'Bloom Lambie': ['snc147', 'wnc1564'],
    'Carmen Fox': ['wnc833', 'wfc863', 'wtag892'],
    'Carmen Rodriguez': ['snc197'],
    'Cassidy Klein': ['cfc005'],
    'Chanel Lux': ['wnc1238'],
    'Chloe Blue': ['wrygf526'],
    'Christi Cats': ['wrygf553', 'wtag584'],
    'Clockwork Victoria': ['wnc1629', 'snc120'],
    'Cornelia Quinn': ['wnc1467'],
    'Darcy Dark': ['wnc1590', 'wnc1672'],
    'Dayana Kamil': ['snc136'],
    'Denisa Peterson': ['pfc056'],
    'Donna Keller': ['wfc408'],
    'Dushenka': ['wfc701', 'wtag700', 'wnc699'],
    'Elin Holm': ['wnc1453'],
    'Elisaveta Gulobeva': ['wfc926', 'wtag922'],
    'Eliza Thorne': ['snc117'],
    'Ellie': ['pfc129'],
    'Emily C': ['wnc1676', 'snc203'],
    'Emily Thorne': ['wtag1163'],
    'Emily Wilson': ['snc114'],
    'Emma Brown': ['wfc1089', 'wtag1102'],
    'Emma Fantazy': ['wnc1448'],
    'Eva': ['wrygf865', 'wnc880'],
    'Eva Red': ['wnc1707'],
    'Eveline Neill': ['pfc123'],
    'Evelyn Cage': ['wrygf651', 'wtag644'],
    'Foxy Di': ['wrygf886', 'wrygf828', 'wtag859', 'wnc821'],
    'Foxy Katrina': ['wfc866', 'wtag871', 'wnc872'],
    'Francheska': ['wfc406'],
    'Gina Gerson': ['wrygf622', 'wtag617', 'wnc690'],
    'Gisha Forza': ['wrygf1442', 'snc087'],
    'Gloria Miller': ['wrygf738', 'wnc735'],
    'Glorie': ['darygf052'],
    'Grace Young': ['wfc380'],
    'Grace': ['wfc960'],
    'Hanna Rey': ['wnc1550', 'wnc1622', 'wnc1550'],
    'Hazel Dew': ['wnc1301'],
    'Henna Ssy': ['wnc1599'],
    'Herda Wisky': ['wnc1294'],
    'Holly Molly': ['snc184'],
    'Hungry Fox': ['snc218'],
    'Inga Zolva': ['wrygf747', 'wtag767', 'wnc879', 'wnc746'],
    'Iris Kiss': ['snc165', 'wnc1637'],
    'Isabel Stern': ['wfc1075'],
    'Iva Zan': ['wrygf536', 'wtag558', 'wnc745'],
    'Izi Ashley': ['wfc978', 'wtag980', 'wnc97'],
    'Jane Fox': ['wtag1235'],
    'Jenny Fer': ['wnc1330'],
    'Jenny Love': ['wrygf634', 'wfc607', 'wtag601'],
    'Jenny Manson': ['wtag1324', 'wfc1302'],
    'Jessica Malone': ['wrygf1078', 'wtag1101', 'wnc1086'],
    'Jessica Rox': ['prygf138', 'pfc137'],
    'Jessy Nikea': ['wfc374'],
    'Jolie Butt': ['wnc1703'],
    'Kari Sweet': ['prygf135', 'pfc134'],
    'Karry Slot': ['snc080'],
    'Kate Quinn': ['snc159'],
    'Katrin Tequila': ['wnc1256'],
    'Katty Blessed': ['wnc1176'],
    'Katty West': ['wtag1181', 'wnc1483'],
    'Katya': ['wtag1181', 'wnc758'],
    'Kelly Rouss': ['snc091'],
    'Kendra Cole': ['hrygf002'],
    'Kerry Cherry': ['wnc1284'],
    'Kiara Gold': ['wnc1545'],
    'Kiara Knight': ['crygf002'],
    'Kimberly Mansell': ['wrygf528'],
    'Kira Parvati': ['wtag777', 'wnc778'],
    'Kira Roller': ['wnc1338'],
    'Kira Stone': ['snc171'],
    'Kris the Foxx': ['wnc1593', 'wnc1506'],
    'Kylie Green': ['wnc1614'],
    'Lagoon Blaze': ['snc131'],
    'Lana Broks': ['snc158'],
    'Lana Roy': ['wnc1573'],
    'Lena Love': ['wfc600', 'wtag580'],
    'Li Loo': ['wnc1536'],
    'Lia Chalizo': ['wfc373'],
    'Lia Little': ['snc133'],
    'Light Fairy ': ['wnc1608', 'wnc1525'],
    'Lina Arian Joy': ['wfc954'],
    'Lina Napoli': ['wrygf760', 'wtag772', 'wnc752'],
    'Lindsey Olsen': ['wfc589', 'wtag598'],
    'Liona Levi': ['wrygf663', 'wtag660'],
    'Lita': ['wfc902'],
    'Little Candy': ['wnc1394'],
    'Liza Kolt': ['wtag741', 'wnc732'],
    'Lizaveta Kay': ['wrygf733'],
    'Lizi Smoke': ['snc122'],
    'Lola Shine': ['wnc1173'],
    'Lorrelai Gold': ['wnc816'],
    'Lottie Magne': ['snc111'],
    'Luna Haze': ['snc187'],
    'Luna Umberlay': ['wnc1651'],
    'Madlen': ['wnc1430'],
    'Maggie Gold': ['pfc057'],
    'Margarita C': ['wfc940', 'wnc941'],
    'Margo Von Teese': ['wnc1741'],
    'Maribel': ['wfc367'],
    'Mary Solaris': ['wnc1500'],
    'Matty': ['irnc003'],
    'Mazy Teen': ['pfc069'],
    'Megan Promesita': ['pfc104'],
    'Megan Venturi': ['wnc1539'],
    'Melissa Benz': ['wfc1276'],
    'Meow Miu': ['wnc1742'],
    'Mia Hilton': ['pfc065'],
    'Mia Piper': ['snc182', 'snc240'],
    'Mia Reese': ['wtag887', 'wnc890'],
    'Michelle Can': ['wfc1392', 'wnc1354'],
    'Mila Gimnasterka': ['wfc1100'],
    'Milana Milka': ['wnc1639'],
    'Milena Briz': ['snc195'],
    'Mileva': ['irnc005'],
    'Milka Feer': ['snc214'],
    'Mirta': ['wfc919'],
    'Molly Brown': ['snc088'],
    'Molly Manson': ['crygf013'],
    'Monica Rise': ['crygf011'],
    'Monika Jelolt': ['achnc01'],
    'Monroe Fox': ['wnc1671', 'wnc1587'],
    'Nataly Gold': ['wtag594'],
    'Natalya C': ['wtag649'],
    'Nelya Smalls': ['wnc1273'],
    'Nesti': ['wfc696', 'wnc697'],
    'Nika A': ['snc223'],
    'Nika Charming': ['wnc1513'],
    'Nikki Hill': ['snc094'],
    'Norah Nova': ['cfc008'],
    'Oliva Grace': ['wrygf991', 'wtag996'],
    'Olivia Cassi': ['snc150'],
    'Petia': ['pfc062'],
    'Petra Larkson': ['pfc141'],
    'Pinky Breeze': ['snc095'],
    'Queenlin': ['snc155'],
    'Rahyndee James': ['cfc003'],
    'Raquel Rimma': ['wtag1134'],
    'Rebeca Fox': ['snc194'],
    'Rebecca Rainbow': ['wrygf1201', 'wtag1193', 'wnc1220'],
    'Regina Rich': ['snc177', 'wnc1635'],
    'Renata Fox': ['wfc1215'],
    'Ria Koks': ['wnc1377'],
    'Rin White': ['wnc1679', 'wnc1584'],
    'Rita Jalace': ['wrygf633', 'wtag643', 'wnc740'],
    'Rita Lee': ['wnc1369'],
    'Rita Milan': ['wrygf870', 'wfc968', 'wtag961'],
    'Rita': ['wtag1232'],
    'Rosa Mentoni': ['wfc932'],
    'Roxy Lips': ['wnc1458'],
    'Sabrina Moor': ['wfc869', 'wtag995'],
    'Salomja A': ['wtag803'],
    'Sandra Wellness': ['wnc1159'],
    'Sara Redz': ['wtag804', 'wnc800'],
    'Sara Rich': ['wnc1647', 'snc174'],
    'Selena Stuart': ['wrygf798', 'wnc801', 'snc104'],
    'Sheeloves': ['snc153'],
    'Sherry E': ['wtag570'],
    'Shirley Harris': ['wrygf485'],
    'Shrima Malati': ['wrygf993', 'wtag997'],
    'Sofi Goldfinger': ['wtag1130'],
    'Sofy Soul': ['wtag1252'],
    'Soni': ['wrygf648', 'wtag610'],
    'Sonya Sweet': ['wfc1198', 'wtag1204', 'wnc1196'],
    'Stacy Snake': ['wrygf427'],
    'Stasia Si': ['wnc1609', 'wnc1533'],
    'Stefanie Moon': ['wfc1107', 'wtag1122'],
    'Stefany Kyler': ['wnc1569'],
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
    'Vasilisa Lisa': ['wnc1633'],
    'Veronika Fare': ['wnc1315'],
    'Vika Lita': ['wfc1480'],
    'Vika Volkova': ['wtag1036'],
    'Viola Weber': ['snc189'],
    'Violette Pink': ['danc111'],
    'Vivian Grace': ['wnc1654'],
    'Zena Little': ['dafc139', 'danc110'],
}
