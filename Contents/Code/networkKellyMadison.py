import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = None
    parts = searchData.title.split()
    if unicode(re.sub(r'^e(?=\d+$)', '', parts[0], flags=re.IGNORECASE), 'UTF-8').isdigit():
        sceneID = re.sub(r'^e(?=\d+$)', '', parts[0], flags=re.IGNORECASE)
        searchData.title = searchData.title.replace(parts[0], '', 1).strip()

    searchData.encoded = urllib.quote(searchData.title)
    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded, cookies={'nats': 'MC4wLjMuNTguMC4wLjAuMC4w'})
    searchResults = HTML.ElementFromString(req.json()['html'])
    for searchResult in searchResults.xpath('//div[@class="card episode"]'):
        titleNoFormatting = searchResult.xpath('.//a[@class="text-km"] | .//a[@class="text-pf"] | .//a[@class="text-tf"]')[0].text_content().strip()

        sceneURL = searchResult.xpath('.//a[@class="text-km"] | .//a[@class="text-pf"] | .//a[@class="text-tf"]')[0].get('href')
        episodeID = searchResult.xpath('.//span[@class="card-footer-item"]')[-1].text_content().split('#')[-1].strip()
        searchID = sceneURL.split('/')[-1]
        curID = PAutils.Encode(sceneURL)

        title = PAutils.Encode(titleNoFormatting)
        result = PAutils.Encode(HTML.StringFromElement(searchResult))

        date = searchResult.xpath('.//span[.//i[@class="far fa-calendar-alt"]]')
        try:
            releaseDate = datetime.strptime(date[0].text_content().strip(), '%b %d, %Y').strftime('%Y-%m-%d')
        except:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if sceneID and int(sceneID) == int(episodeID):
            score = 100
        elif sceneID and int(sceneID) == int(searchID):
            score = 100
        elif searchData.date:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s|%s|%s' % (curID, siteNum, releaseDate, title, result), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    sceneDate = metadata_id[2]
    if len(metadata_id) > 3:
        title = PAutils.Decode(metadata_id[3])
        searchResult = HTML.ElementFromString(PAutils.Decode(metadata_id[4]))
    req = PAutils.HTTPRequest(sceneURL, cookies={'nats': 'MC4wLjMuNTguMC4wLjAuMC4w'})
    detailsPageElements = HTML.ElementFromString(req.text)

    try:
        # Title
        metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//div[@class="level-left"]')[0].text_content().strip(), siteNum)

        # Summary
        metadata.summary = detailsPageElements.xpath('//div[@class="column is-three-fifths"]')[0].text_content().replace('Episode Summary', '').strip()

        # Studio
        metadata.studio = 'Kelly Madison Productions'

        # Actors
        actors = detailsPageElements.xpath('//a[@class="is-underlined"]')
    except:
        # Title
        metadata.title = PAutils.parseTitle(title, siteNum)

        # Studio
        metadata.studio = 'Kelly Madison Productions'

        # Actors
        actors = searchResult.xpath('.//a[contains(@href, "/models/")]')

    # Tagline and Collection(s)
    if 'teenfidelity' in metadata.title.lower():
        tagline = 'TeenFidelity'
    elif 'kelly madison' in metadata.title.lower():
        tagline = 'Kelly Madison'
    else:
        tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//li[.//i[@class="fas fa-calendar"]]')
    if date:
        date_object = datetime.strptime(date[0].text_content().split(':')[-1].strip(), '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year
    elif sceneDate:
        date_object = parse(sceneDate)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.addGenre('Hardcore')
    movieGenres.addGenre('Heterosexual')

    # Actor(s)
    if actors:
        if len(actors) == 3:
            movieGenres.addGenre('Threesome')
        if len(actors) == 4:
            movieGenres.addGenre('Foursome')
        if len(actors) > 4:
            movieGenres.addGenre('Orgy')

        for actorLink in actors:
            actorName = actorLink.text_content()

            actorPageURL = actorLink.get('href')
            req = PAutils.HTTPRequest(actorPageURL, cookies={'nats': 'MC4wLjMuNTguMC4wLjAuMC4w'})
            actorPage = HTML.ElementFromString(req.text)
            actorPhotoURL = actorPage.xpath('//div[contains(@class, "one")]//@src')[0]

            movieActors.addActor(actorName, actorPhotoURL)

    # Posters/Background
    art.append('https://tour-cdn.kellymadisonmedia.com/content/episode/poster_image/%s/poster.jpg' % sceneURL.rsplit('/')[-1])
    art.append('https://tour-cdn.kellymadisonmedia.com/content/episode/episode_thumb_image_1/%s/1.jpg' % sceneURL.rsplit('/')[-1])

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
