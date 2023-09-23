import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchResults = HTML.ElementFromString(req.text)
    for searchResult in searchResults.xpath('//div[@align="left"]'):
        titleNoFormatting = searchResult.xpath('.//td[@valign="top"][2]/a')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('.//td[@valign="top"][2]/a/@href')[0])

        date = searchResult.xpath('.//span[@class="date"]')[0].text_content().replace('Added', '').strip()
        releaseDate = parse(date).strftime('%Y-%m-%d')

        if searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [FuelVirtual/%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    siteName = PAsearchSites.getSearchSiteName(siteNum).strip()
    sceneURL = PAutils.Decode(metadata_id[0])
    if siteName == 'NewGirlPOV':
        server_path = '/tour/newgirlpov/'
    else:
        server_path = '/membersarea/'
    sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + server_path + sceneURL

    sceneDate = metadata_id[2]
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    if siteName == 'NewGirlPOV':
        metadata.title = detailsPageElements.xpath('//title')[0].text_content().split(' ')[1].strip()
    else:
        metadata.title = detailsPageElements.xpath('//title')[0].text_content().split('-')[0].strip()

    # Studio
    metadata.studio = 'FuelVirtual'

    # Tagline and Collection(s)
    tagline = siteName
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    for genreLink in detailsPageElements.xpath('//td[@class="plaintext"]/a[@class="model_category_link"]'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)
    if siteName != 'NewGirlPOV':
        movieGenres.addGenre('18-Year-Old')

    # Actor(s)
    actors = detailsPageElements.xpath('//div[@id="description"]//td[@align="left"]/a')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        actorPhotoURL = ''

        # Ambiguous actors must be hardcoded by ID
        found_scene_id = False
        scene_id = re.search(r'id=(\d+)', sceneURL)
        if scene_id:
            scene_id = int(scene_id.group(1))
            if siteName in actor_db and scene_id in actor_db[siteName]:
                found_scene_id = True
                for actorName in actor_db[siteName][scene_id]:
                    movieActors.addActor(actorName, actorPhotoURL)

        if not found_scene_id:
            for actorLink in actors:
                actorName = actorLink.text_content().strip()
                movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//a[@class="jqModal"]/img/@src',
        '//div[@id="overallthumb"]/a/img/@src',
    ]
    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if img.startswith('/'):
                img = PAsearchSites.getSearchBaseURL(siteNum) + img
            else:
                img = PAsearchSites.getSearchBaseURL(siteNum) + '/tour/newgirlpov/' + img

            art.append(img)

    photoPageUrl = sceneURL.replace('vids', 'highres')
    req = PAutils.HTTPRequest(photoPageUrl)
    photoPage = HTML.ElementFromString(req.text)
    for img in photoPage.xpath('//a[@class="jqModal"]/img/@src'):
        img = PAsearchSites.getSearchBaseURL(siteNum) + img

        art.append(img)

    re_img = re.compile(r'image:\s*"(.+)"')
    for script in detailsPageElements.xpath('//div[@id="mediabox"]/script/text()'):
        match = re_img.search(script)
        if match:
            art.append(PAsearchSites.getSearchBaseURL(siteNum) + match.group(1))

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


actor_db = {
    'FuckedHard18': {
        434: ['Abby Lane'],
        435: ['Abby Cross'],
        445: ['Alexa Rydell'],
        446: ['Alexa Nicole'],
        469: ['Alexis Grace'],
        470: ['Ashley Abott'],
        474: ['Ashlyn Molloy'],
        481: ['Ava White'],
        482: ['Ava Sparxxx'],
        483: ['Ava Taylor'],
        486: ['Dahlia Sky'],
        487: ['Bailey Bam'],
        501: ['Callie Cobra'],
        502: ['Callie Cyprus'],
        503: ['Callie Calypso'],
        522: ['Chloe Addison'],
        523: ['Chloe Brooke'],
        524: ['Chloe Foster'],
        553: ['Gracie Glam'],
        554: ['Gracie Ivanoe'],
        558: ['Holly Sims'],
        559: ['Holly Michaels'],
        572: ['Jenna Ashley'],
        573: ['Jenna Ross'],
        591: ['Katie Jordin'],
        592: ['Katie Michaels'],
        612: ['Lexi Bloom'],
        613: ['Lexi Swallow'],
        621: ['Lily Love'],
        622: ['Lily Carter'],
        625: ['Lola Foxx'],
        648: ['Melissa Mathews'],
        651: ['Mia Malkova'],
        652: ['Mia Gold'],
        661: ['Molly Madison'],
        662: ['Molly Bennett'],
        668: ['Naomi West'],
        684: ['Rachel Rogers'],
        685: ['Rachel Roxxx'],
        686: ['Rachel Bella'],
        692: ['Riley Ray'],
        693: ['Riley Jensen', 'Celeste Star'],
        694: ['Riley Reid'],
        695: ['Chanel White'],
        703: ['Samantha Ryan'],
        717: ['Sophia Sutra'],
        718: ['Sophia Striker'],
        728: ['Taylor Tilden'],
        729: ['Taylor Whyte'],
        749: ['Veronica Radke'],
        750: ['Veronica Rodriguez'],
        757: ['Whitney Stevens'],
        825: ['Alexa Grace'],
        839: ['Abby Cross'],
        947: ['Melissa May'],
    },
    'MassageGirls18': {
        134: ['Melissa Mathews'],
        135: ['Melissa Mathews'],
        137: ['Abby Paradise'],
        138: ['Abby Cross'],
        139: ['Abby Lane'],
        147: ['Alexa Nicole'],
        148: ['Alexa Rydell'],
        169: ['Ashley Abott'],
        170: ['Alexis Grace'],
        178: ['Ava Sparxxx'],
        179: ['Ava White'],
        181: ['Bailey Bam'],
        183: ['Dahlia Sky'],
        196: ['Callie Calypso'],
        197: ['Callie Cobra'],
        198: ['Callie Cyprus'],
        211: ['Riley Jensen', 'Celeste Star'],
        213: ['Chloe Skyy'],
        215: ['Chloe Brooke'],
        242: ['Gracie Glam'],
        243: ['Gracie Ivanoe'],
        248: ['Holly Sims'],
        249: ['Holly Michaels'],
        262: ['Jenna Ross'],
        276: ['Katie Jordin'],
        277: ['Katie Michaels'],
        278: ['Katie Summers'],
        301: ['Lily Carter'],
        302: ['Lily Love'],
        305: ['Lola Foxx'],
        332: ['Mia Gold'],
        333: ['Mia Malkova'],
        341: ['Molly Bennett'],
        342: ['Molly Madison'],
        361: ['Rachel Bella'],
        362: ['Rachel Roxxx'],
        367: ['Riley Ray'],
        368: ['Chanel White'],
        394: ['Sophia Striker'],
        395: ['Sophia Sutra'],
        403: ['Taylor Whyte'],
        404: ['Taylor Tilden'],
        422: ['Veronica Radke'],
        423: ['Veronica Rodriguez'],
        768: ['Samantha Rone'],
        828: ['Bailey Bae'],
    },
    'NewGirlPOV': {
        1159: ['Ashley Adams'],
        1178: ['Lola Hunter'],
        1206: ['Molly Manson'],
        1242: ['Naomi Woods'],
        1280: ['Melissa Moore'],
    },
}
