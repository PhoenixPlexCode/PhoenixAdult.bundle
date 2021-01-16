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
                    if newPhoto:
                        req = PAutils.HTTPRequest(newPhoto, 'HEAD')

                    if not req or not req.ok:
                        newPhoto = actorDBfinder(newActor)

                    Log('Actor: %s %s' % (newActor, newPhoto))

                    role = metadata.roles.new()
                    role.name = newActor
                    role.photo = newPhoto

                actorsProcessed = actorsProcessed + 1


def actorDBfinder(actorName):
    actorEncoded = urllib.quote(actorName)
    actorPhotoURL = ''

    if actorName:
        databaseName = 'AdultDVDEmpire'
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

        if not actorPhotoURL:
            databaseName = 'Boobpedia'
            actorPageURL = 'http://www.boobpedia.com/boobs/' + actorName.title().replace(' ', '_')
            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            img = actorPage.xpath('//table[@class="infobox"]//a[@class="image"]//img/@src')
            if img:
                actorPhotoURL = 'http://www.boobpedia.com' + img[0]

        if not actorPhotoURL:
            databaseName = 'Babes and Stars'
            actorPageURL = 'http://www.babesandstars.com/' + actorName[0:1].lower() + '/' + actorName.lower().replace(' ', '-').replace('\'', '-') + '/'
            req = PAutils.HTTPRequest(actorPageURL)
            actorPage = HTML.ElementFromString(req.text)
            img = actorPage.xpath('//div[@class="profile"]//div[@class="thumb"]/img/@src')
            if img:
                actorPhotoURL = img[0]

        if not actorPhotoURL:
            databaseName = 'IAFD'
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

        if not actorPhotoURL:
            databaseName = 'Babepedia'
            img = 'http://www.babepedia.com/pics/' + actorName.title().replace(' ', '%20') + '.jpg'
            req = PAutils.HTTPRequest(img, 'HEAD', bypass=False)
            if req.ok:
                actorPhotoURL = img

        if actorPhotoURL:
            Log('%s found in %s ' % (actorName, databaseName))
            Log('PhotoURL: %s' % actorPhotoURL)
        else:
            Log('%s not found' % actorName)

    return actorPhotoURL
