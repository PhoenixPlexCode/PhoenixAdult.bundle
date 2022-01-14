import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    sceneID = searchData.title.split(' ', 1)[0]
    if unicode(sceneID, 'UTF-8').isdigit() and len(sceneID) > 3:  # don't match things like '2 girls do something...'
        searchData.title = searchData.title.replace(sceneID, '', 1).strip()
    else:
        sceneID = None

    if sceneID:
        url = PAsearchSites.getSearchBaseURL(siteNum) + '/watch/' + sceneID
        req = PAutils.HTTPRequest(url)
        detailsPageElements = HTML.ElementFromString(req.text)

        curID = PAutils.Encode(url)
        titleNoFormatting = getTitle(detailsPageElements)

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name=titleNoFormatting, score=100, lang=lang))
    else:
        searchData.encoded = searchData.title.replace(' ', '+')
        req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
        searchResults = HTML.ElementFromString(req.text)

        if not searchResults.xpath('//h1[contains(@class, "section__title")]'):
            # if there is only one result returned by the search function it automatically redirects to the video page
            titleNoFormatting = getTitle(searchResults)

            url = searchResults.xpath('//a[contains(@class, "__pagination_button--more")]/@href')[0]
            curID = PAutils.Encode(url)

            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))
            return results

        for searchResult in searchResults.xpath('//div[@class="card-scene__text"]'):
            titleNoFormatting = searchResult.xpath('./a')[0].text_content().strip()

            url = searchResult.xpath('./a/@href')[0]
            curID = PAutils.Encode(url)

            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

            results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if 'http' not in sceneURL:
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = getTitle(detailsPageElements)

    # Summary
    description = detailsPageElements.xpath('//div[text()="Description:"]/following-sibling::div')
    if description:
        metadata.summary = description[0].text_content().strip()

    # Studio
    metadata.studio = 'PornWorld'

    # Tagline / Collection
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum)
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Release Date
    date = detailsPageElements.xpath('//i[contains(@class, "bi-calendar")]')
    if date:
        date_object = parse(date[0].text_content().strip())
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//div[contains(@class, "genres-list")]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actorLink in detailsPageElements.xpath('//h1[contains(@class, "watch__title")]//a'):
        actorName = actorLink.text_content().strip()
        actorPhotoURL = ''
        # actorPhotoURL = 'http:' + actorLink.get('data-src')

        movieActors.addActor(actorName, actorPhotoURL)

    # Posters
    art.append(detailsPageElements.xpath('//video/@data-poster')[0])

    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
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


def getTitle(htmlElements):
    titleNoFormatting = htmlElements.xpath('//title')[0].text_content().strip()

    return re.sub(r' - PornWorld$', '', titleNoFormatting)
