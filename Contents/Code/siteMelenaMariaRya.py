import PAsearchSites
import PAgenres
import PAactors
import PAutils
import re

def search(results, encodedTitle, searchTitle, siteNum, lang, searchDate):
    sceneID = searchTitle.split(' ', 1)[0]
    try:
        sceneTitle = searchTitle.split(' ', 1)[1]
    except:
        sceneTitle = ''

    sceneURL = PAsearchSites.getSearchSearchURL(siteNum) + sceneID
    Log(sceneURL)
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    titleNoFormatting = detailsPageElements.xpath('//title')[0].text_content().split(' - Sex Movies Featuring Melena Maria Rya')[0]
    titleNoFormatting = re.sub(r'[^A-Za-z0-9\s\-]+', ' ', titleNoFormatting).strip()

    curID = PAutils.Encode(sceneURL)
    releaseDate = '1900-01-01'

    if sceneTitle:
        score = 100 - Util.LevenshteinDistance(sceneTitle.lower(), titleNoFormatting.lower())
    else:
        score = 90

    results.Append(MetadataSearchResult(id='%s|%d' % (curID, siteNum), name='%s [MelenaMariaRya]' % (titleNoFormatting), score=score, lang=lang))

    return results


def update(metadata, siteNum, movieGenres, movieActors):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    if not sceneURL.startswith('http'):
        sceneURL = PAsearchSites.getSearchBaseURL(siteNum) + sceneURL
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    metadata.title = detailsPageElements.xpath('//title')[0].text_content().split(' - Sex Movies Featuring Melena Maria Rya')[0]
    metadata.title = re.sub('[^A-Za-z0-9\s\-]', ' ', metadata.title).strip()
    oTitle = metadata.title
    metadata.title = re.sub(r' with ([A-Z][a-z]+) ([A-Z][a-z]+)', '', metadata.title)

    # Summary
    metadata.summary = detailsPageElements.xpath('//meta[@name="description"]/@content')[0].strip()

    # Studio
    metadata.studio = 'MelenaMariaRya'

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = PAsearchSites.getSearchSiteName(siteNum).strip()
    metadata.tagline = tagline
    metadata.collections.add(tagline)

    # Genres
    movieGenres.clearGenres()
    movieGenres.addGenre('European Girls')

    # Actors
    movieActors.clearActors()
    movieActors.addActor('Melena Maria Rya', '')

    m = re.search(r' with ([A-Z][a-z]+ [A-Z][a-z]+)', oTitle)
    if m:
        movieActors.addActor(m.group(1), '')

    return metadata

