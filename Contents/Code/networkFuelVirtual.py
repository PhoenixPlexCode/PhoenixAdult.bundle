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
    if siteName == 'NewGirlPOV':
        server_path = '/tour/newgirlpov/'
    else:
        server_path = '/membersarea/'
    sceneURL = '%s%s%s' % (PAsearchSites.getSearchBaseURL(siteNum), server_path, PAutils.Decode(metadata_id[0]))
    Log('sceneURL: {}'.format(sceneURL))
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
    metadata.collections.clear()
    tagline = siteName
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    if sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
        Log('{} recycles content, release date may be inaccurate'.format(tagline))

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//td[@class="plaintext"]/a[@class="model_category_link"]'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)
    if siteName != 'NewGirlPOV':
        movieGenres.addGenre('18-Year-Old')

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//div[@id="description"]//td[@align="left"]/a')
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content().strip()
            actorPhotoURL = ''

            # Ambiguous actors must be hardcoded by ID
            actorID = int(re.search(r'id=(\d+)', PAutils.Decode(metadata_id[0])).group(1))
            if siteName == 'FuckedHard18':
                if False:
                    pass
                elif actorID == 435 or actorID == 839:
                    actorName = 'Abby Cross'
                elif actorID == 434:
                    actorName = 'Abby Lane'
                elif actorID == 825:
                    actorName = 'Alexa Grace'
                elif actorID == 446:
                    actorName = 'Alexa Nicole'
                elif actorID == 445:
                    actorName = 'Alexa Rydell'
                elif actorID == 469:
                    actorName = 'Alexis Grace'
                elif actorID == 470:
                    actorName = 'Ashley Abott'
                elif actorID == 474:
                    actorName = 'Ashlyn Molloy'
                elif actorID == 482:
                    actorName = 'Ava Sparxxx'
                elif actorID == 483:
                    actorName = 'Ava Taylor'
                elif actorID == 481:
                    actorName = 'Ava White'
                elif actorID == 487:
                    actorName = 'Bailey Bam'
                elif actorID == 503:
                    actorName = 'Callie Calypso'
                elif actorID == 501:
                    actorName = 'Callie Cobra'
                elif actorID == 502:
                    actorName = 'Callie Cyprus'
                elif actorID == 695:
                    actorName = 'Chanel White'
                elif actorID == 522:
                    actorName = 'Chloe Addison'
                elif actorID == 523:
                    actorName = 'Chloe Brooke'
                elif actorID == 524:
                    actorName = 'Chloe Foster'
                elif actorID == 486:
                    actorName = 'Dahlia Sky'
                elif actorID == 553:
                    actorName = 'Gracie Glam'
                elif actorID == 554:
                    actorName = 'Gracie Ivanoe'
                elif actorID == 559:
                    actorName = 'Holly Michaels'
                elif actorID == 558:
                    actorName = 'Holly Sims'
                elif actorID == 572:
                    actorName = 'Jenna Ashley'
                elif actorID == 573:
                    actorName = 'Jenna Ross'
                elif actorID == 591:
                    actorName = 'Katie Jordin'
                elif actorID == 592:
                    actorName = 'Katie Michaels'
                elif actorID == 612:
                    actorName = 'Lexi Bloom'
                elif actorID == 613:
                    actorName = 'Lexi Swallow'
                elif actorID == 622:
                    actorName = 'Lily Carter'
                elif actorID == 621:
                    actorName = 'Lily Love'
                elif actorID == 625:
                    actorName = 'Lola Foxx'
                elif actorID == 648:
                    actorName = 'Melissa Mathews'
                elif actorID == 947:
                    actorName = 'Melissa May'
                elif actorID == 652:
                    actorName = 'Mia Gold'
                elif actorID == 651:
                    actorName = 'Mia Malkova'
                elif actorID == 662:
                    actorName = 'Molly Bennett'
                elif actorID == 661:
                    actorName = 'Molly Madison'
                elif actorID == 668:
                    actorName = 'Naomi West'
                elif actorID == 686:
                    actorName = 'Rachel Bella'
                elif actorID == 684:
                    actorName = 'Rachel Rogers'
                elif actorID == 685:
                    actorName = 'Rachel Roxxx'
                elif actorID == 693:
                    actorName = 'Riley Jensen'
                    movieActors.addActor('Celeste Star', actorPhotoURL)
                elif actorID == 692:
                    actorName = 'Riley Ray'
                elif actorID == 694:
                    actorName = 'Riley Reid'
                elif actorID == 703:
                    actorName = 'Samantha Ryan'
                elif actorID == 718:
                    actorName = 'Sophia Striker'
                elif actorID == 717:
                    actorName = 'Sophia Sutra'
                elif actorID == 728:
                    actorName = 'Taylor Tilden'
                elif actorID == 729:
                    actorName = 'Taylor Whyte'
                elif actorID == 749:
                    actorName = 'Veronica Radke'
                elif actorID == 750:
                    actorName = 'Veronica Rodriguez'
                elif actorID == 757:
                    actorName = 'Whitney Stevens'
            
            elif siteName == 'MassageGirls18':
                if False:
                    pass
                elif actorID == 138:
                    actorName = 'Abby Cross'
                elif actorID == 139:
                    actorName = 'Abby Lane'
                elif actorID == 137:
                    actorName = 'Abby Paradise'
                elif actorID == 147:
                    actorName = 'Alexa Nicole'
                elif actorID == 148:
                    actorName = 'Alexa Rydell'
                elif actorID == 170:
                    actorName = 'Alexis Grace'
                elif actorID == 169:
                    actorName = 'Ashley Abott'
                elif actorID == 178:
                    actorName = 'Ava Sparxxx'
                elif actorID == 179:
                    actorName = 'Ava White'
                elif actorID == 828:
                    actorName = 'Bailey Bae'
                elif actorID == 181:
                    actorName = 'Bailey Bam'
                elif actorID == 196:
                    actorName = 'Callie Calypso'
                elif actorID == 197:
                    actorName = 'Callie Cobra'
                elif actorID == 198:
                    actorName = 'Callie Cyprus'
                elif actorID == 368:
                    actorName = 'Chanel White'
                elif actorID == 215:
                    actorName = 'Chloe Brooke'
                elif actorID == 213:
                    actorName = 'Chloe Skyy'
                elif actorID == 183:
                    actorName = 'Dahlia Sky'
                elif actorID == 242:
                    actorName = 'Gracie Glam'
                elif actorID == 243:
                    actorName = 'Gracie Ivanoe'
                elif actorID == 249:
                    actorName = 'Holly Michaels'
                elif actorID == 248:
                    actorName = 'Holly Sims'
                elif actorID == 262:
                    actorName = 'Jenna Ross'
                elif actorID == 276:
                    actorName = 'Katie Jordin'
                elif actorID == 277:
                    actorName = 'Katie Michaels'
                elif actorID == 278:
                    actorName = 'Katie Summers'
                elif actorID == 301:
                    actorName = 'Lily Carter'
                elif actorID == 302:
                    actorName = 'Lily Love'
                elif actorID == 305:
                    actorName = 'Lola Foxx'
                elif 134 <= actorID <= 135:
                    actorName = 'Melissa Mathews'
                elif actorID == 332:
                    actorName = 'Mia Gold'
                elif actorID == 333:
                    actorName = 'Mia Malkova'
                elif actorID == 341:
                    actorName = 'Molly Bennett'
                elif actorID == 342:
                    actorName = 'Molly Madison'
                elif actorID == 361:
                    actorName = 'Rachel Bella'
                elif actorID == 362:
                    actorName = 'Rachel Roxxx'
                elif actorID == 367:
                    actorName = 'Riley Ray'
                elif actorID == 768:
                    actorName = 'Samantha Rone'
                elif actorID == 394:
                    actorName = 'Sophia Striker'
                elif actorID == 395:
                    actorName = 'Sophia Sutra'
                elif actorID == 404:
                    actorName = 'Taylor Tilden'
                elif actorID == 403:
                    actorName = 'Taylor Whyte'
                elif actorID == 422:
                    actorName = 'Veronica Radke'
                elif actorID == 423:
                    actorName = 'Veronica Rodriguez'
                elif actorID == 211:
                    movieActors.addActor('Riley Jensen', actorPhotoURL)
            
            elif siteName == 'NewGirlPOV':
                if False:
                    pass
                elif actorID == 1159:
                    actorName = 'Ashley Adams'
                elif actorID == 1178:
                    actorName = 'Lola Hunter'
                elif actorID == 1280:
                    actorName = 'Melissa Moore'
                elif actorID == 1206:
                    actorName = 'Molly Manson'
                elif actorID == 1242:
                    actorName = 'Naomi Woods'
            
            movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//a[@class="jqModal"]/img/@src',
        '//div[@id="overallthumb"]/a/img/@src'
    ]
    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if img[0] == '/':
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

    for script in detailsPageElements.xpath('//div[@id="mediabox"]/script/text()'):
        match = re.search(r'image:\s*"(.+)"', script)
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
