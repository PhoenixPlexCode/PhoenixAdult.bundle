import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = searchData.title.replace(' ', '+')
    req = PAutils.HTTPRequest('%svideo&q=%s' % (PAsearchSites.getSearchSearchURL(siteNum), searchData.encoded))
    searchPageElements = HTML.ElementFromString(req.text)

    for searchResult in searchPageElements.xpath('//ul[@id="studio-videos-container"]/li'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//span[contains(@class, "title")]')[0].text_content().strip(), siteNum)
        galleryID = searchResult.xpath('.//a/@href')[0].split('=')[-1]
        sceneURL = '%s/studios/video/%s' % (PAsearchSites.getSearchBaseURL(siteNum), galleryID)
        curID = PAutils.Encode(sceneURL)

        date = searchResult.xpath('.//span[contains(@class, "releasedate")]')
        if date:
            releaseDate = datetime.strptime(date[0].text_content().strip(), '%b %d, %Y').strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if searchData.date and displayDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='%s [Adult Prime/%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h2')[0].text_content().strip(), siteNum)

    # Summary
    summary = detailsPageElements.xpath('//p[contains(@class, "description")]')[0].text_content().strip()
    if not summary.lower().startswith(tuple(map(str.lower, skipGeneric))):
        metadata.summary = summary

    # Studio
    metadata.studio = 'Adult Prime'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = detailsPageElements.xpath('//p[@class="update-info-line regular"][./b[contains(., "Studio")]]//a')[0].text_content().strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//p[@class="update-info-line regular"]/b[1][./preceding-sibling::i[contains(@class, "calendar")]]')
    if date:
        date_object = datetime.strptime(date[0].text_content().strip(), '%d.%m.%Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//p[@class="update-info-line regular"][./b[contains(., "Niches")]]')[0].text_content().split(':')[-1].split(','):
        genreName = PAutils.parseTitle(genreLink.strip(), siteNum)

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    actors = detailsPageElements.xpath('//p[@class="update-info-line regular"][./b[contains(., "Performer")]]/a')
    for actorLink in actors:
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''

        modelPageURL = '%sperformer&q=%s' % (PAsearchSites.getSearchSearchURL(siteNum), actorName.replace(' ', '+'))
        req = PAutils.HTTPRequest(modelPageURL)
        modelPageElements = HTML.ElementFromString(req.text)

        try:
            actorPhoto = modelPageElements.xpath('//div[@class="performer-container"]//div[@class="ratio-square"]/@style')[0]
            actorPhotoURL = actorPhoto.split('(')[-1].replace(')', '')
        except:
            pass

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    xpaths = [
        '//div[@class="video-wrapper update-video-wrapper"]//div/@style'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            if not img.startswith('http'):
                img = img.split('(')[-1].replace(')', '')

            art.append(img)

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
                if height > 1:
                    # Item is a poster
                    metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
                if width > 100:
                    # Item is an art item
                    metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


skipGeneric = {
    'One-stop shop for all your dirty needs',
    'CFNM stands for clothed-female-nude-male',
    'Coming straight from Germany, on BBVideo',
    'BeautyAndTheSenior is all about giving some',
    'Perfect18 brings you fresh new girls',
    'If you are somebody who truly appreciates the beauty of the bondage',
    'Submissed has a rather straightforward name',
    'Latina girls are known to be some of the most beautiful',
    'It\'s the BreedBus, come on hop and join us',
    'ClubBangBoys is one of the hottest gay porn',
    'With such a straightforward name, one can already guess what ClubCastings',
    'Welcome to our dirty filthy porn hospital at DirtyHospital.com',
    'Distorded.com brings you a big fetish variety',
    'Coming to you exclusively from Nathan Blake Production, ElegantRaw',
    'Evil Playgrounds is a great brand if you like tight young Eastern European',
    'FamilyScrew is all about keeping it in the family',
    'We all have different preferences when it comes to porn, which is why FetishPrime',
    'Fixxxion is an adventurous fantasy',
    'Welcome to FreshPOV.com videos',
    'FuckingSkinny gives you exactly that',
    'Gonzo2000.com is bringing you a selection',
    'The older the babes, the more experience they have',
    'If you want to watch experienced older couples',
    'GroupBanged is filled with the most cum-thirsty',
    'GroupMams.com is bringing you exactly what it says',
    'When a group of horny people gets together',
    'When you remember that Amsterdam is the sex capital of the world',
    'From couples having some passionate fun to hardcore threesomes',
    'Jim Slip follows the life of the luckiest man on Earth',
    'All the videos featured on YoungBusty',
}
