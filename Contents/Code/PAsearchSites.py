import PAsiteList
import PAutils


def getSearchSiteName(siteNum):
    return PAsiteList.searchSites[siteNum][0]


def getSearchBaseURL(siteNum):
    return PAsiteList.searchSites[siteNum][1]


def getSearchSearchURL(siteNum):
    url = PAsiteList.searchSites[siteNum][2]
    if not url.startswith('http'):
        url = getSearchBaseURL(siteNum) + url

    return url


def getSearchsiteNumByFilter(searchFilter):
    searchResults = []
    searchFilterF = searchFilter.lower().replace(' ', '').replace('.com', '').replace('.net', '').replace('\'', '').replace('-', '')
    for searchID, site in PAsiteList.searchSites.items():
        if site:
            siteNameF = site[0].lower().replace(' ', '').replace('\'', '').replace('-', '')

            if searchFilterF.startswith(siteNameF):
                searchResults.append((searchID, siteNameF))

    if searchResults:
        from operator import itemgetter

        Log('Site found')
        return max(searchResults, key=itemgetter(1))[0]

    return None


def getSearchSettings(mediaTitle):
    Log('mediaTitle w/ possible abbreviation: %s' % mediaTitle)

    for abbreviation, full in PAsiteList.abbreviations:
        r = re.compile(abbreviation, flags=re.IGNORECASE)
        if r.match(mediaTitle):
            mediaTitle = r.sub(full, mediaTitle, 1)
            break

    Log('mediaTitle w/ possible abbrieviation fixed: %s' % mediaTitle)

    # Search Site ID
    siteNum = None
    # What to search for
    searchTitle = None
    # Date search
    searchDate = None

    # Remove Site from Title
    siteNum = getSearchsiteNumByFilter(mediaTitle)
    if siteNum is not None:
        Log('^^^^^^^ siteNum: %d' % siteNum)
        Log('^^^^^^^ Shortening Title')

        title = mediaTitle.replace('.com', '').title()
        site = PAsiteList.searchSites[siteNum][0].lower()

        title = re.sub(r'[^a-zA-Z0-9 ]', '', title)
        site = re.sub(r'\W', '', site)

        matched = False
        while(' ' in title):
            title = title.replace(' ', '', 1)
            if title.lower().startswith(site):
                matched = True
                break

        if matched:
            searchTitle = re.sub(site, '', title, 1, flags=re.IGNORECASE)
            searchTitle = ' '.join(searchTitle.split())
        else:
            searchTitle = mediaTitle

        searchTitle = searchTitle.replace(' S ', '\'s ').replace(' In ', ' in ').replace(' A ', ' a ')

        Log('searchTitle (before date processing): %s' % searchTitle)

        # Search Type
        searchDate = None
        regex = [
            (r'\b\d{4} \d{2} \d{2}\b', '%Y %m %d'),
            (r'\b\d{2} \d{2} \d{2}\b', '%y %m %d')
        ]
        date_obj = None
        for r, dateFormat in regex:
            date = re.search(r, searchTitle)
            if date:
                try:
                    date_obj = datetime.strptime(date.group(), dateFormat)
                except:
                    pass

                if date_obj:
                    searchDate = date_obj.strftime('%Y-%m-%d')
                    searchTitle = ' '.join(re.sub(r, '', searchTitle, 1).split())
                    break

    return (siteNum, searchTitle, searchDate)


def posterAlreadyExists(posterUrl, metadata):
    posterUrl = PAutils.getClearURL(posterUrl)
    for p in metadata.posters.keys():
        if p.lower() == posterUrl.lower():
            Log('Found %s in posters collection' % posterUrl)
            return True
        else:
            pass

    for p in metadata.art.keys():
        if p.lower() == posterUrl.lower():
            return True

    return False
