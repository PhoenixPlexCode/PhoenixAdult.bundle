import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchData.encoded = ' '.join(searchData.title.replace('sons', '').replace('mothers', '').replace('moms', '').split(' ')).lower().replace(' ', '+').replace('\'', '')
    searchURL = PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded
    req = PAutils.HTTPRequest(searchURL)
    searchResults = HTML.ElementFromString(req.text)

    for searchResult in searchResults.xpath('//article'):
        titleNoFormatting = searchResult.xpath('./h2')[0].text_content().strip()
        curID = PAutils.Encode(searchResult.xpath('./h2/a/@href')[0])
        date = searchResult.xpath('./p/span')[0].text_content().strip()

        if date:
            releaseDate = datetime.strptime(date, '%b %d, %Y').strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''
        displayDate = releaseDate if date else ''

        if searchData.date:
            score = 80 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 80 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [%s] %s' % (titleNoFormatting, PAsearchSites.getSearchSiteName(siteNum), displayDate), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])

    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = PAutils.parseTitle(detailsPageElements.xpath('//h1')[0].text_content().strip(), siteNum)

    # Summary
    parts = []
    for part in detailsPageElements.xpath('//div[@class="entry-content"]/p'):
        if 'starring' not in part.text_content().lower():
            parts.append(part.text_content().strip())

    metadata.summary = '\n'.join(parts)

    # Studio
    metadata.studio = PAsearchSites.getSearchSiteName(siteNum)

    # Tagline and Collection(s)
    metadata.collections.add(metadata.studio)

    # Release Date
    date = detailsPageElements.xpath('//span[@class="published"]')[0].text_content().strip()
    if date:
        date_object = datetime.strptime(date, '%b %d, %Y')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    actors = []
    for genreLink in detailsPageElements.xpath('//a[contains(@rel, "tag")]'):
        genreName = PAutils.parseTitle(genreLink.text_content().strip(), siteNum)

        for actorName in actorsDB:
            if genreName.lower() == actorName:
                actors.append(actorName)
                break
        else:
            movieGenres.addGenre(genreName)

    # Actor(s)
    try:
        actorSubtitle = detailsPageElements.xpath('//div[@class="entry-content"]/p')[-1]
        if 'starring' in actorSubtitle.text_content().lower():
            actors.extend(actorSubtitle.text_content().split('Starring')[-1].split('*')[0].split('&'))
    except:
        pass

    for actorLink in actors:
        actorName = actorLink.strip()
        actorPhotoURL = ''

        movieActors.addActor(actorName, actorPhotoURL)

    return metadata


actorsDB = {
    'alex adams', 'brianna beach', 'sophia locke', 'crystal rush', 'tucker stevens', 'coralia baby', 'juliett russo',
    'demi diveena', 'mandy waters', 'mandy rhea', 'april love', 'kate dee', 'emma magnolia', 'naomi foxxx', 'rachael cavalli',
    'cory chase', 'abby somers', 'bailey base', 'kiki klout', 'victoria june', 'kendra heart', 'archie stone', 'jaime vine',
    'casca akashova', 'katie monroe', 'eve rebel', 'dakota burns', 'nikita reznikova', 'taylor blake', 'tricia oaks', 'artemisia love',
    'kyla keys', 'brianna rose', 'jordan max', 'jadan snow', 'kaylynn keys', 'lucy sunflower', 'jackie hoff', 'kenzie foxx',
    'mirabella amore', 'heather vahn', 'natasha nice', 'kat marie', 'miss brat', 'macy meadows', 'sydney paige', 'vanessa cage',
}
