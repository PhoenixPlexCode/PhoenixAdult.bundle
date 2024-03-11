import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    url = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded + '/page1.html'
    req = PAutils.HTTPRequest(url)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//li[@class="col-sm-6 col-lg-4"]'):
        imgURL = searchResult.xpath('.//div[@class="vidthumb"]/a[@class="diagrad"]/img/@src')[0]
        imgURL = PAutils.Encode(imgURL)

        titleNoFormatting = searchResult.xpath('.//div[@class="vidtitle"]/p[1]')[0].text_content().strip()
        curID = int(searchResult.xpath('.//a[@href="#"]/@data-movie')[0])

        description = searchResult.xpath('.//div[@class="collapse"]/p')[0].text_content().split(':')[1].strip()
        description = PAutils.Encode(description)

        date = None
        try:
            date = searchResult.xpath('.//div[@class="vidtitle"]/p[2]')[0].text_content().strip()
        except:
            pass

        if date:
            releaseDate = parse(date).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        displayDate = releaseDate if date else ''

        if searchData.date and displayDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%d|%d|%s|%s' % (curID, siteNum, description, imgURL), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneID = metadata_id[0]
    imgURL = PAutils.Decode(metadata_id[3])
    if not imgURL.startswith('http'):
        imgURL = PAsearchSites.getSearchBaseURL(siteNum) + imgURL

    pageURL = PAsearchSites.getSearchBaseURL(siteNum) + 'v6/v6.pop.php?id=' + sceneID
    req = PAutils.HTTPRequest(pageURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Studio
    metadata.studio = 'Sicflics'

    # Title
    metadata.title = detailsPageElements.xpath('//h4[@class="red"]')[0].text_content().strip().title()

    # Summary
    description = PAutils.Decode(metadata_id[2])
    if description:
        metadata.summary = description.replace('\n', '').strip()

    # Tagline and Collection(s)
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    for genreLink in detailsPageElements.xpath('//div[@class="vidwrap"]/p/a'):
        genreName = genreLink.text_content().replace('#', '').strip()

        movieGenres.addGenre(genreName)

    # Release Date
    date = detailsPageElements.xpath('//span[@title="Date Added"]')[0].text_content().split(':')[1].strip()
    if date:
        date_object = parse(date)
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Actor(s)
    description = description.encode('ascii', 'replace')
    actorName = re.split(r'[\'?]', description)[1].strip()
    actorPhotoURL = ''
    if actorName:
        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    if imgURL:
        art.append(imgURL)

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
