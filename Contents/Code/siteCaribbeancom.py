import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    scene_id = searchData.title.replace(' ', '-')
    scene_url = PAsearchSites.getSearchSearchURL(siteNum) + scene_id + '/index.html'
    req = PAutils.HTTPRequest(scene_url)
    result = HTML.ElementFromString(req.text)

    titleNoFormatting = result.xpath('//title')[0].text_content()

    score = 100

    cur_id = PAutils.Encode(scene_url)
    results.Append(MetadataSearchResult(id='%s|%d' % (cur_id, siteNum), name='%s [%s]' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum)), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    scene_url = PAutils.Decode(metadata_id[0])
    req = PAutils.HTTPRequest(scene_url)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//title')[0].text_content()

    # Studio
    metadata.studio = 'caribbeancom'

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Release Date
    str_date = detailsPageElements.xpath('//span[@itemprop="uploadDate"]')[0].text_content()
    date_object = datetime.strptime(str_date, '%Y/%m/%d')
    metadata.originally_available_at = date_object
    metadata.year = metadata.originally_available_at.year

    # Actor(s)
    section = detailsPageElements.xpath('//a[@itemprop="actor"]')
    for actor_section in section:
        for actor_name in actor_section.xpath('//span[@itemprop="name"]')[0].text_content().split(','):
            movieActors.addActor(actor_name, "")

    # Genres
    for genre_link in detailsPageElements.xpath('//a[@itemprop="genre"]'):
        genre_name = genre_link.text_content().strip()

        movieGenres.addGenre(genre_name)

    # Posters/Background
    backgroundUrl = scene_url.replace('/eng', '').replace('index.html', 'images/poster_en.jpg')
    art.append(backgroundUrl)

    for poster in detailsPageElements.xpath('//img[@class="gallery-image"]/@src'):
        if poster.startswith('background-image'):
            poster.split('url(')[1].split(')')[0]
        posterUrl = PAsearchSites.getSearchSearchURL(siteNum) + poster
        art.append(posterUrl)

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
