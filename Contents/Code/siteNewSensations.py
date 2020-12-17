import PAsearchSites
import PAgenres
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):
    encodedTitle = searchTitle.replace(' ', '-')
    searchResultsURLs = [
        PAsearchSites.getSearchSearchURL(siteNum) + 'updates/' + encodedTitle + '.html',
        PAsearchSites.getSearchSearchURL(siteNum) + 'updates/' + encodedTitle + '-.html',
        PAsearchSites.getSearchSearchURL(siteNum) + 'dvds/' + encodedTitle + '.html'
    ]

    googleResults = PAutils.getFromGoogleSearch(searchTitle, siteNum)
    for sceneURL in googleResults:
        if sceneURL not in searchResultsURLs:
            if (('/updates/' in sceneURL or '/dvds/' in sceneURL or '/scenes/' in sceneURL) and '/tour_ns/' in sceneURL) and sceneURL not in searchResultsURLs:
                searchResultsURLs.append(sceneURL)

    for sceneURL in searchResultsURLs:
        req = PAutils.HTTPRequest(sceneURL)
        if req.ok:
            try:
                searchResult = HTML.ElementFromString(req.text)

                titleNoFormatting = searchResult.xpath('(//div[@class="indScene"] | //div[@class="indSceneDVD"])/h2')[0].text_content().strip()
                curID = PAutils.Encode(sceneURL)

                score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

                results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [New Sensations]' % titleNoFormatting, score=score, lang=lang))
            except:
                pass

    return results


def update(metadata, siteID, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteID) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    if 'dvds' in sceneURL:
        sceneType = 'DVD'
    else:
        sceneType = 'Scene'

    art = []
    metadata.collections.clear()
    movieGenres.clearGenres()
    movieActors.clearActors()

    # Studio
    metadata.studio = 'New Sensations'

    if sceneType == 'Scene':
        # Title
        metadata.title = detailsPageElements.xpath('//div[@class="indScene"]/h2')[0].text_content().strip()

        # Summary
        metadata.summary = detailsPageElements.xpath('//div[@class="description"]/p')[0].text_content().replace('Description:', '').strip()

        # Tagline and Collection(s)
        metadata.collections.add(PAsearchSites.getSearchSiteName(siteID))

        # No genres for scenes

        # Release Date
        date = detailsPageElements.xpath('//div[@class="sceneDateP"]')[0].text_content().split(',')[0].strip()
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

        # Actors
        actors = detailsPageElements.xpath('//div[@class="sceneTextLink"]/span[@class="tour_update_models"]/a')
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

                try:
                    actorPageURL = actorLink.get('href')
                    req = PAutils.HTTPRequest(actorPageURL)
                    actorPage = HTML.ElementFromString(req.text)
                    actorPhotoURL = actorPage.xpath('//div[@class="modelBioPic"]/img/@src0_3x')[0]
                except:
                    pass

                movieActors.addActor(actorName, actorPhotoURL)

        # Posters
        try:
            art.append(detailsPageElements.xpath('//span[@id="trailer_thumb"]//img[@class="loading"]/@src')[0])
        except:
            pass

    else:
        # Title
        metadata.title = detailsPageElements.xpath('//div[@class="dvdSections clear"]/div[1]')[0].text_content().replace('DVDS /', '').strip()

        # Summary
        metadata.summary = detailsPageElements.xpath('//div[@class="dDetails"]/p')[0].text_content().strip()

        # Tagline and Collection(s)
        dvdName = title
        metadata.tagline = dvdName
        metadata.collections.add(dvdName)
        metadata.collections.add(PAsearchSites.getSearchSiteName(siteID))

        # Genres
        genres = detailsPageElements.xpath('//div[@class="dvdDetails clear"]/ul/li[2]/a')
        for genreLink in genres:
            genreName = genreLink.text_content().strip()

            movieGenres.addGenre(genreName)

        # Release Date
        date = detailsPageElements.xpath('//div[@class="dvdDetails clear"]/ul/li[1]')[0].text_content().replace('Released:', '').strip()
        if date:
            try:
                date_object = datetime.strptime(date, '%Y-%m-%d')
            except:
                date_object = datetime.strptime(date, '%m/%d/%y')
            metadata.originally_available_at = date_object
            metadata.year = metadata.originally_available_at.year

        # Actors
        try:
            actors = detailsPageElements.xpath('//span[@class="tour_update_models"]/a')
            for actorLink in detailsPageElements.xpath('//span[@class="tour_update_models"]/a'):
                actorName = str(actorLink.text_content().strip())
                actorPhotoURL = ''

                try:
                    actorPageURL = actorLink.get('href')
                    req = PAutils.HTTPRequest(actorPageURL)
                    actorPage = HTML.ElementFromString(req.text)
                    actorPhotoURL = actorPage.xpath('//div[@class="modelPicture"]/div/img/@src0_3x')[0]
                except:
                    pass

                movieActors.addActor(actorName, actorPhotoURL)
        except:
            actorsList = detailsPageElements.xpath('//div[@class="dvdDetails clear"]/div[2]/p')[0].text_content().replace('Featuring:', ' ')[1]
            for actorLink in actorsList.split('', ''):
                actorName = actorLink.strip()
                actorPhotoURL = ''

                movieActors.addActor(actorName, actorPhotoURL)

        # Posters
        dvdPosterURL = dvdPageElements.xpath('//div[@class="dvdcover"]//img/@src')
        if not dvdPosterURL:
            dvdPosterURL = dvdPageElements.xpath('//div[@class="dvdcover"]//img/@data-src')

        if dvdPosterURL:
            art.append(dvdPosterURL[0])

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.google.com'})
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
