import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    parts = searchData.title.split(' ', 1)

    if len(parts) == 1 and searchData.filename == searchData.title:
        Log('No scene name')
        return results
    elif len(parts) == 1 and searchData.filename != searchData.title:
        parts.append(searchData.filename)

    userID = parts[0]
    sceneTitle = parts[1]

    parts = sceneTitle.split(' ', 1)
    sceneID = None
    if len(parts) == 1 and unicode(parts[0]).isdigit():
        sceneID = parts[0]

    searchData.encoded = urllib.quote(sceneTitle)

    if sceneID:
        sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + '%s/%s/' % (userID, sceneID)
        req = PAutils.HTTPRequest(sceneURL)
        if req.ok:
            detailsPageElements = HTML.ElementFromString(req.text)

            curID = PAutils.Encode(sceneURL)
            titleNoFormatting = getCleanTitle(detailsPageElements.xpath('//h3')[0].text_content())
            subSite = detailsPageElements.xpath('//title')[0].text_content().split('-')[0].strip()

            score = 100

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [Clips4Sale/%s]' % (titleNoFormatting, subSite), score=score, lang=lang))

    url = PAsearchSites.getSearchSearchURL(siteNum) + userID + '/*/Cat0-AllCategories/Page1/SortBy-bestmatch/Limit50/search/' + searchData.encoded
    req = PAutils.HTTPRequest(url)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[contains(@class, "clipWrapper")]//section[@id]'):
        sceneURL = searchResult.xpath('.//h3//a/@href')[0]
        curID = PAutils.Encode(sceneURL)

        titleNoFormatting = getCleanTitle(searchResult.xpath('.//h3')[0].text_content())
        subSite = searchResult.xpath('//title')[0].text_content().strip()

        score = 100 - Util.LevenshteinDistance(sceneTitle.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [Clips4Sale/%s]' % (titleNoFormatting, subSite), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieCastCrew, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    userID = sceneURL.split('/')[-3]
    sceneID = sceneURL.split('/')[-2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    movieGenres.clearGenres()
    movieCastCrew.clearActors()

    # Title
    metadata.title = getCleanTitle(detailsPageElements.xpath('//h3')[0].text_content())

    # Summary
    summary = detailsPageElements.xpath('//div[@class="individualClipDescription"]')[0].text_content().strip()
    summary = summary.split('--SCREEN SIZE')[0].split('--SREEN SIZE')[0].strip()  # K Klixen
    summary = summary.split('window.NREUM')[0].replace('**TOP 50 CLIP**', '').replace('1920x1080 (HD1080)', '').strip()  # MHBHJ
    metadata.summary = summary

    # Studio
    metadata.studio = 'Clips4Sale'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = detailsPageElements.xpath('//title')[0].text_content().split('-')[1].split('|')[0].strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//span[contains(., "Added:")]//span')[0].text_content().split()[0].strip()
    if date:
        date_object = datetime.strptime(date, '%m/%d/%y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actors / Genres
    # Main Category
    cat = detailsPageElements.xpath('//div[contains(@class, "clip_details")]//div[contains(., "Category:")]//a')[0].text_content().strip().lower()
    movieGenres.addGenre(cat)
    # Related Categories / Keywords
    genreList = []
    for genreLink in detailsPageElements.xpath('//span[@class="relatedCatLinks"]//a'):
        genreName = genreLink.text_content().strip().lower()

        genreList.append(genreName)
    # Add Actors

    #  CherryCrush
    if '57445' in userID:
        genreList.remove('cherry')
        genreList.remove('cherrycrush')

    #  Klixen
    elif '7373' in userID:
        actors = detailsPageElements.xpath('//span[contains(., "Keywords:")]/following-sibling::span//a')
        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            actorPhotoURL = ''

            genreList.remove(actorName)
            movieCastCrew.addActor(actorName, actorPhotoURL)

    #  AAA wicked
    elif '40156' in userID:
        if 'mistress candide' in genreList:
            movieCastCrew.addActor('Mistress Candice', '')
            genreList.remove('mistress candice')

    #  Aballs and cock crushing sexbomb
    elif '14662' in userID:
        if 'Alina' in metadata.title or 'Alina' in metadata.summary:
            movieCastCrew.addActor('Mistress Alina', '')

    #  Adrienne Adora
    elif '62839' in userID:
        movieCastCrew.addActor('Adrienne Adora', '')

    #  Amazon Goddess Harley
    elif '101989' in userID:
        if 'goddess harley' in genreList:
            movieCastCrew.addActor('Goddess Harley', '')
            genreList.remove('goddess harley')
        if 'amazon goddess harley' in genreList:
            movieCastCrew.addActor('Goddess Harley', '')
            genreList.remove('amazon goddess harley')

    #  AnikaFall
    elif '123317' in userID:
        movieCastCrew.addActor('Anika Fall', '')
        if 'anikafall' in genreList:
            movieCastCrew.addActor('Anika Fall', '')
            genreList.remove('anikafall')
        if 'anika fall' in genreList:
            movieCastCrew.addActor('Anika Fall', '')
            genreList.remove('anika fall')
        if 'goddess anika fall' in genreList:
            movieCastCrew.addActor('Anika Fall', '')
            genreList.remove('goddess anika fall')

    #  Ashley Albans Fetish Fun
    elif '71774' in userID:
        if 'ashley alban' in genreList:
            movieCastCrew.addActor('Ashley Alban', '')
            genreList.remove('ashley alban')

    #  AstroDomina
    elif '56587' in userID:
        if 'astrodomina' in genreList:
            movieCastCrew.addActor('Astro Domina', '')
            genreList.remove('astrodomina')
        if 'alrik angel' in genreList:
            movieCastCrew.AddActor('Alrik Angel', '')
            genreList.remove('alrik angel')
        if 'casey calvert' in genreList:
            movieCastCrew.AddActor('casey calvert', '')
            genreList.remove('casey calvert')
        if 'Ellie Idol' in metadata.title:
            movieCastCrew.addActor('Ellie Idol', '')
        if 'Ellie Idol' in genreList:
            movieCastCrew.addActor('Ellie Idol', '')
            genreList.remove('ellie idol')
        if 'Astrodomina' in metadata.title or 'AstroDomina' in metadata.title:
            movieCastCrew.addActor('Astro Domina', '')
        if 'StellarLoving' in metadata.title:
            movieCastCrew.addActor('Stellar Loving', '')

    #  Ball Busting Chicks
    elif '8565' in userID:
        if 'hera' in genreList:
            movieCastCrew.addActor('Domina Hera', '')
            genreList.remove('hera')
        if 'amy' in genreList:
            movieCastCrew.addActor('Domina Amy', '')
            genreList.remove('amy')

    #  Ballbusting World PPV
    elif '87149' in userID:
        if 'Tasha Holz' in metadata.summary or 'Tasha' in metadata.summary:
            movieCastCrew.addActor('Tasha Holz', '')

    #  Bare Back Studios
    elif '35625' in userID:
        #  Genre list match
        if 'cory chase' in genreList:
            movieCastCrew.addActor('Cory Chase', '')
            genreList.remove('cory chase')
        if 'luke longly' in genreList:
            movieCastCrew.addActor('Luke Longly', '')
            genreList.remove('luke longly')
        if 'coco vandi' in genreList:
            movieCastCrew.addActor('Coco Vandi', '')
            genreList.remove('coco vandi')
        if 'vanessa cage' in genreList:
            movieCastCrew.addActor('Vanessa Cage', '')
            genreList.remove('vanessa cage')
        if 'melanie hicks' in genreList:
            movieCastCrew.addActor('Melanie Hicks', '')
            genreList.remove('melanie hicks')
        if 'alice visby' in genreList:
            movieCastCrew.addActor('Alice Visby', '')
            genreList.remove('alice visby')
        if 'aimee cambridge' in genreList:
            movieCastCrew.addActor('Aimee Cambridge', '')
            genreList.remove('aimee cambridge')
        if 'bailey base' in genreList:
            movieCastCrew.addActor('Bailey Base', '')
            genreList.remove('bailey base')
        if 'brooklyn chase' in genreList:
            movieCastCrew.addActor('Brooklyn Chase', '')
            genreList.remove('brooklyn chase')
        if 'johnny kidd' in genreList:
            movieCastCrew.addActor('Johnny Kidd', '')
            genreList.remove('johnny kidd')
        if 'clover baltimore' in genreList:
            movieCastCrew.addActor('Clover Baltimore', '')
            genreList.remove('clover baltimore')
        if 'dixie lynn' in genreList:
            movieCastCrew.addActor('Dixie Lynn', '')
            genreList.remove('dixie lynn')
        if 'gabriella lopez' in genreList:
            movieCastCrew.addActor('Gabriella Lopez', '')
            genreList.remove('gabriella lopez')
        if 'kitten latenight' in genreList:
            movieCastCrew.addActor('Kitten Latenight', '')
            genreList.remove('kitten latenight')
        if 'lexxi steele' in genreList:
            movieCastCrew.addActor('Lexxi Steele', '')
            genreList.remove('lexxi steele')
        if 'maggie green' in genreList:
            movieCastCrew.addActor('Maggie Green', '')
            genreList.remove('maggie green')
        if 'michele james' in genreList:
            movieCastCrew.addActor('Michele James', '')
            genreList.remove('michele james')
        if 'skylar vox' in genreList:
            movieCastCrew.addActor('Skylar Vox', '')
            genreList.remove('skylar vox')

        #  Metadata match
        if 'cory chase' in metadata.summary:
            movieCastCrew.addActor('Cory Chase', '')
        if 'luke longly' in metadata.summary:
            movieCastCrew.addActor('Luke Longly', '')
        if 'coco vandi' in metadata.summary:
            movieCastCrew.addActor('Coco Vandi', '')
        if 'vanessa cage' in metadata.summary:
            movieCastCrew.addActor('Vanessa Cage', '')
        if 'melanie hicks' in metadata.summary:
            movieCastCrew.addActor('Melanie Hicks', '')
        if 'alice visby' in metadata.summary:
            movieCastCrew.addActor('Alice Visby', '')
        if 'aimee cambridge' in metadata.summary:
            movieCastCrew.addActor('Aimee Cambridge', '')
        if 'bailey base' in metadata.summary:
            movieCastCrew.addActor('Bailey Base', '')
        if 'brooklyn chase' in metadata.summary:
            movieCastCrew.addActor('Brooklyn Chase', '')
        if 'johnny kidd' in metadata.summary:
            movieCastCrew.addActor('Johnny Kidd', '')
        if 'clover baltimore' in metadata.summary:
            movieCastCrew.addActor('Clover Baltimore', '')
        if 'dixie lynn' in metadata.summary:
            movieCastCrew.addActor('Dixie Lynn', '')
        if 'gabriella lopez' in metadata.summary:
            movieCastCrew.addActor('Gabriella Lopez', '')
        if 'kitten latenight' in metadata.summary:
            movieCastCrew.addActor('Kitten Latenight', '')
        if 'lexxi steele' in metadata.summary:
            movieCastCrew.addActor('Lexxi Steele', '')
        if 'maggie green' in metadata.summary:
            movieCastCrew.addActor('Maggie Green', '')
        if 'michele james' in metadata.summary:
            movieCastCrew.addActor('Michele James', '')
        if 'skylar vox' in metadata.summary:
            movieCastCrew.addActor('Skylar Vox', '')

    #  Best Latin ASS on the WEB!
    elif '27570!' in userID:
        if 'goddess sandra' in genreList:
            movieCastCrew.addActor('Sandra Latina', '')
            genreList.remove('goddess sandra')
        if 'sandra latina' in genreList:
            movieCastCrew.addActor('Sandra Latina', '')
            genreList.remove('sandra latina')
        if 'latinsandra' in genreList:
            movieCastCrew.addActor('Sandra Latina', '')
            genreList.remove('latinsandra')
        if 'latin sandra' in genreList:
            movieCastCrew.addActor('Sandra Latina', '')
            genreList.remove('latin sandra')
        if 'latina sandra' in genreList:
            movieCastCrew.addActor('Sandra Latina', '')
            genreList.remove('latina sandra')
        if 'hotwife sandra' in genreList:
            movieCastCrew.addActor('Sandra Latina', '')
            genreList.remove('hotwife sandra')

    #  Bikini Blackmail Ballbust Lyne
    elif '14404' in userID:
        if 'princess lyne' in genreList.summary:
            movieCastCrew.addActor('Princess Lyne', '')
            genreList.remove('princess lyne')

    #  Brat Doll Amanda Powers
    elif '69131' in userID:
        movieCastCrew.addActor('Amanda Powers', '')

    #  Brat Princess 2
    elif '21233' in userID:
        #  Genre list match
        if 'natalya vega' in genreList:
            movieCastCrew.addActor('Natalya Vega', '')
            genreList.remove('natalya vega')
        if 'kat soles' in genreList:
            movieCastCrew.addActor('Kat Soles', '')
            genreList.remove('kat soles')
        if 'macy cartel' in genreList:
            movieCastCrew.addActor('Macy Cartel', '')
            genreList.remove('macy cartel')
        if 'amadahy' in genreList:
            movieCastCrew.addActor('Goddess Amadahy', '')
            genreList.remove('amadahy')
        if 'goddess amadahy' in genreList:
            movieCastCrew.addActor('Goddess Amadahy', '')
            genreList.remove('amadahy')
            genreList.remove('goddess amadahy')
        if 'jennifer' in genreList:
            movieCastCrew.addActor('Empress Jennifer', '')
            genreList.remove('jennifer')
        if 'empress jennifer' in genreList:
            movieCastCrew.addActor('Empress Jennifer', '')
            genreList.remove('empress jennifer')
        #  Metadata match
        if 'Cali Carter' in metadata.summary:
            movieCastCrew.addActor('Cali Carter', '')
        if 'Kenzie Taylor' in metadata.summary:
            movieCastCrew.addActor('Kenzie Taylor', '')
        if 'Alexa' in metadata.summary:
            movieCastCrew.addActor('Alexa', '')
        if 'Natalya' in metadata.summary:
            movieCastCrew.addActor('Natalya Vega', '')
        if 'Jessica' in metadata.summary:
            movieCastCrew.addActor('Jessica', '')
        # title match
        if 'Alexis' in metadata.title:
            movieCastCrew.addActor('Alexis Grace', '')
        if 'Amadahy' in metadata.title:
            movieCastCrew.addActor('Goddess Amadahy', '')
        if 'Jade' in metadata.title:
            movieCastCrew.addActor('Jade Indica', '')

    #  Brat Princess Natalya
    elif '116956' in userID:
        movieCastCrew.addActor('Princess Natalya', '')
        #  Genre list match
        if 'princess natalya' in genreList:
            genreList.remove('princess natalya')

    #  Brat Princess POV
    elif '5590' in userID:
        #  Genre list match
        if 'brandi' in genreList:
            movieCastCrew.addActor('Princess Brandi', '')
            genreList.remove('brandi')
        if 'kelli' in genreList:
            movieCastCrew.addActor('Princess Kelli', '')
            genreList.remove('kelli')

        #  Metadata match
        if 'Brandi' in metadata.summary:
            movieCastCrew.addActor('Princess Brandi', '')
        if 'Princess Kelli' in metadata.summary:
            movieCastCrew.addActor('Princess Kelli', '')
        if 'Jennifer' in metadata.summary:
            movieCastCrew.addActor('Jennifer', '')
        if 'Mia' in metadata.summary:
            movieCastCrew.addActor('Mia', '')

    #  Bratty Ashley Sinclair and Friends
    elif '62843' in userID:
        movieCastCrew.addActor('Ashley Sinclair', '')

    # Bratty Bunny
    elif '35587' in userID:
        movieCastCrew.addActor('Bratty Bunny', '')
        # Clean the title to remove "Bratty Bunny - " and keep everything else
        metadata.title = re.sub(r'^.*-\s*(.*)$', r'\1', metadata.title)

    #  Bratty Foot Girls
    elif '40537' in userID:
        #  metadata match
        if 'Sasha Foxxx' in metadata.summary:
            movieCastCrew.addActor('Sasha Foxxx', '')

    #  Bratty Jamie Productions
    elif '29810' in userID:
        movieCastCrew.addActor('Bratty Jamie', '')

    #  Bratty Princess Lisa
    elif '34346' in userID:
        if 'bratty princess lisa' in genreList:
            movieCastCrew.addActor('Lisa Jordan', '')
            genreList.remove('bratty princess lisa')
        if 'lisa jordan' in genreList:
            movieCastCrew.addActor('Lisa Jordan', '')
            genreList.remove('lisa jordan')

    #  Brie White
    elif 'Brie White' in tagline:
        movieCastCrew.addActor('Brie White', '')
        if 'brie white' in genreList:
            movieCastCrew.addActor('Brie White', '')
            genreList.remove('brie white')
        if 'larkin love' in genreList:
            movieCastCrew.addActor('Larkin Love', '')
            genreList.remove('larkin love')

    #  British Bratz
    elif '73287' in userID:
        #  Genre list match
        if 'lizzie murphy' in genreList:
            movieCastCrew.addActor('Lizzie Murphy', '')
            genreList.remove('lizzie murphy')
        if 'goddess melissa' in genreList:
            movieCastCrew.addActor('Goddess Melissa', '')
            genreList.remove('goddess melissa')
        if 'princess chloe' in genreList:
            movieCastCrew.addActor('Princess Chloe', '')
            genreList.remove('princess chloe')
        if 'princess rosie' in genreList:
            movieCastCrew.addActor('Princess Rosie Lee', '')
            genreList.remove('princess rosie')
        if 'princess rosie lee' in genreList:
            movieCastCrew.addActor('Princess Rosie Lee', '')
            genreList.remove('princess rosie lee')
        if 'rosie lee' in genreList:
            movieCastCrew.addActor('Princess Rosie Lee', '')
            genreList.remove('rosie lee')
        if 'jasmine jones' in genreList:
            movieCastCrew.addActor('Jasmine Jones', '')
            genreList.remove('jasmine jones')
        if 'elle pharrell' in genreList:
            movieCastCrew.addActor('Elle Pharrel', '')
            genreList.remove('elle pharrell')
        if 'danni maye' in genreList:
            movieCastCrew.addActor('Danni Maye', '')
            genreList.remove('danni maye')
        if 'princess danni' in genreList:
            movieCastCrew.addActor('Princess Danni', '')
            genreList.remove('princess danni')
        if 'princess stephanie' in genreList:
            movieCastCrew.addActor('Princess Stephanie', '')
            genreList.remove('princess stephanie')
        if 'jessie jenson' in genreList:
            movieCastCrew.addActor('Jessie Jenson', '')
            genreList.remove('jessie jenson')
        if 'diva boss ivy' in genreList:
            movieCastCrew.addActor('Diva Boss Ivy', '')
            genreList.remove('diva boss ivy')
        if 'stephanie wright' in genreList:
            movieCastCrew.addActor('Stephanie Wright', '')
            genreList.remove('stephanie wright')
        if 'lady natt' in genreList:
            movieCastCrew.addActor('Lady Natt', '')
            genreList.remove('lady natt')
        #  Metadata match
        if 'Princess Stephanie' in metadata.title or 'Princess Stephanie' in metadata.summary:
            movieCastCrew.addActor('Princess Stephanie', '')
        if 'Princess Kiki' in metadata.title or 'Princess Kiki' in metadata.summary:
            movieCastCrew.addActor('Princess Kiki', '')
        if 'Vicky' in metadata.title or 'Vicky' in metadata.summary:
            movieCastCrew.addActor('Vicky Narni', '')

    #  Brittany Marie
    elif '91727' in userID:
        movieCastCrew.addActor('Brittany Marie', '')
        if 'brittany marie' in genreList:
            genreList.remove('brittany marie')

    #  Brooke Marie's Fantasies
    elif '55685' in userID:
        movieCastCrew.addActor('Brooke Marie', '')
        if 'brooke marie' in genreList:
            movieCastCrew.addActor('Brooke Marie', '')
            genreList.remove('brooke marie')

    #  Butt3rflyforU Fantasies
    elif '95917' in userID:
        if 'rae knight' in genreList:
            movieCastCrew.addActor('Rae Knight', '')
            genreList.remove('rae knight')
        if 'butt3rflyforu' in genreList:
            genreList.remove('butt3rflyforu')

    #  Candy Glitter
    elif '89733' in userID:
        if 'candyglitter' in genreList:
            movieCastCrew.addActor('Candy Glitter', '')
            genreList.remove('candyglitter')
        if 'candy glitter' in genreList:
            movieCastCrew.addActor('Candy Glitter', '')
            genreList.remove('candy glitter')

    #  Carlie
    elif '120440' in userID:
        movieCastCrew.addActor('Carlie', '')

    #  Ceara Lynch Humiliatrix
    elif '16312' in userID:
        movieCastCrew.addActor('Ceara Lynch', '')
        if 'ceara' in genreList:
            movieCastCrew.addActor('Ceara Lynch', '')
            genreList.remove('ceara')
        if 'ceara lynch' in genreList:
            movieCastCrew.addActor('Ceara Lynch', '')
            genreList.remove('ceara lynch')
        if 'princess ceara' in genreList:
            movieCastCrew.addActor('Ceara Lynch', '')
            genreList.remove('princess ceara')
        if 'bratty bunny' in genreList:
            movieCastCrew.addActor('Bratty Bunny', '')
            genreList.remove('bratty bunny')

    #  Charlotte Stokely
    elif '61269' in userID:
        if 'goddess charlotte stokely' in genreList:
            movieCastCrew.addActor('Charlotte Stokely', '')
            genreList.remove('goddess charlotte stokely')

    elif 'chicks' in tagline:
        #  Metadata match
        if 'Sophia' in metadata.summary:
            movieCastCrew.addActor('Mistress Sophia', '')

    #  Christy Berrie
    elif '94447' in userID:
        movieCastCrew.addActor('Christy Berrie', '')

    #  Club Stiletto Femdom
    elif '896' in userID:
        #  Genre list match
        if 'mistress kandy kink' in genreList:
            movieCastCrew.addActor('Mistress Kandy Kink', '')
            genreList.remove('mistress kandy kink')
        if 'mistress kandy' in genreList:
            movieCastCrew.addActor('Mistress Kandy', '')
            genreList.remove('mistress kandy')
        if 'princess lily' in genreList:
            movieCastCrew.addActor('Princess Lily', '')
            genreList.remove('princess lily')
        if 'miss jasmine' in genreList:
            movieCastCrew.addActor('Miss Jasmine', '')
            genreList.remove('miss jasmine')

        #  Summary match
        if 'Princess Jemma' in metadata.summary:
            movieCastCrew.addActor('Princess Jemma', '')

    #  Countess Crystal Knight
    elif '96651' in userID:
        if 'crystal knight' in genreList:
            movieCastCrew.addActor('Crystal Knight', '')
            genreList.remove('crystal knight')

    #  Cruel City
    elif '111474' in userID:
        if 'Mistress Julia' in metadata.summary:
            movieCastCrew.addActor('Mistress Julia', '')

    #  Cruel Girlfriend
    elif '34982' in userID:
        if 'jessie jensen' in genreList:
            movieCastCrew.addActor('Jessie Jensen', '')
            genreList.remove('jessie jensen')

    #  CRUEL MISTRESSES
    elif '39213' in userID:
        if 'Lady Ann' in metadata.summary:
            movieCastCrew.addActor('Lady Ann', '')
        if 'Mistress Anette' in metadata.summary:
            movieCastCrew.addActor('Mistress Anette', '')
        if 'Mistress Amanda' in metadata.summary:
            movieCastCrew.addActor('Mistress Amanda', '')
        if 'Mistress Ariel' in metadata.summary:
            movieCastCrew.addActor('Mistress Ariel', '')
        if 'Mistress Kittina' in metadata.summary:
            movieCastCrew.addActor('Mistress Kittina', '')

    #  Cruel Seductress
    elif '66097' in userID:
        movieCastCrew.addActor('Goddess Victoria', '')

    #  Cruel  Unusual FemDom
    elif '5751' in userID:
        #  Genre List
        if 'kiki klout' in genreList:
            movieCastCrew.addActor('Kiki Klout', '')
            genreList.remove('kiki klout')
        if 'megan jones' in genreList:
            movieCastCrew.addActor('Megan Jones', '')
            genreList.remove('megan jones')
        if 'kylie rogue' in genreList:
            movieCastCrew.addActor('Kylie Rogue', '')
            genreList.remove('kylie rogue')
        if 'dava foxx' in genreList:
            movieCastCrew.addActor('Dava Foxx', '')
            genreList.remove('dava foxx')
        if 'alexis grace' in genreList:
            movieCastCrew.addActor('Alexis Grace', '')
            genreList.remove('alexis grace')
        if 'jean bardot' in genreList:
            movieCastCrew.addActor('Jean Bardot', '')
            genreList.remove('jean Bardot')
        if 'stevie shae' in genreList:
            movieCastCrew.addActor('Stevie Shae', '')
            genreList.remove('stevie shae')
        if 'stevie shay' in genreList:
            movieCastCrew.addActor('Stevie Shay', '')
            genreList.remove('stevie shay')
        if 'goddess stevie shae' in genreList:
            movieCastCrew.addActor('Goddess Stevie Shae', '')
            genreList.remove('goddess stevie shae')
        if 'victoria saphire' in genreList:
            movieCastCrew.addActor('Victoria Saphire', '')
            genreList.remove('victoria saphire')
        if 'victoria sapphire' in genreList:
            movieCastCrew.addActor('Victoria Saphire', '')
            genreList.remove('victoria sapphire')
        if 'hailey young' in genreList:
            movieCastCrew.addActor('Hailey Young', '')
            genreList.remove('hailey young')
        if 'holly halston' in genreList:
            movieCastCrew.addActor('Holly Halston', '')
            genreList.remove('holly halston')
        if 'mistress holly halston' in genreList:
            movieCastCrew.addActor('Mistress Holly Halston', '')
            genreList.remove('mistress holly halston')
        if 'mistress holly' in genreList:
            movieCastCrew.addActor('Mistress Holly', '')
            genreList.remove('mistress holly')
        if 'randy moore' in genreList:
            movieCastCrew.addActor('Randy Moore', '')
            genreList.remove('randy moore')
        if 'deanna storm' in genreList:
            movieCastCrew.addActor('Deanna Storm', '')
            genreList.remove('deanna storm')
        if 'ashley edmunds' in genreList:
            movieCastCrew.addActor('Ashley Edmunds', '')
            genreList.remove('ashley edmunds')
        if 'ashely edmunds' in genreList:
            movieCastCrew.addActor('Ashely Edmunds', '')
            genreList.remove('ashely edmunds')
        if 'ashley edmonds' in genreList:
            movieCastCrew.addActor('Ashley edmonds', '')
            genreList.remove('ashley edmonds')
        if 'goddess ashley edmunds' in genreList:
            movieCastCrew.addActor('Goddess Ashley Edmunds', '')
            genreList.remove('goddess ashley edmunds')
        if 'mistress ashley' in genreList:
            movieCastCrew.addActor('Mistress Ashley', '')
            genreList.remove('mistress ashley')
        if 'shay evans' in genreList:
            movieCastCrew.addActor('Shay Evans', '')
            genreList.remove('shay evans')
        if 'kelly diamond' in genreList:
            movieCastCrew.addActor('Kelly Diamond', '')
            genreList.remove('kelly diamond')
        if 'bella reese' in genreList:
            movieCastCrew.addActor('Bella Reese', '')
            genreList.remove('bella reese')
        if 'bella ink' in genreList:
            movieCastCrew.addActor('Bella Ink', '')
            genreList.remove('bella ink')
        if 'raven eve' in genreList:
            movieCastCrew.addActor('Raven Eve', '')
            genreList.remove('raven eve')
        if 'kitty carrera' in genreList:
            movieCastCrew.addActor('Kitty Carrera', '')
            genreList.remove('kitty carrera')
        if 'goddess brianna' in genreList:
            movieCastCrew.addActor('Goddess Brianna', '')
            genreList('goddess brianna')
        if 'kendra james' in genreList:
            movieCastCrew.addActor('Kendra James', '')
            genreList.remove('kendra james')

        #  Summary List
        if 'Goddess Brianna' in metadata.summary:
            movieCastCrew.addActor('Goddess Brianna', '')
        if 'Goddess Hailey' in metadata.summary:
            movieCastCrew.addActor('Goddess Hailey', '')
        if 'Jean Bardot' in metadata.summary:
            movieCastCrew.addActor('Jean Bardot', '')
        if 'Simone Kross' in metadata.summary:
            movieCastCrew.addActor('Simone Kross', '')
        if 'Mistress Alexis' in metadata.summary:
            movieCastCrew.addActor('Mistress Alexis', '')
        if 'Mistress Candance' in metadata.summary:
            movieCastCrew.addActor('Mistress Candence', '')
        if 'Mistress Allison' in metadata.summary:
            movieCastCrew.addActor('Mistress Allison', '')
        if 'Mistress Megan' in metadata.summary or 'Megan' in metadata.summary:
            movieCastCrew.addActor('Mistress Megan', '')
        if 'Kendra James' in metadata.summary:
            movieCastCrew.addActor('Kendra James', '')
        if 'Goddess Victoria' in metadata.summary or 'Victoria Saphire' in metadata.summary or 'Victoria Sapphire' in metadata.summary:
            movieCastCrew.addActor('Goddess Victoria', '')
        if 'Mistress Coral' in metadata.summary:
            movieCastCrew.addActor('Mistress Coral', '')
        if 'Mistress Megan Jones' in metadata.summary:
            movieCastCrew.addActor('Mistress Megan jones', '')
        if 'Princess Stevie' in metadata.summary or 'Stevie' in metadata.summary:
            movieCastCrew.addActor('Princess Stevie', '')
        if 'Goddess Holly' in metadata.summary or 'Holly' in metadata.summary:
            movieCastCrew.addActor('Goddess Holly', '')
        if 'Alexis Grace' in metadata.summary:
            movieCastCrew.addActor('Alexis Grace', '')
        if 'Mistress Heidi' in metadata.summary or 'Heidi' in metadata.summary:
            movieCastCrew.addActor('Mistress Heidi', '')
        if 'Mistress Varla' in metadata.summary:
            movieCastCrew.addActor('Mistress Varla', '')
        if 'Goddess Skyler' in metadata.summary or 'Skyler' in metadata.summary:
            movieCastCrew.addActor('Goddess Skyler', '')
        if 'Goddess Hailey' in metadata.summary or 'Hailey' in metadata.summary:
            movieCastCrew.addActor('Goddess Hailey', '')
        if 'Mistress Raina' in metadata.summary or 'Raina' in metadata.summary:
            movieCastCrew.addActor('Mistress Raina', '')
        if 'Goddess Ashley' in metadata.summary or 'Princess Ashley' in metadata.summary or 'Mistress Ashley' in metadata.summary or 'Ashley' in metadata.summary:
            movieCastCrew.addActor('Mistress Ashley', '')
        if 'Stevie Shay' in metadata.summary:
            movieCastCrew.addActor('Stevie Shay', '')
        if 'Kelly Diamon' in metadata.summary:
            movieCastCrew.addActor('Kelly Diamond', '')
        if 'Tatiana' in metadata.summary:
            movieCastCrew.addActor('Mistress Tatiana', '')
        if 'Mistress Bella' in metadata.summary:
            movieCastCrew.addActor('Mistress Bella', '')

    #  CUCKOLD BRAZIL
    elif '89785' in userID:
        if 'Mistress Megan' in metadata.summary:
            movieCastCrew.addActor('Mistress Megan', '')

    #  Cuckoldress Cameron and Friends
    elif '80009' in userID:
        #  Genre list match
        if 'cali carter' in genreList:
            movieCastCrew.addActor('Cali Carter', '')
            genreList.remove('cali carter')
        if 'sadie holmes' in genreList:
            movieCastCrew.addActor('Sadie Holmes', '')
            genreList.remove('sadie holmes')
        if 'vienna' in genreList:
            movieCastCrew.addActor('Vienna', '')
            genreList.remove('vienna')

    #  DANGEROUS TEMPTATION
    elif '34502' in userID:
        if 'goddess celine' in genreList:
            movieCastCrew.addActor('Goddess Celine', '')
            genreList.remove('goddess celine')

    #  DANIELLE MAYE XXX
    elif '58355' in userID:
        if 'dani' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('dani')
        if 'danielle' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('danielle')
        if 'dani maye' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('dani maye')
        if 'danielle maye' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('danielle maye')

    #  Darias Fetish KingDom
    elif '16582' in userID:
        movieCastCrew.addActor('Goddess Daria', '')
        if 'goddess daria' in genreList:
            movieCastCrew.addActor('Goddess Daria', '')
            genreList.remove('goddess daria')

    #  Diane Andrews
    elif '47036' in userID:
        movieCastCrew.addActor('Diane Andrews', '')
        if 'milf diane' in genreList:
            genreList.remove('milf diane')
        if 'milf diane andrews vids' in genreList:
            genreList.remove('milf diane andrews vids')
        if 'diane andrews' in genreList:
            genreList.remove('diane andrews')

    #  Divine Goddess Jessica
    elif '55619' in userID:
        movieCastCrew.addActor('Goddess Jessica', '')

    #  DomNation
    elif '69281' in userID:
        if 'snow mercy' in genreList:
            movieCastCrew.addActor('Snow Mercy', '')
            genreList.remove('snow mercy')

    #  Empress Elle
    elif '125477' in userID:
        movieCastCrew.addActor('Empress Elle', '')

    #  EMPRESS JENNIFER
    elif '78787' in userID:
        movieCastCrew.addActor('Empress Jennifer', '')

    #  Eva de Vil
    elif '122965' in userID:
        movieCastCrew.addActor('Eva de Vil', '')

    #  Explore With Ivy Starshyne
    elif '71434' in userID:
        movieCastCrew.addActor('Ivy Starshyne', '')
        if 'ivy starshyne' in genreList:
            genreList.remove('ivy starshyne')
        if 'khandi redd' in genreList:
            movieCastCrew.addActor('Khandi Redd', '')
            genreList.remove('khandi redd')
        if 'vera price' in genreList:
            movieCastCrew.addActor('Vera Price', '')
            genreList.remove('vera price')
        if 'bianca baker' in genreList:
            movieCastCrew.addActor('Bianca Baker', '')
            genreList.remove('bianca baker')

    #  Exquisite Goddess
    elif '81245' in userID:
        movieCastCrew.addActor('Exquisite Goddess', '')

    # Family Therapy
    elif '81593' in userID:
        if genreList:
            del genreList[0]

    #  femdomuncut Store
    elif '9824' in userID:
        if 'Princess Nikki' in metadata.summary or 'Nikki' in metadata.summary:
            movieCastCrew.addActor('Princess Nikki', '')
        if 'Zazie' in metadata.summary:
            movieCastCrew.addActor('Zazie Skymm', '')

    #  Fetish By LucySkye
    elif '47257' in userID:
        movieCastCrew.addActor('Lucy Skye', '')

    #  Fetish Princess Kristi
    elif '58257' in userID:
        movieCastCrew.addActor('Princess Kristi', '')
        if 'princess kristi' in genreList:
            genreList.remove('princess kristi')
        if 'kinky kristi' in genreList:
            genreList.remove('kinky kristi')

    #  FIlth Syndicate
    elif 'FIlth Syndicate' in tagline:
        if 'robin ray' in genreList:
            movieCastCrew.addActor('Robin Ray', '')
            genreList.remove('robin ray')
        if 'ryan keely' in genreList:
            movieCastCrew.addActor('Ryan Keely', '')
            genreList.remove('ryan keely')
        if 'ashley paige' in genreList:
            movieCastCrew.addActor('Ashley Paige', '')
            genreList.remove('ashley paige')
        if 'sophie monroe' in genreList:
            movieCastCrew.addActor('Sophie Monroe', '')
            genreList.remove('sophie monroe')
        if 'cherry torn' in genreList:
            movieCastCrew.addActor('Cherry Torn', '')
            genreList.remove('cherry torn')
        if 'barbary rose' in genreList:
            movieCastCrew.addActor('Barbary Rose', '')
            genreList.remove('barbary rose')

    #  Galactic Goddess
    elif '73481' in userID:
        movieCastCrew.addActor('Galactic Goddess', '')

    #  Glam Worship
    elif '43868' in userID:
        if 'mikaela witt' in genreList:
            movieCastCrew.addActor('Mikaela Witt', '')
            genreList.remove('mikaela witt')
        if 'mikaela' in genreList:
            movieCastCrew.addActor('Mikaela Witt', '')
            genreList.remove('mikaela')
        if 'jessie jensen' in genreList:
            movieCastCrew.addActor('Jessie Jensen', '')
            genreList.remove('jessie jensen')
        if 'jessie' in genreList:
            movieCastCrew.addActor('Jessie Jensen', '')
            genreList.remove('jessie')
        if 'lizzie murphy' in genreList:
            movieCastCrew.addActor('Lizzie Murphy', '')
            genreList.remove('lizzie murphy')
        if 'lizzie' in genreList:
            movieCastCrew.addActor('Lizzie Murphy', '')
            genreList.remove('lizzie')
        if 'lucy zara' in genreList:
            movieCastCrew.addActor('Lucy Zara', '')
            genreList.remove('lucy zara')
        if 'lucy' in genreList:
            movieCastCrew.addActor('Lucy Zara', '')
            genreList.remove('lucy')
        if 'lilly roma' in genreList:
            movieCastCrew.addActor('Lilly Roma', '')
            genreList.remove('lilly roma')
        if 'lilly' in genreList:
            movieCastCrew.addActor('Lilly Roma', '')
            genreList.remove('lilly')
        if 'dannii harwood' in genreList:
            movieCastCrew.addActor('Dannii Harwood', '')
            genreList.remove('dannii harwood')
        if 'dannii' in genreList:
            movieCastCrew.addActor('Dannii Harwood', '')
            genreList.remove('dannii')
        if 'vicky narni' in genreList:
            movieCastCrew.addActor('Vicky Narni', '')
            genreList.remove('vicky narni')
        if 'vicky' in genreList:
            movieCastCrew.addActor('Vicky Narni', '')
            genreList.remove('vicky')
        if 'dani maye' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('dani maye')
        if 'dani' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('dani')
        if 'danielle maye' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('danielle maye')
        if 'danielle' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('danielle')
        if 'nina leigh' in genreList:
            movieCastCrew.addActor('Nina Leigh', '')
            genreList.remove('nina leigh')
        if 'nina' in genreList:
            movieCastCrew.addActor('Nina Leigh', '')
            genreList.remove('nina')

    #  Goddess Alexandra Snow
    elif '38007' in userID:
        movieCastCrew.addActor('Alexandra Snow', '')

    #  Goddess Bs Slave Training 101
    elif '20178' in userID:
        movieCastCrew.addActor('Brandon Areana', '')
        if 'brandon areana' in genreList:
            genreList.remove('brandon areana')
        if 'goddess brandon' in genreList:
            genreList.remove('goddess brandon')

    #  Goddess Cheyenne
    elif '34631' in userID:
        if 'goddess cheyenne' in genreList:
            movieCastCrew.addActor('Goddess Cheyenne', '')
            genreList.remove('goddess cheyenne')
        if 'jewell marceau' in genreList:
            movieCastCrew.addActor('Jewell Marceau', '')
            genreList.remove('jewell marceau')
        if 'lady kyra' in genreList:
            movieCastCrew.addActor('Lady Kyra', '')
            genreList.remove('lady kyra')
        if 'jean bardot' in genreList:
            movieCastCrew.addActor('Jean Bardot', '')
            genreList.remove('jean bardot')

    #  Goddess Christina
    elif '89556' in userID:
        movieCastCrew.addActor('Goddess Cristina', '')
        if 'goddess christina' in genreList:
            genreList.remove('goddess christina')
        if 'erotic goddess christina' in genreList:
            genreList.remove('erotic goddess christina')
        if 'eroticgoddessxxx' in genreList:
            genreList.remove('eroticgoddessxxx')
        if 'erotic goddess' in genreList:
            genreList.remove('erotic goddess')

    #  Goddess Ella Kross
    elif '71734' in userID:
        movieCastCrew.addActor('Ella Kross', '')

    #  Goddess Eris Temple
    elif '127409' in userID:
        movieCastCrew.addActor('Eris Temple', '')
        #  Metadata match
        if 'Nikki Nyx' in metadata.title or 'Nikki Nyx' in metadata.summary:
            movieCastCrew.addActor('Nikki Nyx', '')

    #  Goddess Femdom
    elif '47562' in userID:
        movieCastCrew.addActor('Madame Amiee', '')
        if 'madame amiee' in genreList:
            genreList.remove('madame amiee')
        if 'johnny rifle' in genreList:
            movieCastCrew.addActor('Johnny Rifle', '')
            genreList.remove('johnny rifle')

    #  Goddess Foot Domination
    elif '38347' in userID:
        if 'goddess brianna' in genreList:
            movieCastCrew.addActor('Goddess Brianna', '')
            genreList.remove('goddess brianna')
        if 'vicky vixxx' in genreList:
            movieCastCrew.addActor('Vicky Vixxx', '')
            genreList.remove('vicky vixxx')
        if 'nicki blake' in genreList:
            movieCastCrew.addActor('Nicki Blake', '')
            genreList.remove('nicki blake')

    #  Goddess Gemma
    elif '80587' in userID:
        movieCastCrew.addActor('Goddess Gemma', '')

    #  Goddess Gwen the Princess Boss
    elif '92683' in userID:
        movieCastCrew.addActor('Goddess Gwen', '')

    #  Goddess Idelsy
    elif '51155' in userID:
        movieCastCrew.addActor('Idelsy Love', '')
        if 'idelsy love' in genreList:
            genreList.remove('idelsy love')
        if 'goddess idelsy' in genreList:
            genreList.remove('goddess idelsy')

    #  Goddess JessiBelle
    elif '55033' in userID:
        movieCastCrew.addActor('Jessi Belle', '')
        if 'jessibelle' in genreList:
            genreList.remove('jessibelle')
        if 'jessi belle' in genreList:
            genreList.remove('jessi belle')

    #  Goddess Kendall
    elif '47396' in userID:
        movieCastCrew.addActor('Kendall Olsen', '')

    #  Goddess Kims Fantasies
    elif '135383' in userID:
        movieCastCrew.addActor('Young Goddess Kim', '')
        if 'young goddess kim' in genreList:
            genreList.remove('young goddess kim')

    #  Goddess Kittys Findom Fuckery
    elif '119550' in userID:
        movieCastCrew.addActor('Goddess Kitty', '')
        if 'goddess blonde kitty' in genreList:
            genreList.remove('goddess blonde kitty')

    #  Goddess Madam Violet
    elif '87549' in userID:
        movieCastCrew.addActor('Madam Violet', '')
        if 'madam violet' in genreList:
            genreList.remove('madam violet')

    #  Goddess Mira
    elif '90731' in userID:
        movieCastCrew.addActor('Goddess Mira', '')

    #  Goddess Misha Mystique
    elif '74723' in userID:
        movieCastCrew.addActor('Misha Mystique', '')
        if 'misha mystique' in genreList:
            genreList.remove('misha mystique')

    #  Goddess Nikki
    elif '7817' in userID:
        movieCastCrew.addActor('Nikki Ashton', '')
        if 'nikki ashton' in genreList:
            genreList.remove('nikki ashton')
        if 'goddess nikki' in genreList:
            genreList.remove('goddess nikki')
        if 'erotic nikki' in genreList:
            genreList.remove('erotic nikki')
        if 'eroticnikki' in genreList:
            genreList.remove('eroticnikki')

    #  Goddess Paige
    elif '144585' in userID:
        movieCastCrew.addActor('Paige Orion', '')
        if 'paige orion' in genreList:
            genreList.remove('paige orion')
        if 'goddess paige' in genreList:
            genreList.remove('goddess paige')
        if 'goddess paige orion' in genreList:
            genreList.remove('goddess paige orion')

    #  Goddess Saffron
    elif '51793' in userID:
        movieCastCrew.addActor('Goddess Saffron', '')
        if 'goddess saffron' in genreList:
            genreList.remove('goddess saffron')
        if 'saffronism' in genreList:
            genreList.remove('saffronism')
        if 'saffmas' in genreList:
            genreList.remove('saffmas')

    #  Goddess Stella Sol
    elif '119947' in userID:
        movieCastCrew.addActor('Stella Sol', '')

    #  Goddess Tangent World of Femdom
    elif '115000' in userID:
        movieCastCrew.addActor('Goddess Tangent', '')
        if 'tangent' in genreList:
            genreList.remove('tangent')
        if 'goddess tangent' in genreList:
            genreList.remove('goddess tangent')

    #  Goddess Valora
    elif '104604' in userID:
        movieCastCrew.addActor('Goddess Valora', '')
        if 'goddess valora' in genreList:
            genreList.remove('goddess valora')

    #  Goddess Venus
    elif '106900' in userID:
        movieCastCrew.addActor('Goddess Venus', '')
        if 'goddess venus' in genreList:
            genreList.remove('goddess venus')
        if 'venus' in genreList:
            genreList.remove('venus')

    #  Goddess Vivian Leigh
    elif '81053' in userID:
        movieCastCrew.addActor('Vivian Leigh', '')
        if 'goddess vivian leigh' in genreList:
            genreList.remove('goddess vivian leigh')

    #  Goddess Zenova Controls Your Mind
    elif '75409' in userID:
        movieCastCrew.addActor('Goddess Zenova', '')

    #  Goddess Zephy
    elif '134471' in userID:
        movieCastCrew.addActor('Goddess Zephy', '')
        if 'zephy' in genreList:
            genreList.remove('Zephy')
        if 'zephyanna' in genreList:
            genreList.remove('zephianna')

    #  Harley LaVey
    elif '119180' in userID:
        # Manually fix tagline and collection
        metadata.tagline = 'Harley LaVey'
        metadata.collections.clear()
        metadata.collections.add(metadata.tagline)

        movieCastCrew.addActor('Harley LaVey', '')

    #  HollyDomme
    elif '36138' in userID:
        movieCastCrew.addActor('Holly Webster', '')
        if 'hollydomme' in genreList:
            genreList.remove('hollydomme')
        if 'hollywebster' in genreList:
            genreList.remove('hollywebster')

    #  HomSmother
    elif '17488' in userID:
        if 'liana' in genreList:
            movieCastCrew.addActor('Liana', '')
            genreList.remove('Liana')
        if 'amy' in genreList:
            movieCastCrew.addActor('Amy', '')
            genreList.remove('amy')
        if 'sabrina' in genreList:
            movieCastCrew.addActor('Sabrina', '')
            genreList.remove('sabrina')
        if 'sabrina a' in genreList:
            movieCastCrew.addActor('Sabrina', '')
            genreList.remove('sabrina a')
        if 'anna' in genreList:
            movieCastCrew.addActor('Anna', '')
            genreList.remove('anna')
        if 'anna b' in genreList:
            movieCastCrew.addActor('Anna', '')
            genreList.remove('anna a')
        if 'cindy' in genreList:
            movieCastCrew.addActor('Cindy', '')
            genreList.remove('cindy')
        if 'cindy c' in genreList:
            movieCastCrew.addActor('Cindy', '')
            genreList.remove('cindy c')
        if 'florence' in genreList:
            movieCastCrew.addActor('Florence', '')
            genreList.remove('florence')
        if 'rayana' in genreList:
            movieCastCrew.addActor('Rayana', '')
            genreList.remove('rayana')
        if 'sara' in genreList:
            movieCastCrew.addActor('Sara', '')
            genreList.remove('sara')
        if 'adriana' in genreList:
            movieCastCrew.addActor('Adriana', '')
            genreList.remove('adriana')
        if 'felicitas' in genreList:
            movieCastCrew.addActor('Felicitas', '')
            genreList.remove('felicitas')

    #  Hot Juls Fetishes
    elif '102725' in userID:
        movieCastCrew.addActor('Goddess Juls', '')
        if 'goddess juls' in genreList:
            genreList.remove('goddess juls')
        if 'hot juls fetishes' in genreList:
            genreList.remove('hot juls fetishes')
        if 'juls' in genreList:
            genreList.remove('juls')

    #  Humiliation Brat Girls
    elif '72067' in userID:
        if 'Jolene' in metadata.summary:
            movieCastCrew.addActor('Jolene', '')
        if 'Bobbi Dylan' in metadata.summary:
            movieCastCrew.addActor('Bobbi Dylan', '')
        if 'Cydel' in metadata.summary:
            movieCastCrew.addActor('Cydel', '')

    #  Humiliation POV
    elif '16417' in userID:
        if 'Goddess Carissa' in metadata.summary or 'Carissa Montgomery' in metadata.summary:
            movieCastCrew.addActor('Carissa Montgomery', '')
        if 'Princess Ellie' in metadata.summary:
            movieCastCrew.addActor('Ellie Idol', '')
        if 'Miss Tiffany' in metadata.summary:
            movieCastCrew.addActor('Miss Tiffany', '')
        if 'Goddess Alexa' in metadata.summary:
            movieCastCrew.addActor('Goddess Alexa', '')
        if 'Goddess Isabel' in metadata.summary:
            movieCastCrew.addActor('Goddess Isabel', '')
        if 'Kelle Martina' in metadata.summary:
            movieCastCrew.addActor('Kelle Martina', '')
        if 'Bratty Bunny' in metadata.summary:
            movieCastCrew.addActor('Bratty Bunny', '')
        if 'Macey Jade' in metadata.summary:
            movieCastCrew.addActor('Macey Jade', '')
        if 'Princess Kaelin' in metadata.summary:
            movieCastCrew.addActor('Princess Kaelin', '')
        if 'Princess Kate' in metadata.summary:
            movieCastCrew.addActor('Princess Kate', '')
        if 'Megan Foxx' in metadata.summary:
            movieCastCrew.addActor('Megan Foxx', '')
        if 'Nikki Next' in metadata.summary:
            movieCastCrew.addActor('Nikki Next', '')
        if 'Goddess Sahrye' in metadata.summary:
            movieCastCrew.addActor('Goddess Sahrye', '')
        if 'Amai Liu' in metadata.summary:
            movieCastCrew.addActor('Amai Liu', '')
        if 'London Lix' in metadata.summary:
            movieCastCrew.addActor('London Lix', '')

    #  Humiliation Princess Rene's Clips!
    elif '26992!' in userID:
        movieCastCrew.addActor('Princess Rene', '')
        if 'princess rene' in genreList:
            genreList.remove('princess rene')
        if 'worship rene' in genreList:
            genreList.remove('worship rene')
        if 'renee' in genreList:
            genreList.remove('renee')
        if 'rene' in genreList:
            genreList.remove('rene')

    #  HUMILIATRIX CLIPSTORE
    elif '17070' in userID:
        #  Genre list match
        if 'princess selena' in genreList:
            movieCastCrew.addActor('Princess Selana', '')
            genreList.remove('princess selana')
        if 'princess ashleigh' in genreList:
            movieCastCrew.addActor('Princess Ashleigh', '')
            genreList.remove('princess ashleigh')
        if 'princess missy' in genreList:
            movieCastCrew.addActor('Princess Missy', '')
            genreList.remove('princess missy')
        if 'princess tiffani' in genreList:
            movieCastCrew.addActor('Princess Tiffani', '')
            genreList.remove('princess tiffani')
        if 'kendra james' in genreList:
            movieCastCrew.addActor('Kendra James', '')
            genreList.remove('kendra james')

        #  Metadata match
        if 'Princess Becky' in metadata.title or 'Princess Becky' in metadata.summary:
            movieCastCrew.addActor('Princess Becky', '')
        if 'Kendra James' in metadata.title or 'Kendra James' in metadata.summary:
            movieCastCrew.addActor('Kendra James', '')
        if 'Princess luna' in metadata.title or 'princess luna' in metadata.summary:
            movieCastCrew.addActor('Princess Luna', '')
        if 'Princess Tiffani' in metadata.title or 'Princess Tiffani' in metadata.summary:
            movieCastCrew.addActor('Princess Tiffani', '')
        if 'Ashleigh' in metadata.title or 'Ashleigh' in metadata.summary:
            movieCastCrew.addActor('Princess Ashleigh', '')
        if 'Princess Tessa' in metadata.title or 'Princess Tessa' in metadata.summary:
            movieCastCrew.addActor('Princess Tessa', '')
        if 'Princess Remi' in metadata.title or 'Princess Remi' in metadata.summary or 'Remi' in metadata.title or 'remi' in metadata.summary:
            movieCastCrew.addActor('Princess Remi', '')
        if 'Goddess Rhianna' in metadata.title or 'Goddess Rhianna' in metadata.summary:
            movieCastCrew.addActor('Goddess Rhianna', '')
        if 'Princess Ashley' in metadata.title or 'Princess Ashley' in metadata.summary:
            movieCastCrew.addActor('Princess Ashley', '')
        if 'Princess Jade' in metadata.title or 'Princess Jade' in metadata.summary:
            movieCastCrew.addActor('Princess Jade', '')
        if 'Princess Missy' in metadata.title or 'Princess Missy' in metadata.summary:
            movieCastCrew.addActor('Princess Missy', '')
        if 'Pimpstress Sari' in metadata.title or 'Pimpstress Sari' in metadata.summary:
            movieCastCrew.addActor('Pimpstress Sari', '')

    #  Italian Empress Daria
    elif '56791' in userID:
        movieCastCrew.addActor('Empress Daria', '')
        if 'daria' in genreList:
            genreList.remove('daria')

    #  Jasmine Mendez  LatinAss Locas
    elif '54509' in userID:
        movieCastCrew.addActor('Jasmine Mendez', '')

    #  Jerk Off Instructions
    elif '4102' in userID:
        #  Genre list match
        if 'amai liu' in genreList:
            movieCastCrew.addActor('Amai Liu', '')
            genreList.remove('amai liu')
        if 'lacy lennon' in genreList:
            movieCastCrew.addActor('Lacy Lennon', '')
            genreList.remove('lacy lennon')
        if 'katie kush' in genreList:
            movieCastCrew.addActor('Katie Kush', '')
            genreList.remove('katie kush')
        if 'veronica valentine' in genreList:
            movieCastCrew.addActor('Veronica Valentine', '')
            genreList.remove('veronica valentine')
        if 'victoria voxxx' in genreList:
            movieCastCrew.addActor('Victoria Voxxx', '')
            genreList.remove('victoria voxxx')
        if 'licey sweet' in genreList:
            movieCastCrew.addActor('Licey Sweet', '')
            genreList.remove('licey sweet')
        if 'lily adams' in genreList:
            movieCastCrew.addActor('Lily Adams', '')
            genreList.remove('lily adams')
        if 'ryder skye' in genreList:
            movieCastCrew.addActor('Ryder Sky', '')
            genreList.remove('ryder skye')
        if 'violet starr' in genreList:
            movieCastCrew.addActor('Violet Starr', '')
            genreList.remove('violet starr')
        if 'kasey warner' in genreList:
            movieCastCrew.addActor('Kasey Warner', '')
            genreList.remove('kasey warner')
        if 'aiden ashley' in genreList:
            movieCastCrew.addActor('Aiden Ashley', '')
            genreList.remove('aiden ashley')
        if 'olivia glass' in genreList:
            movieCastCrew.addActor('Olivia Glass', '')
            genreList.remove('olivia glass')
        if 'carolina sweets' in genreList:
            movieCastCrew.addActor('Carolina Sweets', '')
            genreList.remove('carolina sweets')
        if 'jillian janson' in genreList:
            movieCastCrew.addActor('Jillian Janson', '')
            genreList.remove('jillian janson')
        if 'raven hart' in genreList:
            movieCastCrew.addActor('Raven Hart', '')
            genreList.remove('raven hart')
        if 'jayden cole' in genreList:
            movieCastCrew.addActor('Jayden Cole', '')
            genreList.remove('jayden cole')
        if 'anna graham' in genreList:
            movieCastCrew.addActor('Anna Graham', '')
            genreList.remove('anna graham')

        #  Metadata match
        if 'Anna' in metadata.summary:
            movieCastCrew.addActor('Anna Graham', '')

    #  Jerk4PrincessUK
    elif '36426' in userID:
        if 'axa jay' in genreList:
            movieCastCrew.addActor('Axa Jay', '')
            genreList.remove('axa jay')
        if 'axajay' in genreList:
            movieCastCrew.addActor('Axa Jay', '')
            genreList.remove('axajay')
        if 'cherry blush' in genreList:
            movieCastCrew.addActor('Cherry Blush', '')
            genreList.remove('cherry blush')
        if 'raven lee' in genreList:
            movieCastCrew.addActor('Raven Lee', '')
            genreList.remove('raven lee')
        if 'bonnie bellotti' in genreList:
            movieCastCrew.addActor('Bonnie Bellotti', '')
            genreList.remove('bonnie bellotti')
        if 'charn' in genreList:
            movieCastCrew.addActor('Charn', '')
            genreList.remove('charn')
        if 'natalia forrest' in genreList:
            movieCastCrew.addActor('Natalia Forrest', '')
            genreList.remove('natalia forrest')
        if 'michelle hush' in genreList:
            movieCastCrew.addActor('Michelle Hush', '')
            genreList.remove('michelle hush')
        if 'carmen' in genreList:
            movieCastCrew.addActor('Carmen', '')
            genreList.remove('carmen')
        if 'jessica fox' in genreList:
            movieCastCrew.addActor('Jessica Fox', '')
            genreList.remove('jessica fox')
        if 'kacie james' in genreList:
            movieCastCrew.addActor('Kacie James', '')
            genreList.remove('kacie james')
        if 'volkova' in genreList:
            movieCastCrew.addActor('Volkova', '')
            genreList.remove('volkova')
        if 'setina rose' in genreList:
            movieCastCrew.addActor('Setina Rose', '')
            genreList.remove('setina rose')

    #  Jerky Wives
    elif '28671' in userID:
        #  Genre list match
        if 'cory chase' in genreList:
            movieCastCrew.addActor('Cory Chase', '')
            genreList.remove('cory chase')
        if 'luke longly' in genreList:
            movieCastCrew.addActor('Luke Longly', '')
            genreList.remove('luke longly')
        if 'coco vandi' in genreList:
            movieCastCrew.addActor('Coco Vandi', '')
            genreList.remove('coco vandi')
        if 'vanessa cage' in genreList:
            movieCastCrew.addActor('Vanessa Cage', '')
            genreList.remove('vanessa cage')
        if 'melanie hicks' in genreList:
            movieCastCrew.addActor('Melanie Hicks', '')
            genreList.remove('melanie hicks')
        if 'alice visby' in genreList:
            movieCastCrew.addActor('Alice Visby', '')
            genreList.remove('alice visby')
        if 'aimee cambridge' in genreList:
            movieCastCrew.addActor('Aimee Cambridge', '')
            genreList.remove('aimee cambridge')
        if 'bailey base' in genreList:
            movieCastCrew.addActor('Bailey Base', '')
            genreList.remove('bailey base')
        if 'brooklyn chase' in genreList:
            movieCastCrew.addActor('Brooklyn Chase', '')
            genreList.remove('brooklyn chase')
        if 'johnny kidd' in genreList:
            movieCastCrew.addActor('Johnny Kidd', '')
            genreList.remove('johnny kidd')
        if 'clover baltimore' in genreList:
            movieCastCrew.addActor('Clover Baltimore', '')
            genreList.remove('clover baltimore')
        if 'dixie lynn' in genreList:
            movieCastCrew.addActor('Dixie Lynn', '')
            genreList.remove('dixie lynn')
        if 'gabriella lopez' in genreList:
            movieCastCrew.addActor('Gabriella Lopez', '')
            genreList.remove('gabriella lopez')
        if 'kitten latenight' in genreList:
            movieCastCrew.addActor('Kitten Latenight', '')
            genreList.remove('kitten latenight')
        if 'lexxi steele' in genreList:
            movieCastCrew.addActor('Lexxi Steele', '')
            genreList.remove('lexxi steele')
        if 'maggie green' in genreList:
            movieCastCrew.addActor('Maggie Green', '')
            genreList.remove('maggie green')
        if 'michele james' in genreList:
            movieCastCrew.addActor('Michele James', '')
            genreList.remove('michele james')
        if 'skylar vox' in genreList:
            movieCastCrew.addActor('Skylar Vox', '')
            genreList.remove('skylar vox')

        #  Metadata match
        if 'cory chase' in metadata.summary:
            movieCastCrew.addActor('Cory Chase', '')
        if 'luke longly' in metadata.summary:
            movieCastCrew.addActor('Luke Longly', '')
        if 'coco vandi' in metadata.summary:
            movieCastCrew.addActor('Coco Vandi', '')
        if 'vanessa cage' in metadata.summary:
            movieCastCrew.addActor('Vanessa Cage', '')
        if 'melanie hicks' in metadata.summary:
            movieCastCrew.addActor('Melanie Hicks', '')
        if 'alice visby' in metadata.summary:
            movieCastCrew.addActor('Alice Visby', '')
        if 'aimee cambridge' in metadata.summary:
            movieCastCrew.addActor('Aimee Cambridge', '')
        if 'bailey base' in metadata.summary:
            movieCastCrew.addActor('Bailey Base', '')
        if 'brooklyn chase' in metadata.summary:
            movieCastCrew.addActor('Brooklyn Chase', '')
        if 'johnny kidd' in metadata.summary:
            movieCastCrew.addActor('Johnny Kidd', '')
        if 'clover baltimore' in metadata.summary:
            movieCastCrew.addActor('Clover Baltimore', '')
        if 'dixie lynn' in metadata.summary:
            movieCastCrew.addActor('Dixie Lynn', '')
        if 'gabriella lopez' in metadata.summary:
            movieCastCrew.addActor('Gabriella Lopez', '')
        if 'kitten latenight' in metadata.summary:
            movieCastCrew.addActor('Kitten Latenight', '')
        if 'lexxi steele' in metadata.summary:
            movieCastCrew.addActor('Lexxi Steele', '')
        if 'maggie green' in metadata.summary:
            movieCastCrew.addActor('Maggie Green', '')
        if 'michele james' in metadata.summary:
            movieCastCrew.addActor('Michele James', '')
        if 'skylar vox' in metadata.summary:
            movieCastCrew.addActor('Skylar Vox', '')

    #  KEBRANOZES BRAZILIAN BALLBUSTING
    elif '60749' in userID:
        #  Genre list match
        if 'barbara inked' in genreList:
            movieCastCrew.addActor('Barbara Inked', '')
            genreList.remove('barbara inked')
        if 'tygra' in genreList:
            movieCastCrew.addActor('Tygra', '')
            genreList.remove('tygra')
        if 'renata' in genreList:
            movieCastCrew.addActor('Renata', '')
            genreList.remove('renata')
        if 'leona' in genreList:
            movieCastCrew.addActor('Leona', '')
            genreList.remove('leona')
        if 'yoko' in genreList:
            movieCastCrew.addActor('Yoko', '')
            genreList.remove('yoko')
        if 'alexa' in genreList:
            movieCastCrew.addActor('Alexa', '')
            genreList.remove('alexa')

        #  Metadata match
        if 'Tygra' in metadata.summary:
            movieCastCrew.addActor('Tygra', '')
        if 'Yoko' in metadata.summary:
            movieCastCrew.addActor('Yoko', '')
        if 'Sandy' in metadata.summary:
            movieCastCrew.addActor('Sandy', '')
        if 'Renata' in metadata.summary:
            movieCastCrew.addActor('Renata', '')
        if 'Leona' in metadata.summary:
            movieCastCrew.addActor('Leona', '')

    #  Kerri King's Naughty Pleasures
    elif '67401' in userID:
        movieCastCrew.addActor('Kerri King', '')
        if 'kerri king' in genreList:
            genreList.remove('kerri king')

    #  KIMBERLY KANES KANEARMY
    elif '48773' in userID:
        movieCastCrew.addActor('Kimberly Kane', '')
        if 'kimberly kane' in genreList:
            genreList.remove('kimberly kane')
        if 'syren demer' in genreList:
            movieCastCrew.addActor('Syren Demer', '')
            genreList.remove('syren demer')
        if 'dee williams' in genreList:
            movieCastCrew.addActor('Dee Williams', '')
            genreList.remove('dee williams')
        if 'natalia mars' in genreList:
            movieCastCrew.addActor('Natalia Mars', '')
            genreList.remove('natalia mars')
        if 'mandy mitchell' in genreList:
            movieCastCrew.addActor('Mandy Mitchell', '')
            genreList.remove('mandy mitchell')

    #  Kitzis Clown Fetish
    elif '54167' in userID:
        movieCastCrew.addActor('Kitzi Klown', '')

    #  Kyaa's Empire
    elif '23738' in userID:
        movieCastCrew.addActor('Kyaa Chimera', '')
        if 'goddess kyaa' in genreList:
            genreList.remove('goddess kyaa')
        if 'domme kyaa' in genreList:
            genreList.remove('domme kyaa')
        if 'kyaa chimera' in genreList:
            genreList.remove('kyaa chimera')
        if 'kyaaism' in genreList:
            genreList.remove('kyaaism')
        if 'sarah diavola' in genreList:
            movieCastCrew.addActor('Sarah Diavola', '')
            genreList.remove('sarah diavola')
        if 'laila delight' in genreList:
            movieCastCrew.addActor('Laila Delight', '')
            genreList.remove('laila delight')
        if 'jessica doll' in genreList:
            movieCastCrew.addActor('Jessica Doll', '')
            genreList.remove('jessica doll')

    #  Lady Bellatrix
    elif '58975' in userID:
        movieCastCrew.addActor('Lady Bellatrix', '')
        if 'lady bellatrix' in genreList:
            genreList.remove('lady bellatrix')
        if 'mistress nikki whiplash' in genreList:
            movieCastCrew.addActor('Nikki Whiplash', '')
            genreList.remove('mistress nikki whiplash')
        if 'miss xi' in genreList:
            movieCastCrew.addActor('Miss Xi', '')
            genreList.remove('miss xi')
        if 'miss jasmine' in genreList:
            movieCastCrew.addActor('Miss Jasmine', '')
            genreList.remove('miss jasmine')
        if 'gaelle lagalle' in genreList:
            movieCastCrew.addActor('Gaelle Lagalle', '')
            genreList.remove('gaelle lagalle')
        if 'mistress esme' in genreList:
            movieCastCrew.addActor('Mistress Esme', '')
            genreList.remove('mistress esme')
        if 'miss tiffany naylor' in genreList:
            movieCastCrew.addActor('Tiffany Naylor', '')
            genreList.remove('miss tiffany naylor')

    #  Lady Fyre Femdom
    elif '60555' in userID:
        #  Genre list match
        if 'lady fyre' in genreList:
            movieCastCrew.addActor('Lady Fyre', '')
            genreList.remove('lady fyre')
        if 'kenzie madison' in genreList:
            movieCastCrew.addActor('Kenzie Madison', '')
            genreList.remove('kenzie madison')
        if 'indica flower' in genreList:
            movieCastCrew.addActor('Indica Flower', '')
            genreList.remove('indica flower')
        if 'laney grey' in genreList:
            movieCastCrew.addActor('Laney Grey', '')
            genreList.remove('laney grey')
        if 'katie kush' in genreList:
            movieCastCrew.addActor('Katie Kush', '')
            genreList.remove('katie kush')
        if 'violet starr' in genreList:
            movieCastCrew.addActor('Violet Starr', '')
            genreList.remove('violet starr')
        if 'laz fyre' in genreList:
            movieCastCrew.addActor('Laz Fyre', '')
            genreList.remove('laz fyre')
        if 'mandy muse' in genreList:
            movieCastCrew.addActor('Mandy Muse', '')
            genreList.remove('mandy muse')
        if 'house of fyre' in genreList:
            genreList.remove('house of fyre')

        #  Metadata Match
        if 'Cali Carter' in metadata.summary:
            movieCastCrew.addActor('Cali Carter', '')

    #  Lady Karame
    elif '81851' in userID:
        movieCastCrew.addActor('Lady Karame', '')
        if 'lady karame' in genreList:
            genreList.remove('lady karame')

    #  Lady Nina Leighs Royal Domination
    elif '53735' in userID:
        movieCastCrew.addActor('Nina Leigh', '')
        if 'ladyninaleigh' in genreList:
            genreList.remove('ladyninaleigh')
        if 'loveladynina' in genreList:
            genreList.remove('loveladynina')
        if 'lady nina leigh' in genreList:
            genreList.remove('lady nina leigh')

    #  Latex Barbie Land
    elif '103769' in userID:
        movieCastCrew.addActor('Latex Barbie', '')
        if 'latexbarbie' in genreList:
            genreList.remove('latexbarbie')
        if 'latex barbie' in genreList:
            genreList.remove('latex barbie')
        if 'barbie' in genreList:
            genreList.remove('barbie')
        if 'latex' in genreList:
            genreList.remove('latex')

    #  Lelu Love
    elif '44611' in userID:
        movieCastCrew.addActor('Lelu Love', '')
        if 'lelu' in genreList:
            genreList.remove('lelu')
        if 'lelu-love' in genreList:
            genreList.remove('lelu-love')
        if 'lelu love' in genreList:
            genreList.remove('lelu love')

    #  Lindsey Leigh Addiction
    elif '37081' in userID:
        movieCastCrew.addActor('Lindsey Leigh', '')

    #  Luna Sapphire
    elif '97183' in userID:
        movieCastCrew.addActor('Luna Sapphire', '')
        if 'luna sapphire' in genreList:
            genreList.remove('luna sapphire')
        if 'goddess luna' in genreList:
            genreList.remove('goddess luna')
        if 'goddess ellie' in genreList:
            movieCastCrew.addActor('Ellie Boulder', '')
            genreList.remove('goddess ellie')
        if 'ellie boulder' in genreList:
            movieCastCrew.addActor('Ellie Boulder', '')
            genreList.remove('ellie boulder')

    #  Majesty Natalie
    elif '128701' in userID:
        movieCastCrew.addActor('Majesty Natalie', '')
        if 'majesty natalie' in genreList:
            genreList.remove('majesty natalie')
        if 'majestynatalie' in genreList:
            genreList.remove('majestynatalie')

    #  Makayla Divine Busty Latina Goddess
    elif '62421' in userID:
        movieCastCrew.addActor('Makayla Divine', '')

    #  Mandy Flores
    elif '33729' in userID:
        movieCastCrew.addActor('Mandy Flores', '')
        if 'mandy flores' in genreList:
            genreList.remove('mandy flores')
        if 'new mandy flores video' in genreList:
            genreList.remove('new mandy flores video')
        if 'mymandygirl' in genreList:
            genreList.remove('mymandygirl')

    #  MARKS HEAD BOBBERS  HAND JOBBERS
    elif '47321' in userID:
        movieCastCrew.addActor('Mark Rockwell', '')
        #  Genre list match
        if 'mark rockwell' in genreList:
            genreList.remove('mark rockwell')
        if 'alexa grace' in genreList:
            movieCastCrew.addActor('Alexa Grace', '')
            genreList.remove('alexa grace')
        if 'remy lacroix' in genreList:
            movieCastCrew.addActor('Remy LaCroix', '')
            genreList.remove('remy lacroix')
        if 'jade indica' in genreList:
            movieCastCrew.addActor('Jade Indica', '')
            genreList.remove('jade indica')
        if 'dillion carter' in genreList:
            movieCastCrew.addActor('Dillion Carter', '')
            genreList.remove('dillion carter')
        if 'sierra cure' in genreList:
            movieCastCrew.addActor('Sierra Cure', '')
            genreList.remove('sierra cure')
        if 'britney stevens' in genreList:
            movieCastCrew.addActor('Britney Stevens', '')
            genreList.remove('britney stevens')
        if 'megan piper' in genreList:
            movieCastCrew.addActor('Megan Piper', '')
            genreList.remove('megan piper')
        if 'alexis venton' in genreList:
            movieCastCrew.addActor('Alexis Venton', '')
            genreList.remove('alexis venton')
        if 'jessica rayne' in genreList:
            movieCastCrew.addActor('Jessica Rayne', '')
            genreList.remove('jessica rayne')
        if 'mandy haze' in genreList:
            movieCastCrew.addActor('Mandy Haze', '')
            genreList.remove('mandy haze')

        #  Metadata match
        if 'Alexa Grace' in metadata.summary:
            movieCastCrew.addActor('Alexa Grace', '')
        if 'Remy LaCroix' in metadata.summary:
            movieCastCrew.addActor('Remy LaCroix', '')
        if 'Jade Indica' in metadata.summary:
            movieCastCrew.addActor('Jade Indica', '')
        if 'Dillion Carter' in metadata.summary:
            movieCastCrew.addActor('Dillion Carter', '')
        if 'Sierra Cure' in metadata.summary:
            movieCastCrew.addActor('Sierra Cure', '')
        if 'Britney Stevens' in metadata.summary:
            movieCastCrew.addActor('Britney Stevens', '')
        if 'Megan Piper' in metadata.summary:
            movieCastCrew.addActor('Megan Piper', '')
        if 'Alexis Venton' in metadata.summary:
            movieCastCrew.addActor('Alexis Venton', '')
        if 'Jessica Rayne' in metadata.summary:
            movieCastCrew.addActor('Jessica Rayne', '')
        if 'Mandy Haze' in metadata.summary:
            movieCastCrew.addActor('Mandy Haze', '')

    #  Maternal Seductions
    elif '32590' in userID:
        #  Genre list match
        if 'cory chase' in genreList:
            movieCastCrew.addActor('Cory Chase', '')
            genreList.remove('cory chase')
        if 'luke longly' in genreList:
            movieCastCrew.addActor('Luke Longly', '')
            genreList.remove('luke longly')
        if 'coco vandi' in genreList:
            movieCastCrew.addActor('Coco Vandi', '')
            genreList.remove('coco vandi')
        if 'vanessa cage' in genreList:
            movieCastCrew.addActor('Vanessa Cage', '')
            genreList.remove('vanessa cage')
        if 'melanie hicks' in genreList:
            movieCastCrew.addActor('Melanie Hicks', '')
            genreList.remove('melanie hicks')
        if 'alice visby' in genreList:
            movieCastCrew.addActor('Alice Visby', '')
            genreList.remove('alice visby')
        if 'aimee cambridge' in genreList:
            movieCastCrew.addActor('Aimee Cambridge', '')
            genreList.remove('aimee cambridge')
        if 'bailey base' in genreList:
            movieCastCrew.addActor('Bailey Base', '')
            genreList.remove('bailey base')
        if 'brooklyn chase' in genreList:
            movieCastCrew.addActor('Brooklyn Chase', '')
            genreList.remove('brooklyn chase')
        if 'johnny kidd' in genreList:
            movieCastCrew.addActor('Johnny Kidd', '')
            genreList.remove('johnny kidd')
        if 'clover baltimore' in genreList:
            movieCastCrew.addActor('Clover Baltimore', '')
            genreList.remove('clover baltimore')
        if 'dixie lynn' in genreList:
            movieCastCrew.addActor('Dixie Lynn', '')
            genreList.remove('dixie lynn')
        if 'gabriella lopez' in genreList:
            movieCastCrew.addActor('Gabriella Lopez', '')
            genreList.remove('gabriella lopez')
        if 'kitten latenight' in genreList:
            movieCastCrew.addActor('Kitten Latenight', '')
            genreList.remove('kitten latenight')
        if 'lexxi steele' in genreList:
            movieCastCrew.addActor('Lexxi Steele', '')
            genreList.remove('lexxi steele')
        if 'maggie green' in genreList:
            movieCastCrew.addActor('Maggie Green', '')
            genreList.remove('maggie green')
        if 'michele james' in genreList:
            movieCastCrew.addActor('Michele James', '')
            genreList.remove('michele james')
        if 'skylar vox' in genreList:
            movieCastCrew.addActor('Skylar Vox', '')
            genreList.remove('skylar vox')

        #  Metadata match
        if 'cory chase' in metadata.summary:
            movieCastCrew.addActor('Cory Chase', '')
        if 'luke longly' in metadata.summary:
            movieCastCrew.addActor('Luke Longly', '')
        if 'coco vandi' in metadata.summary:
            movieCastCrew.addActor('Coco Vandi', '')
        if 'vanessa cage' in metadata.summary:
            movieCastCrew.addActor('Vanessa Cage', '')
        if 'melanie hicks' in metadata.summary:
            movieCastCrew.addActor('Melanie Hicks', '')
        if 'alice visby' in metadata.summary:
            movieCastCrew.addActor('Alice Visby', '')
        if 'aimee cambridge' in metadata.summary:
            movieCastCrew.addActor('Aimee Cambridge', '')
        if 'bailey base' in metadata.summary:
            movieCastCrew.addActor('Bailey Base', '')
        if 'brooklyn chase' in metadata.summary:
            movieCastCrew.addActor('Brooklyn Chase', '')
        if 'johnny kidd' in metadata.summary:
            movieCastCrew.addActor('Johnny Kidd', '')
        if 'clover baltimore' in metadata.summary:
            movieCastCrew.addActor('Clover Baltimore', '')
        if 'dixie lynn' in metadata.summary:
            movieCastCrew.addActor('Dixie Lynn', '')
        if 'gabriella lopez' in metadata.summary:
            movieCastCrew.addActor('Gabriella Lopez', '')
        if 'kitten latenight' in metadata.summary:
            movieCastCrew.addActor('Kitten Latenight', '')
        if 'lexxi steele' in metadata.summary:
            movieCastCrew.addActor('Lexxi Steele', '')
        if 'maggie green' in metadata.summary:
            movieCastCrew.addActor('Maggie Green', '')
        if 'michele james' in metadata.summary:
            movieCastCrew.addActor('Michele James', '')
        if 'skylar vox' in metadata.summary:
            movieCastCrew.addActor('Skylar Vox', '')

    #  Meana Wolf
    elif '81629' in userID:
        movieCastCrew.addActor('Meana Wolf', '')
        #  Genre list match
        if 'meana wolf' in genreList:
            genreList.remove('meana wolf')
        if 'liv revamped' in genreList:
            movieCastCrew.addActor('Liv Revamped', '')
            genreList.remove('liv revamped')
        #  Metadata match
        if 'Liv Revamped' in metadata.summary:
            movieCastCrew.addActor('Liv Revamped')

    #  MeanBitches POV Slave Orders
    elif '15571' in userID:
        #  Genre list match
        if 'valentina jewels' in genreList:
            movieCastCrew.addActor('Valentina Jewels', '')
            genreList.remove('valentina jewels')
        if 'gia dimarco' in genreList:
            movieCastCrew.addActor('Gia Dimarco', '')
            genreList.remove('gia dimarco')
        if 'kimber woods' in genreList:
            movieCastCrew.addActor('Kimber Woods', '')
            genreList.remove('kimber woods')
        if 'alura jenson' in genreList:
            movieCastCrew.addActor('Alura Jenson', '')
            genreList.remove('alura jenson')
        if 'lala ivey' in genreList:
            movieCastCrew.addActor('Lala Ivey', '')
            genreList.remove('lala ivey')
        if 'alexis fawx' in genreList:
            movieCastCrew.addActor('Alexis Fawx', '')
            genreList.remove('alexis fawx')
        if 'london rivers' in genreList:
            movieCastCrew.addActor('London Rivers', '')
            genreList.remove('london rivers')
        if 'victoria voxxx' in genreList:
            movieCastCrew.addActor('Victoria Voxxx', '')
            genreList.remove('victoria voxxx')
        if 'sofia rose' in genreList:
            movieCastCrew.addActor('Sofia Rose', '')
            genreList.remove('sofia rose')
        if 'lana violet' in genreList:
            movieCastCrew.addActor('Lana Violet', '')
            genreList.remove('lana violet')
        #  Metadata match
        if 'Holly Wellin' in metadata.title or 'Holly Wellin' in metadata.summary:
            movieCastCrew.addActor('Holly Wellin', '')
        if 'Holly Michael' in metadata.title or 'Holly Michael' in metadata.summary:
            movieCastCrew.addActor('Holly Michael', '')
        if 'Kristina rose' in metadata.title or 'Kristina Rose' in metadata.summary:
            movieCastCrew.addActor('Kristina Rose', '')
        if 'Phoenix Marie' in metadata.title or 'Phoenix Marie' in metadata.summary:
            movieCastCrew.addActor('Phoenix Marie', '')
        if 'Alexis Texas' in metadata.title or 'Alexis Texas' in metadata.summary:
            movieCastCrew.addActor('Alexis Texas', '')
        if 'Bree Olson' in metadata.title or 'Bree Olson' in metadata.summary:
            movieCastCrew.addActor('Bree Olson', '')

    #  Meggerz
    elif '12252' in userID:
        movieCastCrew.addActor('Meggerz', '')
        #  Genre list match
        if 'meggerz' in genreList:
            genreList.remove('meggerz')
        if 'sarah diavola' in genreList:
            movieCastCrew.addActor('Sarah Diavola', '')
            genreList.remove('sarah diavola')
        if 'ninja jason' in genreList:
            movieCastCrew.addActor('Ninja Jason', '')
            genreList.remove('ninja jason')
        if 'mz devious' in genreList:
            movieCastCrew.addActor('Mz Devious', '')
            genreList.remove('mz devious')
        if 'evelyn milano' in genreList:
            movieCastCrew.addActor('Evelyn Milano', '')
            genreList.remove('evelyn milano')
        #  Metadata Match
        if 'Mz Devious' in metadata.summary:
            movieCastCrew.addActor('Mz Devious', '')

    #  Men Are Slaves
    elif '29646' in userID:
        #  Genre list match
        if 'cadence st. john' in genreList:
            movieCastCrew.addActor('Cadence St. John', '')
            genreList.remove('cadence st.john')
        if 'mistress cadence' in genreList:
            movieCastCrew.addActor('Cadence St. John', '')
            genreList.remove('mistress cadence')
        if 'edyn blair' in genreList:
            movieCastCrew.addActor('Edyn Blair', '')
            genreList.remove('edyn blair')
        if 'miley mae' in genreList:
            movieCastCrew.addActor('Miley Mae', '')
            genreList.remove('miley mae')
        if 'kay carter' in genreList:
            movieCastCrew.addActor('Kay Carter', '')
            genreList.remove('kay carter')
        if 'kendall faye' in genreList:
            movieCastCrew.addActor('Kendall Faye', '')
            genreList.remove('kendall faye')
        if 'sara luvv' in genreList:
            movieCastCrew.addActor('Sara Luvv', '')
            genreList.remove('sara luvv')

        #  Metadata match
        if 'Cadence' in metadata.title or 'Cadence' in metadata.summary:
            movieCastCrew.addActor('Cadence St. John', '')
        if 'Katrina' in metadata.title or 'Katrina' in metadata.summary:
            movieCastCrew.addActor('Goddess Katrina', '')
        if 'Sara Luvv' in metadata.title or 'Sara Luvv' in metadata.summary:
            movieCastCrew.addActor('Sara Luvv', '')
        if 'Kendall Faye' in metadata.title or 'Kendall Faye' in metadata.summary:
            movieCastCrew.addActor('Kendall Faye', '')

    #  Merciless Dominas
    elif '76999' in userID:
        #  Genre list match
        if 'lady tiger' in genreList:
            movieCastCrew.addActor('Lady Tiger', '')
            genreList.remove('lady tiger')
        if 'princess mckenzie' in genreList:
            movieCastCrew.addActor('Princess Mckenzie', '')
            genreList.remove('princess mckenzie')
        if 'mistress athena' in genreList:
            movieCastCrew.addActor('Mistress Athena', '')
            genreList.remove('mistress athena')
        if 'lady deluxe' in genreList:
            movieCastCrew.addActor('Lady Deluxe', '')
            genreList.remove('lady deluxe')
        if 'chloe lovette' in genreList:
            movieCastCrew.addActor('Chloe Lovette', '')
            genreList.remove('chloe lovette')
        if 'mistress chloe' in genreList:
            movieCastCrew.addActor('Chloe Lovette', '')
            genreList.remove('mistress chloe')
        if 'mistress chloe lovette' in genreList:
            movieCastCrew.addActor('Chloe Lovette', '')
            genreList.remove('mistress chloe lovette')
        if 'miss jessica wood' in genreList:
            movieCastCrew.addActor('Jessica Wood', '')
            genreList.remove('miss jessica wood')

    #  Miss Jade
    elif '61593' in userID:
        movieCastCrew.addActor('Macey Jade', '')
        if 'miss jade' in genreList:
            genreList.remove('miss jade')

    #  Miss Kelle Martina
    elif '34531' in userID:
        movieCastCrew.addActor('Kelle Martina', '')
        if 'kelle martina' in genreList:
            genreList.remove('kelle martina')
        if 'kinky kelle' in genreList:
            genreList.remove('kinky kelle')
        if 'miss kelle' in genreList:
            genreList.remove('miss kelle')

    #  Miss Kira Star
    elif '26860' in userID:
        movieCastCrew.addActor('Kira Star', '')
        if 'kira star' in genreList:
            genreList.remove('kira star')

    #  Miss London Lix Femdom and Fetish
    elif '71286' in userID:
        movieCastCrew.addActor('London Lix', '')
        #  Metadata match
        if 'Bratty Bunny' in metadata.title or 'Bratty Bunny' in metadata.summary:
            movieCastCrew.addActor('Bratty Bunny', '')

    #  Miss Melissa
    elif '58397' in userID:
        movieCastCrew.addActor('Miss Melissa', '')

    #  Miss Noel Knight
    elif '38006' in userID:
        movieCastCrew.addActor('Noel Knight', '')

    #  Miss Roper
    elif '100723' in userID:
        movieCastCrew.addActor('Raquel Roper', '')
        if 'miss roper' in genreList:
            genreList.remove('miss roper')
        if 'raquel roper' in genreList:
            genreList.remove('raquel roper')
        if 'lizzy lamb' in genreList:
            movieCastCrew.addActor('Lizzy Lamb', '')
            genreList.remove('lizzy lamb')
        if 'sasha fox' in genreList:
            movieCastCrew.addActor('Sasha Fox', '')
            genreList.remove('sasha fox')
        if 'anatasia rose' in genreList:
            movieCastCrew.addActor('Anatasia Rose', '')
            genreList.remove('anatasia rose')
        if 'nikki brooks' in genreList:
            movieCastCrew.addActor('Nikki Brooks', '')
            genreList.remove('nikki brooks')
        if 'reagan lush' in genreList:
            movieCastCrew.addActor('Reagan Lush', '')
            genreList.remove('reagan lush')
        if 'carmen velentina' in genreList:
            movieCastCrew.addActor('Carmen Valentina', '')
            genreList.remove('carmen valentina')

    #  Miss Suzanna Maxwell
    elif '129207' in userID:
        movieCastCrew.addActor('Suzanna Maxwell', '')
        #  Genre list match
        if 'suzanna' in genreList:
            genreList.remove('suzanna')
        if 'miss suzanna' in genreList:
            genreList.remove('miss suzanna')
        if 'miss suzanna maxwell' in genreList:
            genreList.remove('miss suzanna maxwell')
        if 'mistress krush' in genreList:
            movieCastCrew.addActor('Mistress Krush', '')
            genreList.remove('mistress krush')
        if 'goddess serena' in genreList:
            movieCastCrew.addActor('Goddess Serana', '')
            genreList.remove('goddess serena')
        if 'mistress courtney' in genreList:
            movieCastCrew.addActor('Mistress Courtney', '')
            genreList.remove('mistress courtney')
        if 'mistress inka' in genreList:
            movieCastCrew.addActor('Mistress Inka', '')
            genreList.remove('mistress inka')
        if 'inka' in genreList:
            movieCastCrew.addActor('Mistress Inka', '')
            genreList.remove('inka')
        if 'ruby marks' in genreList:
            movieCastCrew.addActor('Ruby Marks', '')
            genreList.remove('ruby marks')
        if 'miss ruby marks' in genreList:
            movieCastCrew.addActor('Ruby Marks', '')
            genreList.remove('miss ruby marks')
        if 'ruby' in genreList:
            movieCastCrew.addActor('Ruby Marks', '')
            genreList.remove('ruby')
        #  Metadata match
        if 'Goddess Serena' in metadata.title or 'Goddess Serena' in metadata.summary:
            movieCastCrew.addActor('Goddess Serena', '')
        if 'Mistress Krush' in metadata.title or 'Mistress Krush' in metadata.summary:
            movieCastCrew.addActor('Mistress Krush', '')
        if 'Mistress Marks' in metadata.title or 'Mistress Marks' in metadata.summary:
            movieCastCrew.addActor('Ruby Marks', '')

    #  Miss Untamed FemDom Fetish Clips
    elif '31243' in userID:
        movieCastCrew.addActor('Andrea Untamed', '')
        if 'miss untamed' in genreList:
            genreList.remove('miss untamed')
        if 'andrea untamed' in genreList:
            genreList.remove('andrea untamed')
        if 'stella liberty' in genreList:
            movieCastCrew.addActor('Stella Liberty', '')
            genreList.remove('stella liberty')
        if 'cybill troy' in genreList:
            movieCastCrew.addActor('Cybill Troy', '')
            genreList.remove('cybill troy')
        if 'cupcake sinclair' in genreList:
            movieCastCrew.addActor('Cupcake Sinclair', '')
            genreList.remove('cupcake sinclair')

    #  Mistress - T - Fetish Fuckery
    elif '23869' in userID:
        movieCastCrew.addActor('Mistress T', '')
        if 'astrodomina' in genreList:
            movieCastCrew.addActor('Astro Domina', '')
            genreList.remove('astrodomina')

    #  Mistress Ayn
    elif '74153' in userID:
        movieCastCrew.addActor('Mistress Ayn', '')
        #  Genre list match
        if 'mistress ayn' in genreList:
            genreList.remove('mistress ayn')
        #  Metadata match
        if 'Ultra Violet' in metadata.summary:
            movieCastCrew.addActor('Mistress Ultra Violet', '')
        if 'Kellie Bardot' in metadata.summary:
            movieCastCrew.addActor('Kellie Bardot', '')

    #  Mistress Chantel
    elif '15185' in userID:
        movieCastCrew.addActor('Mistress Chantel', '')

    # Mistress Ezada Sinn
    elif '62191' in userID:
        movieCastCrew.addActor('Ezada Sinn', '')
        if 'ezada' in genreList:
            genreList.remove('ezada')
        if 'sinn' in genreList:
            genreList.remove('sinn')
        if 'ezada sinn' in genreList:
            genreList.remove('ezada sinn')
        if 'domina dinah' in genreList:
            movieCastCrew.addActor('Domina Dinah', '')
            genreList.remove('domina dinah')
        if 'ambra' in genreList:
            movieCastCrew.addActor('Goddess Ambra', '')
        if 'tess' in genreList:
            movieCastCrew.addActor('Mistress Tess', '')
            genreList.remove('tess')
        if 'eris martinet' in genreList:
            movieCastCrew.addActor('Eris Martinet', '')
            genreList.remove('eris martinet')

    #  Mistress Harley Studio
    elif '85619' in userID:
        movieCastCrew.addActor('Mistress Harley', '')

    #  Mistress Jessica Starling
    elif '146727' in userID:
        movieCastCrew.addActor('Jessica Starling', '')

    #  Mistress Kawaii
    elif '108110' in userID:
        movieCastCrew.addActor('Mistress Kawaii', '')
        if 'mistress kawaii' in genreList:
            genreList.remove('mistress kawaii')
        if 'jasmine mendez' in genreList:
            movieCastCrew.addActor('Jasmine Mendez', '')
            genreList.remove('jasmine mendez')

    #  Mistress Lady Renee
    elif '108228' in userID:
        movieCastCrew.addActor('Lady Renee', '')
        if 'mistress lady renee' in genreList:
            genreList.remove('mistress lady renee')
        if 'lady renee' in genreList:
            genreList.remove('lady renee')
        if 'renee' in genreList:
            genreList.remove('renee')
        if 'mistress bliss' in genreList:
            movieCastCrew.addActor('Mistress Bliss', '')
            genreList.remove('mistress bliss')
        if 'fetish liza' in genreList:
            movieCastCrew.addActor('Fetish Liza', '')
            genreList.remove('fetish liza')

    #  Mistress Lola Ruin FemDom Fetish
    elif '60551' in userID:
        movieCastCrew.addActor('Lola Ruin', '')
        if 'lola' in genreList:
            genreList.remove('lola')

    #  Mistress Nikki Whiplash
    elif '96987' in userID:
        movieCastCrew.addActor('Nikki Whiplash', '')
        #  Genre list match
        if 'chloe lovette' in genreList:
            movieCastCrew.addActor('Chloe Lovette', '')
            genreList.remove('chloe lovette')
        if 'mistresschloeuk' in genreList:
            genreList.remove('mistresschloeuk')
        if 'fetish nikki' in genreList:
            movieCastCrew.addActor('Fetish Nikki', '')
            genreList.remove('fetish nikki')
        #  Metadata Match
        if 'Mistress Axa' in metadata.summary:
            movieCastCrew.addActor('Mistress Axa', '')
        if 'Fetish Nikki' in metadata.summary:
            movieCastCrew.addActor('Fetish Nikki', '')
        if 'Chloe' in metadata.summary:
            movieCastCrew.addActor('Chloe Lovette', '')
        if 'Jessica' in metadata.summary:
            movieCastCrew.addActor('Mistress Jessica', '')

    #  Mistress Petra Hunter
    elif '119596' in userID:
        movieCastCrew.addActor('Petra Hunter', '')
        #  Genre list match
        if 'mistress petra hunter' in genreList:
            genreList.remove('mistress petra hunter')
        if 'petra hunter' in genreList:
            genreList.remove('petra hunter')
        #  Metadata match
        if 'Elan Kane' in metadata.summary:
            movieCastCrew.addActor('Elan Kane', '')

    #  Mistress Salem
    elif '98077' in userID:
        movieCastCrew.addActor('Mistress Salem', '')
        if 'mistress salem' in genreList:
            genreList.remove('mistress salem')

    #  MistressVictoria
    elif '75307' in userID:
        movieCastCrew.addActor('Vikki Lynn', '')
        if 'mistressvictoria' in genreList:
            genreList.remove('mistressvictoria')
        if 'missvikki' in genreList:
            genreList.remove('missvikki')
        if 'missvikkilynn' in genreList:
            genreList.remove('missvikkilynn')
        if 'twins brooke and vikki' in genreList:
            genreList.remove('twins brooke and vikki')
        if 'twin brooke and vikki' in genreList:
            genreList.remove('twin brooke and vikki')
        if 'mistress vikki lynn' in genreList:
            genreList.remove('mistress vikki lynn')
        if 'twin nikki' in genreList:
            genreList.remove('twin nikki')

    #  Morgan Rain
    elif 'Morgan Rain' in tagline:
        movieCastCrew.addActor('Morgan Rain', '')
        if 'morgan rain' in genreList:
            genreList.remove('morgan rain')
        if 'morgan' in genreList:
            genreList.remove('morgan')
        if 'caitlyn brooks' in genreList:
            movieCastCrew.addActor('Caitlyn Brooks', '')
            genreList.remove('caitlyn brooks')
        if 'jaycee starr' in genreList:
            movieCastCrew.addActor('Jaycee Starr', '')
            genreList.remove('jaycee starr')

    #  My Fetish Addictions
    elif '40470' in userID:
        movieCastCrew.addActor('Maya Sintress', '')
        if 'miss maya sintress' in genreList:
            genreList.remove('miss maya Sintress')
        if 'maya sintress' in genreList:
            genreList.remove('maya sintress')
        if 'julie rocket' in genreList:
            movieCastCrew.addActor('Julie Rocket', '')
            genreList.remove('julie rocket')
        if 'kendra james' in genreList:
            movieCastCrew.addActor('Kendra James', '')
            genreList.remove('kendra james')
        if 'sully savage' in genreList:
            movieCastCrew.addActor('Sully Savage', '')
            genreList.remove('sully savage')
        if 'princess seva' in genreList:
            movieCastCrew.addActor('Princess Seva', '')
            genreList.remove('princess seva')
        if 'queen vanity' in genreList:
            movieCastCrew.addActor('Queen Vanity', '')
            genreList.remove('queen vanity')
        if 'queen paris' in genreList:
            movieCastCrew.addActor('Queen Paris', '')
            genreList.remove('queen paris')

    #  Mz Devious Fetish Clips
    elif '22493' in userID:
        movieCastCrew.addActor('Mz Devious', '')
        if 'mz devious' in genreList:
            genreList.remove('mz devious')
        if 'princess danni' in genreList:
            genreList.remove('princess danni')

    #  Natashas Bedroom
    elif "72779" in userID:
        movieCastCrew.addActor('Goddess Natasha', '')
        if 'natasha' in genreList:
            genreList.remove('natasha')
        if 'natasha\'s bedroom' in genreList:
            genreList.remove('natasha\'s bedroom')
        if 'goddess natasha' in genreList:
            genreList.remove('goddess natasha')

    #  Obey Miss Tiffany
    elif '100823' in userID:
        movieCastCrew.addActor('Miss Tiffany', '')

    #  Play With Amai
    elif '47204' in userID:
        movieCastCrew.addActor('Amai Liu', '')
        if 'amai' in genreList:
            genreList.remove('amai')
        if 'liu' in genreList:
            genreList.remove('liu')
        if 'amai liu' in genreList:
            genreList.remove('amai liu')

    #  Princess Alexa Findom and Fetish
    elif '108870' in userID:
        movieCastCrew.addActor('Princess Alexa', '')
        if 'alexa' in genreList:
            genreList.remove('alexa')
        if 'alexaholic' in genreList:
            genreList.remove('alexaholic')

    #  Princess Amy Latina
    elif '80717' in userID:
        movieCastCrew.addActor('Amy Latina', '')

    #  Princess Ashley's Clip Store
    elif '80339' in userID:
        movieCastCrew.addActor('Princess Ashley', '')
        if 'princess ashley' in genreList:
            genreList.remove('princess ashley')

    #  Princess Beverly
    elif '111744' in userID:
        movieCastCrew.addActor('Princess Beverly', '')

    #  PRINCESS BREANNA'S STORE FOR LOSERS
    elif '52369' in userID:
        movieCastCrew.addActor('Princess Breanna', '')
        if 'princess breanna' in genreList:
            genreList.remove('princess breanna')

    #  Princess Brook Humiliatrix
    elif '49727' in userID:
        movieCastCrew.addActor('Princess Brook', '')

    #  Princess Camryn
    elif '117722' in userID:
        movieCastCrew.addActor('Princess Camryn', '')

    #  Princess Ellie Idol
    elif '44689' in userID:
        movieCastCrew.addActor('Ellie Idol', '')
        if 'princess ellie idol' in genreList:
            genreList.remove('princess ellie idol')
        if 'london lix' in genreList:
            movieCastCrew.addActor('London Lix', '')

    #  Princess Fierce
    elif '2683' in userID:
        movieCastCrew.addActor('Princess Fierce', '')

    #  Princess Jessy Belle
    elif '72533' in userID:
        movieCastCrew.addActor('Jessy Belle', '')

    #  Princess Kimber Lee
    elif '82669' in userID:
        movieCastCrew.addActor('Kimber Lee', '')
        if 'kimber lee' in genreList:
            genreList.remove('kimber lee')
        if 'princess kimber lee' in genreList:
            genreList.remove('princess kimber lee')
        if 'kimberleelive' in genreList:
            genreList.remove('kimberleelive')

    #  Princess Larkin
    elif 'Princess Larkin' in tagline:
        movieCastCrew.addActor('Larkin Love', '')
        if 'larkin love' in genreList:
            genreList.remove('larkin love')
        if 'queen bitch larkin' in genreList:
            genreList.remove('queen bitch larkin')
        if 'princess larkin' in genreList:
            genreList.remove('princess larkin')

    #  Princess Lexie's Clip Store
    elif '18754' in userID:
        movieCastCrew.addActor('Princess Lexie', '')

    #  Princess Lucy
    elif '79807' in userID:
        movieCastCrew.addActor('Princess Lucy', '')

    #  Princess Mackaylas Sinpire
    elif '35918' in userID:
        movieCastCrew.addActor('Princess Mackayla', '')
        if 'princess mackayla' in genreList:
            genreList.remove('princess mackayla')

    #  Princess Samantha
    elif '43948' in userID:
        movieCastCrew.addActor('Princess Samantha', '')

    #  Princess Shaye
    elif '121305' in userID:
        movieCastCrew.addActor('Princess Shay', '')

    #  Princess Tammie
    elif '101081' in userID:
        movieCastCrew.addActor('Tammie Madison', '')
        if 'princess tammie' in genreList:
            genreList.remove('princess tammie')
        if 'tammie madison' in genreList:
            genreList.remove('tammie madison')
        if 'tammie_' in genreList:
            genreList.remove('tammie_')

    #  Psyche Abuse - Goddess Eliza
    elif '89304' in userID:
        movieCastCrew.addActor('Goddess Eliza', '')
        if 'goddess eliza' in genreList:
            genreList.remove('goddess eliza')

    #  Queen Amber Mae
    elif '97281' in userID:
        movieCastCrew.addActor('Amber Mae', '')
        if 'amber mae' in genreList:
            genreList.remove('amber mae')
        if 'goddess amber mae' in genreList:
            genreList.remove('goddess amber mae')

    #  Queen Brea
    elif '135591' in userID:
        movieCastCrew.addActor('Queen Brea', '')
        movieCastCrew.addActor('Vanessa Zaleska', '')

    #  QUEEN JENNIFER MARIE
    elif '119056' in userID:
        movieCastCrew.addActor('Jennifer Marie', '')
        if 'queenjennifermarie' in genreList:
            genreList.remove('queenjennifermarie')

    #  Raptures Fetish Playground
    elif '77159' in userID:
        #  Genre list match
        if 'bella ink' in genreList:
            movieCastCrew.addActor('Bella Ink', '')
            genreList.remove('bella ink')
        if 'bella' in genreList:
            genreList.remove('bella')
        if 'cameron dee' in genreList:
            movieCastCrew.addActor('Cameron Dee', '')
            genreList.remove('cameron dee')
        #  Metadata match
        if 'Lilith' in metadata.title or 'Lilith' in metadata.summary:
            movieCastCrew.addActor('Lilith', '')

    #  reiinapop
    elif '97977' in userID:
        movieCastCrew.addActor('Reiinapop', '')

    #  Ruby Rousson
    elif '78481' in userID:
        movieCastCrew.addActor('Ruby Rousson', '')
        if 'ruby rousson' in genreList:
            genreList.remove('ruby rousson')
        if 'mistress rousson' in genreList:
            genreList.remove('mistress rousson')

    #  Sadurnus New Moon
    elif '109570' in userID:
        #  Metadata match
        if 'Mistress Tatjana' in metadata.title or 'Mistress Tatjana' in metadata.summary or 'Tatjana' in metadata.title or 'Tatjana' in metadata.summary:
            movieCastCrew.addActor('Mistress Tatjana', '')
        if 'Darcia Lee' in metadata.title or 'Darcia Lee' in metadata.summary:
            movieCastCrew.addActor('Darcia Lee', '')

    #  Sarah DiAvola
    elif '14248' in userID:
        movieCastCrew.addActor('Sarah DiAvola', '')
        if 'brat princess sarah' in genreList:
            genreList.remove('brat princess sarah')
        if 'sarah diavola' in genreList:
            genreList.remove('sarah diavola')
        if 'andrea dipre' in genreList:
            movieCastCrew.addActor('Andrea Dipre', '')
            genreList.remove('andrea dipre')
        if 'maria marley' in genreList:
            movieCastCrew.addActor('Maria Marley', '')
            genreList.remove('maria marley')

    #  Savannahs Fetish Fantasies
    elif '95249' in userID:
        movieCastCrew.addActor('Savannah Fox', '')
        if 'skylar renee' in genreList:
            movieCastCrew.addActor('Skylar Renee', '')
            genreList.remove('skylar renee')
        if 'lauren phillips' in genreList:
            movieCastCrew.addActor('Lauren Phillips', '')
            genreList.remove('lauren phillips')
        if 'andrea roso' in genreList:
            movieCastCrew.addActor('Andrea roso', '')
            genreList.remove('andrea roso')
        if 'anrea rosu' in genreList:
            movieCastCrew.addActor('Andrea Roso', '')
            genreList.remove('andrea rosu')
        if 'arena rome' in genreList:
            movieCastCrew.addActor('Arena Rome', '')
            genreList.remove('arena rome')
        if 'brandie mae' in genreList:
            movieCastCrew.addActor('Brandie Mae', '')
            genreList.remove('brandie mae')
        if 'monica mynx' in genreList:
            movieCastCrew.addActor('Monica Mynx', '')
            genreList.remove('monica mynx')
        if 'jasmeen lafleaur' in genreList:
            movieCastCrew.addActor('Jasmeen Lafleaur', '')
            genreList.remove('jasmeen lafleaur')
        if 'jasmmen lafleur' in genreList:
            movieCastCrew.addActor('Jasmeen Lafleaur', '')
            genreList.remove('jasmmen lafleur')
        if 'lux lives' in genreList:
            movieCastCrew.addActor('Lux Lives', '')
            genreList.remove('lux lives')
        if 'cali carter' in genreList:
            movieCastCrew.addActor('Cali Carter', '')
            genreList.remove('cali carter')
        if 'cali logan' in genreList:
            movieCastCrew.addActor('Cali Logan', '')
            genreList.remove('cali logan')

    #  She Owns Your Manhood
    elif '46144' in userID:
        #  Genre list match
        if 'lily lane' in genreList:
            movieCastCrew.addActor('Lily Lane', '')
            genreList.remove('lily lane')
        if 'sharron small' in genreList:
            movieCastCrew.addActor('Sharron Small', '')
            genreList.remove('sharron small')
        if 'alexa ray' in genreList:
            movieCastCrew.addActor('Alexa Ray', '')
            genreList.remove('alexa ray')
        if 'vivienne lamour' in genreList:
            movieCastCrew.addActor('Vivienne Lamour', '')
            genreList.remove('vivienne lamour')
        if 'lance hart' in genreList:
            movieCastCrew.addActor('Lance Hart', '')
            genreList.remove('lance hart')
        #  Metadata Match
        if 'Vivenne LAmours' in metadata.summary or 'VIVIENNE LAMOUR' in metadata.summary:
            movieCastCrew.addActor('Vivienne Lamour', '')

    #  Siren Thorn Inked Asian Goddess
    elif '43580' in userID:
        movieCastCrew.addActor('Siren Thorn', '')
        #  Genre list match
        if 'siren thorn' in genreList:
            genreList.remove('siren thorn')
        if 'miss xi' in genreList:
            movieCastCrew.addActor('Miss Xi', '')
            genreList.remove('miss xi')
        if 'latex barbie' in genreList:
            movieCastCrew.addActor('Latex Barbie', '')
            genreList.remove('latex barbie')
        #  Metadata match
        if 'Miss Xi' in metadata.summary:
            movieCastCrew.addActor('Miss Xi', '')

    #  Slutty Magic
    elif '117288' in userID:
        if 'chanel santini' in genreList:
            movieCastCrew.addActor('Chanel Santini', '')
            genreList.remove('chanel santini')
        if 'cory chase' in genreList:
            movieCastCrew.addActor('Cory Chase', '')
            genreList.remove('cory chase')
        if 'cory chase pegging' in genreList:
            genreList.remove('cory chase pegging')
        if 'alex adams' in genreList:
            movieCastCrew.addActor('Alex Adams', '')
            genreList.remove('alex adams')
        if 'lance hart' in genreList:
            movieCastCrew.addActor('Lance Hart', '')
            genreList.remove('lance hart')
        if 'charlotte sartre' in genreList:
            movieCastCrew.addActor('Charlotte Sartre', '')
            genreList.remove('charlotte sartre')
        if 'alex cole' in genreList:
            movieCastCrew.addActor('Alex Cole', '')
            genreList.remove('alex cole')
        if 'lily lane' in genreList:
            movieCastCrew.addActor('Lily Lane', '')
            genreList.remove('lily lane')
        if 'whitney morgan' in genreList:
            movieCastCrew.addActor('Whitney Morgan', '')
            genreList.remove('whitney morgan')
        if 'sarah diavola' in genreList:
            movieCastCrew.addActor('Sarah DiAvola', '')
            genreList.remove('sarah diavola')
        if 'nikki hearts' in genreList:
            movieCastCrew.addActor('Nikki Hearts', '')
            genreList.remove('nikki hearts')

    #  SparklyHots hot clips
    elif '64639' in userID:
        movieCastCrew.addActor('SparklyHot', '')

    #  SpittingBitches
    elif '26262' in userID:
        if 'serena' in genreList:
            movieCastCrew.addActor('Serena Ice', '')
            genreList.remove('serena')
        if 'serena ice' in genreList:
            movieCastCrew.addActor('Serana Ice', '')
            genreList.remove('serena ice')
        if 'ice' in genreList:
            movieCastCrew.addActor('Serana Ice', '')
            genreList.remove('ice')
        if 'trinity' in genreList:
            movieCastCrew.addActor('Trinity', '')
            genreList.remove('trinity')
        if 'amber' in genreList:
            movieCastCrew.addActor('Amber', '')
            genreList.remove('amber')

    #  Stella Liberty
    elif '101957' in userID:
        movieCastCrew.addActor('Stella Liberty', '')
        if 'stella liberty' in genreList:
            genreList.remove('stella liberty')
        if 'andrea untamed' in genreList:
            movieCastCrew.addActor('Andrea Untamed', '')
            genreList.remove('andrea untamed')

    #  Strapon Encouragement - Dirty TalkS
    elif '7640' in userID:
        #  Genre list match
        if 'brea bennette' in genreList:
            movieCastCrew.addActor('Brea Bennette', '')
            genreList.remove('brea bennette')
        if 'lexi belle' in genreList:
            movieCastCrew.addActor('Lexi Belle', '')
            genreList.remove('lexi belle')
        #  Metadata match
        if 'Tiffany Brookes' in metadata.summary or 'Tiffany' in metadata.summary:
            movieCastCrew.addActor('Tiffany Brookes', '')

    #  Tammie Madison
    elif '95015' in userID:
        movieCastCrew.addActor('Tammie Madison', '')
        if 'tammie madison' in genreList:
            genreList.remove('tammie madison')
        if 'tammie_' in genreList:
            genreList.remove('tammie_')

    #  Tara Tainton
    elif '21571' in userID:
        movieCastCrew.addActor('Tara Tainton', '')
        if 'tara tainton' in genreList:
            genreList.remove('tara tainton')
        if 'the real tara tainton' in genreList:
            genreList.remove('the real tara tainton')

    #  The AnnabelFatalecom store
    elif '65455' in userID:
        movieCastCrew.addActor('Annabel Fatale', '')
        if 'annabellefatale' in genreList:
            genreList.remove('annabellefatale')
        if 'annabelle' in genreList:
            genreList.remove('annabelle')

    #  THE MEAN GIRLS
    elif '32364' in userID:
        #  Genre list match
        if 'goddess harley' in genreList:
            movieCastCrew.addActor('Goddess Harley', '')
            genreList.remove('goddess harley')
        if 'princess carmela' in genreList:
            movieCastCrew.addActor('Princess Carmela', '')
            genreList.remove('princess carmela')
        if 'carmela' in genreList:
            movieCastCrew.addActor('Princess Carmela', '')
            genreList.remove('carmela')
        if 'cindi' in genreList:
            movieCastCrew.addActor('Princess Cindi', '')
            genreList.remove('cindi')
        if 'princess bella' in genreList:
            movieCastCrew.addActor('Princess Bella', '')
            genreList.remove('princess bella')
        if 'queen grace' in genreList:
            movieCastCrew.addActor('Queen Grace', '')
            genreList.remove('queen grace')
        if 'goddess platinum' in genreList:
            movieCastCrew.addActor('Goddess Platinum', '')
            genreList.remove('goddess platinum')
        if 'princess amber' in genreList:
            movieCastCrew.addActor('Princess Amber', '')
            genreList.remove('princess amber')
        if 'goddess draya' in genreList:
            movieCastCrew.addActor('Goddess Draya', '')
            genreList.remove('goddess draya')
        if 'tina' in genreList:
            movieCastCrew.addActor('Goddess Tina', '')
            genreList.remove('tina')
        if 'princess tia' in genreList:
            movieCastCrew.addActor('Princess Tia', '')
            genreList.remove('princess tia')
        if 'princess arianna' in genreList:
            movieCastCrew.addActor('Princess Arianna', '')
            genreList.remove('princess arianna')
        if 'princess natalia' in genreList:
            movieCastCrew.addActor('Princess Natalia', '')
            genreList.remove('princess natalia')
        if 'princess beverly' in genreList:
            movieCastCrew.addActor('Princess Beverly', '')
            genreList.remove('princess beverly')
        if 'princess chanel' in genreList:
            movieCastCrew.addActor('Princess Chanel', '')
            genreList.remove('princess chanel')
        if 'princess ashley' in genreList:
            movieCastCrew.addActor('Princess Ashley', '')
            genreList.remove('princess ashley')
        if 'goddess charlotte' in genreList:
            movieCastCrew.addActor('Charlotte Stokely', '')
            genreList.remove('goddess charlotte')
        if 'goddess rodea' in genreList:
            movieCastCrew.addActor('Goddess Rodea', '')
            genreList.remove('goddess rodea')
        if 'tasha reign' in genreList:
            movieCastCrew.addActor('Tasha Reign', '')
            genreList.remove('tasha reign')

        #  Metadata match
        if 'Goddess Suvana' in metadata.summary or 'GODDESS SUVANA' in metadata.summary:
            movieCastCrew.addActor('Goddess Suvana', '')
        if 'Empress Jennifer' in metadata.summary or 'EMPRESS JENNIFER' in metadata.summary or 'P. Jenn' in metadata.summary or 'PJenn' in metadata.summary:
            movieCastCrew.addActor('Empress Jennifer', '')
        if 'Goddess Charlotte Stokely' in metadata.summary:
            movieCastCrew.addActor('Charlotte Stokely', '')
        if 'QUEEN KASEY' in metadata.summary:
            movieCastCrew.addActor('Queen Kasey', '')
        if 'Princess Cindi' in metadata.summary:
            movieCastCrew.addActor('Princess Cindi', '')
        if 'Ash Hollywood' in metadata.summary:
            movieCastCrew.addActor('Ash Hollywood', '')

        # Metadata match (would not work in the "elif 71196" block)
        if 'P-Jenn' in metadata.title:
            movieCastCrew.addActor('Empress Jennifer', '')
        if 'Princess PERFECTION' in metadata.summary:
            movieCastCrew.addActor('Princess Perfection', '')
        if 'Goddess Farrah' in metadata.summary:
            movieCastCrew.addActor('Goddess Farrah', '')
        if 'Goddess Alexis' in metadata.summary:
            movieCastCrew.addActor('Goddess Alexis', '')
        if 'Goddess Nina' in metadata.summary:
            movieCastCrew.addActor('Goddess Nina', '')
        if 'Goddess Randi' in metadata.summary:
            movieCastCrew.addActor('Goddess Randi', '')

    #  THE MEAN GIRLS- P O V
    elif '71196' in userID:
        #  Genre list match
        if 'goddess harley' in genreList:
            movieCastCrew.addActor('Goddess Harley', '')
            genreList.remove('goddess harley')
        if 'princess nikkole' in genreList:
            movieCastCrew.addActor('Princess Nikkole', '')
            genreList.remove('princess nikkole')
        if 'princess beverly' in genreList:
            movieCastCrew.addActor('Princess Beverly', '')
            genreList.remove('princess beverly')
        if 'princess ashley' in genreList:
            movieCastCrew.addActor('Princess Ashley', '')
            genreList.remove('princess ashley')
        if 'princess chanel' in genreList:
            movieCastCrew.addActor('Princess Chanel', '')
            genreList.remove('princess chanel')
        if 'princess amber' in genreList:
            movieCastCrew.addActor('Princess Amber', '')
            genreList.remove('princess amber')
        if 'ash hollywood' in genreList:
            movieCastCrew.addActor('Ash Hollywood', '')
            genreList.remove('ash hollywood')
        #  Metadata match
        if 'Queen Kasey' in metadata.summary:
            movieCastCrew.addActor('Queen Kasey', '')

    #  The Mistress B
    elif '47623' in userID:
        movieCastCrew.addActor('Mistress B', '')

    #  The Princess Miki
    elif '132509' in userID:
        movieCastCrew.addActor('Princess Miki', '')
        if 'princess miki' in genreList:
            genreList.remove('princess miki')
        if 'miki' in genreList:
            genreList.remove('miki')

    #  Trixie Miss
    elif '36476' in userID:
        movieCastCrew.addActor('Trixis Miss', '')
        if 'trixie miss' in genreList:
            genreList.remove('trixie miss')

    #  Tsarina Baltic
    elif '116628' in userID:
        movieCastCrew.addActor('Tsarina Baltic', '')

    #  valeriesins
    elif '218883' in userID:
        movieCastCrew.addActor('Valerie Sins', '')
        if 'valeriesins' in genreList:
            genreList.remove('valeriesins')

    #  Verbal Humiliatrix Princess Lacey
    elif '20051' in userID:
        movieCastCrew.addActor('Princess Lacey', '')

    #  Vixen Palace
    elif '133311' in userID:
        movieCastCrew.addActor('Miss Vixen', '')

    #  Welcome to Smutty Vallie
    elif '75215' in userID:
        movieCastCrew.addActor('Vallie Beuys', '')
        if 'vallie beuys' in genreList:
            genreList.remove('vallie beuys')
        if 'vallie' in genreList:
            genreList.remove('vallie')
        if 'mistress vallie' in genreList:
            genreList.remove('mistress vallie')
        if 'miss vallie' in genreList:
            genreList.remove('miss vallie')

    #  Worship Amanda
    elif '75883' in userID:
        movieCastCrew.addActor('Goddess Amanda', '')

    #  Worship Goddess Jasmine
    elif '40399' in userID:
        movieCastCrew.addActor('Jasmine Jones', '')
        if 'jasmine jones' in genreList:
            genreList.remove('jasmine jones')
        if 'goddess jasmine' in genreList:
            genreList.remove('goddess jasmine')
        if 'princess danielle' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('princess danielle')
        if 'danni maye' in genreList:
            movieCastCrew.addActor('Danielle Maye', '')
            genreList.remove('danni maye')

    #  WORSHIP Princess NINA
    elif '96967' in userID:
        movieCastCrew.addActor('Princess Nina', '')
        if 'worship princess nina' in genreList:
            genreList.remove('worship princess nina')
        if 'bratty princess nina' in genreList:
            genreList.remove('bratty princess nina')

    #  Worship The Wolfe
    elif '103711' in userID:
        movieCastCrew.addActor('Janira Wolfe', '')
        if 'janira wolfe' in genreList:
            genreList.remove('janira wolfe')
        if 'worship the wolfe' in genreList:
            genreList.remove('worship the wolfe')
        if 'elis ataxxx' in genreList:
            movieCastCrew.addActor('Elis Ataxxx', '')
            genreList.remove('elis ataxxx')
        if 'rick fantana' in genreList:
            movieCastCrew.addActor('Rick Fantana', '')
            genreList.remove('rick fantana')

    #  Worship Violet Doll
    elif '52729' in userID:
        movieCastCrew.addActor('Violet Doll', '')
        if 'violet doll' in genreList:
            genreList.remove('violet doll')
        if 'violet doll joi' in genreList:
            genreList.remove('violet doll joi')
        if 'violet doll ass worship' in genreList:
            genreList.remove('violet doll ass worship')

    #  xRussianBeautyx Clip Store
    elif 'xRussianBeautyx Clip Store' in tagline:
        movieCastCrew.addActor('Russian Beauty', '')

    #  Young Goddess Kim
    elif '107054' in userID:
        movieCastCrew.addActor('Young Goddess Kim', '')
        if 'young goddess kim' in genreList:
            genreList.remove('young goddess kim')

    #  Larkin Love
    elif 'Larkin Love' in tagline:
        movieCastCrew.addActor('Larkin Love', '')

    #  Lovely Liliths Lusty Lair
    elif '63727' in userID:
        movieCastCrew.addActor('Lovely Lilith', '')

    #  PORN STAR Siri: Fetish/Custom Clips
    elif '56567' in userID:
        movieCastCrew.addActor('Siri', '')

    else:
        actorName = tagline
        actorPhotoURL = ''
        movieCastCrew.addActor(actorName, actorPhotoURL)
    # Add Genres
    for genre in genreList:
        movieGenres.addGenre(genre)

    # Posters
    art.append('http://imagecdn.clips4sale.com/accounts99/%s/clip_images/previewlg_%s.jpg' % (userID, sceneID))

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
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


def getCleanTitle(title):
    for format_ in formats:
        for quality in qualities:
            for fileType in fileTypes:
                title = title.replace(format_ % {'quality': quality.lower(), 'fileType': fileType.lower()}, '')
                title = title.replace(format_ % {'quality': quality.lower(), 'fileType': fileType.upper()}, '')
                title = title.replace(format_ % {'quality': quality.upper(), 'fileType': fileType.lower()}, '')
                title = title.replace(format_ % {'quality': quality.upper(), 'fileType': fileType.upper()}, '')

    return title.strip()


fileTypes = [
    'mp4',
    'wmv',
    'avi',
]


qualities = [
    'standard',
    'hd',
    '720p',
    '1080p',
    '4k',
]


formats = [
    '(%(quality)s - %(quality)s)',
    '(%(quality)s %(fileType)s)',
    '%(quality)s %(fileType)s',
    '- %(quality)s;',
    '(.%(fileType)s)',
    '(%(quality)s)',
    '(%(fileType)s)',
    '.%(fileType)s',
    '%(quality)s',
    '%(fileType)s',
]
