import PAsearchSites
import PAgenres
import PAactors
import PAutils


def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + encodedTitle + '.html')
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//div[@class="col-lg-3 col-md-4 col-sm-6 col-xs-6 video-item" and @data-get-thumbs-url]'):
        titleNoFormatting = searchResult.xpath('.//p[@class="title-video"]')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('./a/@href')[0])
        releaseDate = parse(searchResult.xpath('.//div[@class="infos-video"]/p')[0]
                            .text_content().replace('Added on', '').strip()).strftime('%Y-%m-%d')

        if searchDate:
            score = 100 - Util.LevenshteinDistance(searchDate, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchTitle.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), releaseDate), score=score, lang=lang))

    return results


def update(metadata, siteID, movieGenres, movieActors):
    # metadata_id = str(metadata.id).split('|')
    # sceneURL = PAutils.Decode(metadata_id[0])
    # if not sceneURL.startswith('http'):
    #     sceneURL = PAsearchSites.getSearchBaseURL(siteID) + sceneURL
    # req = PAutils.HTTPRequest(sceneURL)
    # detailsPageElements = HTML.ElementFromString(req.text)
    #
    # # Title
    # metadata.title = detailsPageElements.xpath('//h1')[0].text_content().strip()
    #
    # # Summary
    # try:
    #     metadata.summary = detailsPageElements.xpath('///span[@class="full"]')[0].text_content().strip()
    # except:
    #     pass
    #
    # # Studio
    # metadata.studio = 'Marc Dorcel'
    #
    # # Tagline and Collection(s)
    # metadata.collections.clear()
    # tagline = PAsearchSites.getSearchSiteName(siteID)
    # metadata.tagline = tagline
    # metadata.collections.add(tagline)
    #
    # # Genres
    # movieGenres.clearGenres()
    # movieGenres.addGenre('French porn')
    #
    # movieName = detailsPageElements.xpath('//span[@class="movie"]/a')
    # if movieName:
    #     metadata.collections.add(movieName[0].text_content().strip())
    # movieGenres.addGenre('Blockbuster Movie')
    #
    # # Actors
    # movieActors.clearActors()
    # if 'porn-movie' not in sceneURL:
    #     actors = detailsPageElements.xpath('//div[@class="actress"]/a')
    # else:
    #     actors = detailsPageElements.xpath('//div[@class="actor thumbnail "]/a/div[@class="name"]')
    #
    # if actors:
    #     if 'porn-movie' not in sceneURL:
    #         if len(actors) == 3:
    #             movieGenres.addGenre('Threesome')
    #         if len(actors) == 4:
    #             movieGenres.addGenre('Foursome')
    #         if len(actors) > 4:
    #             movieGenres.addGenre('Orgy')
    #
    #     for actorLink in actors:
    #         actorName = actorLink.text_content().strip()
    #         actorPhotoURL = ''
    #
    #         movieActors.addActor(actorName, actorPhotoURL)
    #
    # # Release Date
    # if 'porn-movie' not in sceneURL:
    #     date = detailsPageElements.xpath('//span[@class="publish_date"]')[0].text_content().strip()
    # else:
    #     date = detailsPageElements.xpath('//span[@class="out_date"]')[0].text_content().replace('Year :', '').strip()
    # date_object = parse(date)
    # metadata.originally_available_at = date_object
    # metadata.year = metadata.originally_available_at.year
    #
    # # Director
    # director = metadata.directors.new()
    # movieDirector = detailsPageElements.xpath('//span[@class="director"]')[0].text_content().replace(
    #     'Director :', '').strip()
    # director.name = movieDirector
    #
    # # Poster (only available for movies, scenes are blurred out)
    # art = []
    # if 'porn-movie' in sceneURL:
    #     try:
    #         art.append(detailsPageElements.xpath('//div[@class="header"]//source[@media="(min-width: 768px)"]/@data-srcset')[0].split(',')[-1].strip().split(' ')[0])
    #     except:
    #         pass
    #
    # Log('Artwork found: %d' % len(art))
    # for idx, posterUrl in enumerate(art, 1):
    #     if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
    #         # Download image file for analysis
    #         try:
    #             image = PAutils.HTTPRequest(posterUrl, headers={'Referer': 'http://www.google.com'})
    #             im = StringIO(image.content)
    #             resized_image = Image.open(im)
    #             width, height = resized_image.size
    #             # Add the image proxy items to the collection
    #             if width > 1:
    #                 # Item is a poster
    #                 metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)
    #             if width > 100:
    #                 # Item is an art item
    #                 metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
    #         except:
    #             pass

    return metadata
