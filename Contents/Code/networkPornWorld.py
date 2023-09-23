import PAsearchSites
import PAutils
from datetime import datetime
from datetime import date
import math


def search(results, lang, siteNum, searchData):

    # if we have a scene date, we can use the 'Newest scenes' pages to get a match
    if searchData.date:

        # there are 99 scenes per page starting with today on page 1,
        # so let's try to determine the page on which we will find a match
        # though this can be a bit random with older scenes

        searchDateObj = dateFromIso(searchData.date)
        delta = date.today() - searchDateObj
        searchPage = max(math.ceil(float(delta.days) / 99), 1)

        # the first word in the title is usually a name
        searchName = searchData.title.lower().split()[0]

        # Log('Scene date: %s, Days delta: %d, Page: %d' % (searchData.date, delta.days, searchPage))

        searchUrl = 'https://www.pornworld.com/new-videos/%d'
        dateNotFound = True

        while dateNotFound:
            req = PAutils.HTTPRequest(searchUrl % searchPage)

            if req.status_code != 200:
                Log('Page %d bad request' % searchPage)
                break

            searchResults = HTML.ElementFromString(req.text)

            dateResults = searchResults.xpath("//div[@class='card-scene__time']/div[@class='label label--time'][2]")

            firstDateObj = dateFromIso(dateResults[0].text_content().strip())
            if searchDateObj > firstDateObj and searchPage > 1:
                searchPage = searchPage - 1
                continue

            lastDateObj = dateFromIso(dateResults[-1].text_content().strip())
            if searchDateObj < lastDateObj:
                searchPage = searchPage + 1
                continue

            dateNotFound = False
            for searchResult in searchResults.xpath("//div[contains(concat(' ',normalize-space(@class),' '),' card-scene ')]"):

                titleNoFormatting = PAutils.parseTitle(searchResult.xpath(".//div[@class='card-scene__text']/a")[0].text_content().strip(), siteNum)
                sceneDate = searchResult.xpath('.//div[@class="label label--time"]')[1].text_content().strip()
                sceneDateObj = dateFromIso(sceneDate)

                # get the difference in days between the search target and the current scene
                daysDiff = abs((searchDateObj - sceneDateObj).days)

                # let's allow scenes +/- two days of the target date as sometimes scenes get re-dated on the site
                if daysDiff < 3:

                    url = searchResult.xpath('.//a/@href')[0]
                    curID = PAutils.Encode(url)

                    # take off some points if the date is not a precise match
                    score = 100 - daysDiff * 10

                    # try to match the first word/name in the title
                    if searchName not in titleNoFormatting.lower():
                        # take off some points if we don't match the title search params
                        score = score - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

                    # Log('Scene: %s %s (%s%%)' % (sceneDate, titleNoFormatting, score))

                    results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), sceneDate), score=score, lang=lang))

        # if we have a date, there's a far better chance of a decent match than the title search, so get out now
        return results

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
        titleNoFormatting = getTitle(detailsPageElements, siteNum)

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name=titleNoFormatting, score=100, lang=lang))

    # if we get to here, results can be extremely sketchy...
    else:
        searchData.encoded = searchData.title.replace(' ', '+')
        req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
        searchResults = HTML.ElementFromString(req.text)

        if not searchResults.xpath('//h1[contains(@class, "section__title")]'):
            # if there is only one result returned by the search function it automatically redirects to the video page
            titleNoFormatting = getTitle(searchResults, siteNum)

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


def dateFromIso(dateString):
    return datetime.strptime(dateString, '%Y-%m-%d').date()


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if 'http' not in sceneURL:
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = getTitle(detailsPageElements, siteNum)

    # Summary
    description = detailsPageElements.xpath('//div[text()="Description:"]/following-sibling::div')
    if description:
        metadata.summary = description[0].text_content().strip()

    # Studio
    metadata.studio = 'PornWorld'

    # Tagline and Collection(s)
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
    for genreLink in detailsPageElements.xpath('//div[contains(@class, "genres-list")]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actor(s)
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


def getTitle(htmlElements, siteNum):
    titleNoFormatting = PAutils.parseTitle(htmlElements.xpath('//title')[0].text_content().strip(), siteNum)

    return re.sub(r' - PornWorld$', '', titleNoFormatting)
