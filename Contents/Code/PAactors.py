import PAutils
import PAdatabaseActors


class PhoenixActors:
    actorsTable = None
    photosTable = None
    actorsNum = 0

    def __init__(self):
        self.actorsTable = [None] * 100
        self.photosTable = [None] * 100
        self.actorsNum = 0

    def addActor(self, newActor, newPhoto):
        self.actorsTable[self.actorsNum] = newActor
        self.photosTable[self.actorsNum] = newPhoto
        self.actorsNum = self.actorsNum + 1

    def clearActors(self):
        self.actorsNum = 0

    def processActors(self, metadata):
        actorsProcessed = 0
        while actorsProcessed < self.actorsNum:
            skip = False
            # Save the potentional new Actor or Actress to a new variable, replace &nbsp; with a true space, and strip off any surrounding whitespace
            newActor = self.actorsTable[actorsProcessed].replace('\xc2\xa0', ' ').replace(',', '').strip().title()
            newPhoto = str(self.photosTable[actorsProcessed]).strip()

            newActor = ' '.join(newActor.split())

            # Skip an actor completely; this could be used to filter out male actors if desired
            if newActor == 'Bad Name':
                skip = True
            elif newActor == 'Test Model Name':
                skip = True

            if not skip:
                searchStudioIndex = None
                for studioIndex, studioList in PAdatabaseActors.ActorsStudioIndexes.items():
                    if metadata.studio in studioList:
                        searchStudioIndex = studioIndex
                        break

                if searchStudioIndex is not None and searchStudioIndex in PAdatabaseActors.ActorsReplaceStudios:
                    for actorName, aliases in PAdatabaseActors.ActorsReplaceStudios[searchStudioIndex].items():
                        if newActor.lower() == actorName.lower() or newActor in aliases:
                            newActor = actorName

                            if searchStudioIndex == 32 and newActor != 'QueenSnake':
                                newActor = '%s QueenSnake' % newActor

                            break

                for actorName, aliases in PAdatabaseActors.ActorsReplace.items():
                    if newActor.lower() == actorName.lower() or newActor in aliases:
                        newActor = actorName
                        break

                if ',' in newActor:
                    for actorName in newActor.split(','):
                        newActorName = actorName.strip()
                        newPhoto = actorDBfinder(newActorName)

                        Log('Actor: %s %s' % (newActor, newPhoto))

                        role = metadata.roles.new()
                        role.name = newActor
                        role.photo = newPhoto
                else:
                    req = None
                    img = False
                    if newPhoto:
                        req = PAutils.HTTPRequest(newPhoto, 'HEAD', bypass=False)
                        if req.ok:
                            try:
                                image = PAutils.HTTPRequest(newPhoto, bypass=False)
                                im = StringIO(image.content)
                                resized_image = Image.open(im)
                                width, height = resized_image.size

                                if width > 1:
                                    img = True
                            except:
                                pass

                    if not req or not req.ok or not img:
                        newPhoto = actorDBfinder(newActor)

                    if newPhoto:
                        newPhoto = PAutils.getClearURL(newPhoto)

                    Log('Actor: %s %s' % (newActor, newPhoto))

                    role = metadata.roles.new()
                    role.name = newActor
                    role.photo = newPhoto

                actorsProcessed = actorsProcessed + 1


def actorDBfinder(actorName):
    actorEncoded = urllib.quote(actorName)

    actorPhotoURL = ''
    databaseName = ''

    searchResults = {
        'IAFD': getFromIAFD,
        'Indexxx': getFromIndexxx,
        'AdultDVDEmpire': getFromAdultDVDEmpire,
        'Boobpedia': getFromBoobpedia,
        'Babes and Stars': getFromBabesandStars,
        'Babepedia': getFromBabepedia,
    }

    searchOrder = ['IAFD', 'Indexxx', 'AdultDVDEmpire', 'Boobpedia', 'Babes and Stars', 'Babepedia']

    for sourceName in searchOrder:
        task = searchResults[sourceName]
        url = task(actorName, actorEncoded)
        if url:
            databaseName = sourceName
            actorPhotoURL = url
            break

    if actorPhotoURL:
        Log('%s found in %s ' % (actorName, databaseName))
        Log('PhotoURL: %s' % actorPhotoURL)
    else:
        Log('%s not found' % actorName)

    return actorPhotoURL


def getFromIndexxx(actorName, actorEncoded):
    actorPhotoURL = ''

    req = PAutils.HTTPRequest('https://www.indexxx.com/search/?query=' + actorEncoded)
    actorSearch = HTML.ElementFromString(req.text)
    actorPageURL = actorSearch.xpath('//div[contains(@class, "modelPanel")]//a[@class="modelLink3"]/@href')
    if actorPageURL:
        actorPageURL = actorPageURL[0]
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        img = actorPage.xpath('//img[@class="model-img"]/@src')
        if img:
            actorPhotoURL = img[0]
            actorPhotoURL = cacheActorPhoto(actorPhotoURL, actorName, headers={'Referer': actorPageURL})

    return actorPhotoURL


def getFromAdultDVDEmpire(actorName, actorEncoded):
    actorPhotoURL = ''

    req = PAutils.HTTPRequest('https://www.adultdvdempire.com/performer/search?q=' + actorEncoded)
    actorSearch = HTML.ElementFromString(req.text)
    actorPageURL = actorSearch.xpath('//div[@id="performerlist"]/div//a/@href')
    if actorPageURL:
        actorPageURL = 'https://www.adultdvdempire.com' + actorPageURL[0]
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        img = actorPage.xpath('//div[contains(@class, "performer-image-container")]/a/@href')
        if img:
            actorPhotoURL = img[0]

    return actorPhotoURL


def getFromBoobpedia(actorName, actorEncoded):
    actorPhotoURL = ''

    actorPageURL = 'http://www.boobpedia.com/boobs/' + actorName.title().replace(' ', '_')
    req = PAutils.HTTPRequest(actorPageURL)
    actorPage = HTML.ElementFromString(req.text)
    img = actorPage.xpath('//table[@class="infobox"]//a[@class="image"]//img/@src')
    if img:
        actorPhotoURL = 'http://www.boobpedia.com' + img[0]

    return actorPhotoURL


def getFromBabesandStars(actorName, actorEncoded):
    actorPhotoURL = ''

    actorPageURL = 'http://www.babesandstars.com/' + actorName[0:1].lower() + '/' + actorName.lower().replace(' ', '-').replace('\'', '-') + '/'
    req = PAutils.HTTPRequest(actorPageURL)
    actorPage = HTML.ElementFromString(req.text)
    img = actorPage.xpath('//div[@class="profile"]//div[@class="thumb"]/img/@src')
    if img:
        actorPhotoURL = img[0]

    return actorPhotoURL


def getFromIAFD(actorName, actorEncoded):
    actorPhotoURL = ''

    req = PAutils.HTTPRequest('http://www.iafd.com/results.asp?searchtype=comprehensive&searchstring=' + actorEncoded)
    actorSearch = HTML.ElementFromString(req.text)
    actorPageURL = actorSearch.xpath('//table[@id="tblFem"]//tbody//a/@href')
    if actorPageURL:
        actorPageURL = 'http://www.iafd.com' + actorPageURL[0]
        req = PAutils.HTTPRequest(actorPageURL)
        actorPage = HTML.ElementFromString(req.text)
        img = actorPage.xpath('//div[@id="headshot"]//img/@src')
        if img and 'nophoto' not in img[0]:
            actorPhotoURL = img[0]

    return actorPhotoURL


def getFromBabepedia(actorName, actorEncoded):
    actorPhotoURL = ''

    img = 'http://www.babepedia.com/pics/%s.jpg' % urllib.quote(actorName.title())
    req = PAutils.HTTPRequest(img, 'HEAD', bypass=False)
    if req.ok:
        actorPhotoURL = img

    return actorPhotoURL


# fetches a copy of an actor image and stores it locally, then returns a URL from which Plex can fetch it later
def cacheActorPhoto(url, actorName, **kwargs):
    req = PAutils.HTTPRequest(url, **kwargs)

    actorsResourcesPath = os.path.join(Core.bundle_path, 'Contents', 'Resources')
    if not os.path.exists(actorsResourcesPath):
        os.makedirs(actorsResourcesPath)

    extension = mimetypes.guess_extension(req.headers['Content-Type'])
    filename = 'actor.' + actorName.replace(' ', '-').lower() + extension
    filepath = os.path.join(actorsResourcesPath, filename)

    Log('Saving actor image as: "%s"' % filename)
    with codecs.open(filepath, 'wb+') as file:
        file.write(req.content)

    newPhoto = Resource.ExternalPath(filename)
    if not newPhoto:
        newPhoto = ''

    return newPhoto
