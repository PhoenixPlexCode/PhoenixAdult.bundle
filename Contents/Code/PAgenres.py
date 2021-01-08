
import PAdatabaseGenres


class PhoenixGenres:
    genresTable = None
    genresNum = 0

    def __init__(self):
        self.genresTable = [None] * 150
        self.genresNum = 0

    def addGenre(self, newGenre):
        self.genresTable[self.genresNum] = newGenre
        self.genresNum = self.genresNum + 1

    def clearGenres(self):
        self.genresNum = 0

    def processGenres(self, metadata):
        genresProcessed = 0
        while genresProcessed < self.genresNum:
            skip = False
            newGenre = self.genresTable[genresProcessed].replace('"', '').strip()

            searchGenreName = newGenre.lower()
            for genreName in PAdatabaseGenres.GenresSkip:
                if searchGenreName == genreName.lower():
                    skip = True
                    break

            for genreName in PAdatabaseGenres.GenresPartialSkip:
                if searchGenreName in genreName.lower():
                    skip = True
                    break

            found = False
            if not skip:
                for genreName, aliases in PAdatabaseGenres.GenresReplace.items():
                    if searchGenreName == genreName.lower() or searchGenreName in aliases:
                        found = True
                        newGenre = genreName
                        break

            if not found and not skip:
                if len(newGenre) > 25:
                    skip = True
                if ':' in metadata.title:
                    if newGenre.lower() in metadata.title.split(':')[0].lower():
                        skip = True
                if '-' in metadata.title:
                    if newGenre.lower() in metadata.title.split('-')[0].lower():
                        skip = True
                if ' ' in newGenre:
                    if 3 < len(newGenre.split(' ')):
                        skip = True

            if not skip:
                metadata.genres.add(newGenre.title())
            genresProcessed = genresProcessed + 1
