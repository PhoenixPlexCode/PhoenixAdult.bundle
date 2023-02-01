import PAsearchSites
import PAutils


def search(results, lang, siteNum, searchData):
    searchJAVID = None
    splitSearchTitle = searchData.title.split()

    if splitSearchTitle[0].startswith('3dsvr'):
        splitSearchTitle[0] = splitSearchTitle[0].replace('3dsvr', 'dsvr')
    elif splitSearchTitle[0].startswith('13dsvr'):
        splitSearchTitle[0] = splitSearchTitle[0].replace('13dsvr', 'dsvr')

    if len(splitSearchTitle) > 1:
        if unicode(splitSearchTitle[1], 'UTF-8').isdigit():
            searchJAVID = '%s-%s' % (splitSearchTitle[0], splitSearchTitle[1])

    if searchJAVID:
        searchData.encoded = searchJAVID

    req = PAutils.HTTPRequest(PAsearchSites.getSearchSearchURL(siteNum) + searchData.encoded)
    searchPageElements = HTML.ElementFromString(req.text)
    for searchResult in searchPageElements.xpath('//div[@class="card h-100"]'):
        titleNoFormatting = PAutils.parseTitle(searchResult.xpath('.//div[@class="mt-auto"]/a')[0].text_content().strip(), siteNum)
        JAVID = searchResult.xpath('.//h2')[0].text_content().strip()
        sceneURL = searchResult.xpath('.//h2//@href')[0].strip()
        curID = PAutils.Encode(sceneURL)

        date = searchResult.xpath('.//div[@class="mt-auto"]/text()')
        if date:
            releaseDate = parse(date[1].strip()).strftime('%Y-%m-%d')
        else:
            releaseDate = searchData.dateFormat() if searchData.date else ''

        displayDate = releaseDate if date else ''

        if searchJAVID:
            score = 100 - Util.LevenshteinDistance(searchJAVID.lower(), JAVID.lower())
        elif searchData.date and displayDate:
            score = 100 - Util.LevenshteinDistance(searchData.date, releaseDate)
        else:
            score = 100 - Util.LevenshteinDistance(searchData.title.lower(), titleNoFormatting.lower())

        results.Append(MetadataSearchResult(id='%s|%d|%s' % (curID, siteNum, releaseDate), name='[%s] %s %s' % (JAVID, displayDate, titleNoFormatting), score=score, lang=lang))

    return results


def update(metadata, lang, siteNum, movieGenres, movieActors, art):
    metadata_id = str(metadata.id).split('|')
    sceneURL = PAutils.Decode(metadata_id[0])
    req = PAutils.HTTPRequest(sceneURL)
    detailsPageElements = HTML.ElementFromString(req.text)

    # Title
    javID = detailsPageElements.xpath('//tr[./td[contains(., "DVD ID")]]//td[@class="tablevalue"]')[0].text_content().strip()
    title = detailsPageElements.xpath('//tr[./td[contains(., "Translated")]]//td[@class="tablevalue"]')[0].text_content().replace(javID, '').strip()

    for word, correction in censoredWordsDB.items():
        if word in title:
            title = title.replace(word, correction)

    if len(title) > 80:
        metadata.title = '[%s] %s' % (javID.upper(), PAutils.parseTitle(title, siteNum))
        metadata.summary = PAutils.parseTitle(title, siteNum)
    else:
        metadata.title = '[%s] %s' % (javID.upper(), PAutils.parseTitle(title, siteNum))

    # Studio
    studio = detailsPageElements.xpath('//tr[./td[contains(., "Studio")]]//td[@class="tablevalue"]')
    if studio:
        studioClean = studio[0].text_content().strip()
        for word, correction in censoredWordsDB.items():
            if word in studioClean:
                studioClean = studioClean.replace(word, correction)

        metadata.studio = studioClean

    # Tagline and Collection(s)
    metadata.collections.clear()
    tagline = detailsPageElements.xpath('//tr[./td[contains(., "Label")]]//td[@class="tablevalue"]')
    if tagline and tagline[0].text_content().strip():
        taglineClean = tagline[0].text_content().strip()
        for word, correction in censoredWordsDB.items():
            if word in taglineClean:
                taglineClean = taglineClean.replace(word, correction)

        metadata.tagline = taglineClean
        metadata.collections.add(metadata.tagline)
    elif studio and metadata.studio:
        metadata.collections.add(metadata.studio)
    else:
        metadata.collections.add('Japan Adult Video')

    # Director
    director = metadata.directors.new()
    directorName = detailsPageElements.xpath('//tr[./td[contains(., "Director")]]//td[@class="tablevalue"]')
    if directorName:
        director.name = directorName[0].text_content().strip()

    # Release Date
    date = detailsPageElements.xpath('//tr[./td[contains(., "Release Date")]]//td[@class="tablevalue"]')
    if date:
        date_object = datetime.strptime(date[0].text_content().strip(), '%Y-%m-%d')
        metadata.originally_available_at = date_object
        metadata.year = metadata.originally_available_at.year

    # Genres
    movieGenres.clearGenres()
    for genreLink in detailsPageElements.xpath('//tr[./td[contains(., "Genre")]]//td[@class="tablevalue"]//a'):
        genreName = genreLink.text_content().strip()

        movieGenres.addGenre(genreName)

    # Actors
    movieActors.clearActors()
    for actor in detailsPageElements.xpath('//div/div[./h2[contains(., "Featured Idols")]]//div[@class="idol-thumb"]'):
        actorName = actor.xpath('.//@alt')[0].strip().split('(')[0].replace(')', '')
        actorPhotoURL = actor.xpath('.//img/@src')[0].replace('melody-marks', 'melody-hina-marks')

        req = PAutils.HTTPRequest(actorPhotoURL)
        if 'unknown.' in req.url:
            actorPhotoURL = ''

        if javID not in (actorsCorrectionDB.keys()):
            movieActors.addActor(actorName, actorPhotoURL)
        else:
            for javCorrectionID, actors in actorsDB.items():
                if javID.lower() == javCorrectionID.lower() and actorName.lower() in map(str.lower, actors):
                    movieActors.addActor(actorName, actorPhotoURL)

    # Manually Add Actors By JAV ID
    actors = []
    for actorName, scenes in actorsDB.items():
        if javID.lower() in map(str.lower, scenes):
            actors.append(actorName)

    for actor in actors:
        movieActors.addActor(actor, '')

    # Posters
    xpaths = [
        '//tr[@class="moviecovertb"]//img/@src',
        '//div/div[./h2[contains(., "Images")]]/a/@href'
    ]

    for xpath in xpaths:
        for img in detailsPageElements.xpath(xpath):
            art.append(img)

    # JavBus Images
    # Manually Match JavBus to JAVDatabase
    for javBusID, javDatabaseIDs in crossSiteDB.items():
        if javID.lower() in map(str.lower, javDatabaseIDs):
            javID = javID.replace(javDatabaseIDs[0], javBusID)
            break

    numLen = len(javID.split('-', 1)[-1])
    if int(numLen) < 3 and javID.split('-')[0].lower() not in map(str.lower, ignoreList):
        for idx in range(1, 4 - numLen):
            javID = '%s-0%s' % (javID.split('-')[0], javID.split('-')[-1])

    javBusURL = PAsearchSites.getSearchSearchURL(912) + javID
    req = PAutils.HTTPRequest(javBusURL)
    javbusPageElements = HTML.ElementFromString(req.text)

    if '404 Page' in req.text and date:
        javBusURL = '%s_%s' % (javBusURL, date_object.strftime('%Y-%m-%d'))
        req = PAutils.HTTPRequest(javBusURL)
        javbusPageElements = HTML.ElementFromString(req.text)

    if '404 Page' not in req.text:
        xpaths = [
            '//a[contains(@href, "/cover/")]/@href',
            '//a[@class="sample-box"]/@href',
        ]

        for xpath in xpaths:
            for poster in javbusPageElements.xpath(xpath):
                if not poster.startswith('http'):
                    poster = PAsearchSites.getSearchBaseURL(912) + poster

                if 'nowprinting' not in poster and poster not in art:
                    art.append(poster)

        coverImage = javbusPageElements.xpath('//a[contains(@href, "/cover/")]/@href|//img[contains(@src, "/sample/")]/@src')
        if coverImage:
            coverImageCode = coverImage[0].rsplit('/', 1)[1].split('.')[0].split('_')[0]
            imageHost = coverImage[0].rsplit('/', 2)[0]
            coverImage = imageHost + '/thumb/' + coverImageCode + '.jpg'
            if coverImage.count('/images.') == 1:
                coverImage = coverImage.replace('thumb', 'thumbs')

            if not coverImage.startswith('http'):
                coverImage = PAsearchSites.getSearchBaseURL(912) + coverImage

            art.append(coverImage)

    images = []
    posterExists = False
    Log('Artwork found: %d' % len(art))
    for idx, posterUrl in enumerate(art, 1):
        if not PAsearchSites.posterAlreadyExists(posterUrl, metadata):
            # Download image file for analysis
            try:
                image = PAutils.HTTPRequest(posterUrl)
                if 'now_printing' not in image.url:
                    im = StringIO(image.content)
                    images.append(image)
                    resized_image = Image.open(im)
                    width, height = resized_image.size
                    # Add the image proxy items to the collection
                    if height > width:
                        # Item is a poster
                        metadata.posters[posterUrl] = Proxy.Media(image.content, sort_order=idx)

                        if 'javbus.com/pics/thumb' not in posterUrl:
                            posterExists = True
                    if width > height:
                        # Item is an art item
                        metadata.art[posterUrl] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    if not posterExists:
        for idx, image in enumerate(images, 1):
            try:
                im = StringIO(image.content)
                resized_image = Image.open(im)
                width, height = resized_image.size
                # Add the image proxy items to the collection
                if width > 1:
                    # Item is a poster
                    metadata.posters[art[idx - 1]] = Proxy.Media(image.content, sort_order=idx)
            except:
                pass

    return metadata


actorsDB = {
    'Ai Kawana': ['HUNTB-035'],
    'Ai Makise': ['SVDVD-455', 'RDT-214'],
    'Ai Sakura': ['MBM-029'],
    'Ai Uehara': ['AOZ-212Z', 'AOZ-124', 'IESP-607'],
    'Aimi Rika': ['HJMO-496'],
    'Aimi Usui': ['RTP-015', 'SCPX-020'],
    'Aino Tsubaki': ['HJMO-472'],
    'Airu Oshima': ['MIJPS-0017'],
    'Aisei Minami': ['OYC-034'],
    'Akane Mizusaki': ['NNPJ-140'],
    'Akari Asagiri': ['KCDA-073'],
    'Alice Otsu': ['HJMO-472', 'HUNTB-035'],
    'Alicia Williams': ['CRDD-007'],
    'Ami Kashiwagi': ['ANZD-056'],
    'Amu Hanamiya': ['DVDMS-699'],
    'Anju Mizushima': ['OYC-031'],
    'Anri Okita': ['MBM-029', 'MDB-433'],
    'Aoi Miyama': ['IENE-148'],
    'Aoi Shirosaki': ['OYC-040'],
    'Arisa Hanyu': ['KATU-068'],
    'Arisu Chigasaki': ['SCPX-016'],
    'Arisu Suzuki': ['AOZ-124'],
    'Asahi Mizuno': ['NHDTA-609'],
    'Asami Tsuchiya': ['SCPX-020'],
    'Asuka Asakura': ['SVDVD-455'],
    'Audrey Hempburne': ['CRDD-002'],
    'Aya Miura': ['HJMO-486'],
    'Ayaka Hirosaki': ['MEAT-034'],
    'Ayaka Mochizuki': ['HJMO-439', 'HJMO-472'],
    'Ayaka Muto': ['DVDMS-627'],
    'Ayaka Tomoda': ['AOZ-212Z', 'DANDY-275'],
    'Ayana Kawase': ['ONER-006'],
    'Ayu Sakura': ['JYMA-005', 'BANK-047', 'USAG-018'],
    'Ayumi Shinoda': ['WANZ-313', 'MBM-029'],
    'Azusa Misaki': ['SAIT-023'],
    'Chigusa Hara': ['SAIT-004', 'MBM-029'],
    'Chika Hirako': ['AOZ-124'],
    'Chinatsu Koizumi': ['HUNT-436'],
    'Chisa Hoshino': ['OYC-040'],
    'Chitose Saegusa': ['DVDMS-674'],
    'Darcia Lee': ['CRDD-002', 'CRDD-004'],
    'Eimi Fukada': ['MIAA-448'],
    'Ena Koume': ['USAG-027'],
    'Erika Kitagawa': ['OYC-029'],
    'Erika Kurisu': ['KCDA-073'],
    'Erika Mikami': ['DANDY-593'],
    'Eriko Miura': ['MKCK-124'],
    'Erina': ['MIAD-595'],
    'Gabbie Carter': ['CRDD-001', 'CRDD-013'],
    'Hana Yoshida': ['DANDY-275'],
    'Harua Narumiya': ['HUNTB-070', 'HUNTB-084'],
    'Haruki Sato': ['MBM-029'],
    'Haruna Ayane': ['OYC-030'],
    'Haruna Kawai': ['FLAV-288'],
    'Haruna Nakayama': ['SVDVD-288'],
    'Haruna Saeki': ['OYC-033'],
    'Harura Mori': ['NHDTB-151'],
    'Hibiki Hoshino': ['PPSD-052', 'SCPX-089'],
    'Hijiri Maihara': ['SABA-181'],
    'Hikaru Kawana': ['SVDVD-455'],
    'Hikaru Konno': ['HJMO-472'],
    'Hikaru Minatsuki': ['NCYF-012', 'HUNTB-035'],
    'Hina Kamikawa': ['MDB-433'],
    'Hinami Narisawa': ['JYMA-009'],
    'Hinano Kikuchi': ['SCPX-089'],
    'Hitomi Enshiro': ['CETD-296'],
    'Hitomi Honda': ['HJMO-496'],
    'Hiyori Mihashi': ['SCPX-018'],
    'Honoka Orihara': ['SCPX-089'],
    'Honami Akagi': ['BANK-052'],
    'Hono Wakamiya': ['USAG-003'],
    'Honoka Tsuji': ['DVDMS-699'],
    'Io Hayami': ['KTKC-135'],
    'Iroha Suzumura': ['NNPJ-140'],
    'Itsuki Maino': ['NNPJ-136'],
    'Jillian Janson': ['CRDD-004', 'CRDD-007', 'CRDD-013'],
    'Julia Yoshine': ['DVDMS-623', 'HJMO-439', 'MIMK-078', 'HUNTB-084'],
    'June Lovejoy': ['DVDMS-553'],
    'Kaede Niyama': ['NHDTA-609'],
    'Kaho Shibuya': ['DANDY-593', 'NHDTB-151'],
    'Kana Amatsuki': ['OYC-031'],
    'Kana Miyashita': ['PPPD-408'],
    'Kaname Tsubaki': ['DANDY-593'],
    'Kanari Tsubaki': ['MIAD-599'],
    'Kanon Takigawa': ['RCT-527'],
    'Kaori Saejima': ['MBM-029'],
    'Karen Asahina': ['HJMO-486'],
    'Karin Natsumi': ['OYC-031'],
    'Kokoa Aisu': ['ABP-060'],
    'Kokona Hakuto': ['ABP-060'],
    'Kotone Amamiya': ['OKAD-398'],
    'Koyo Hasegawa': ['USAG-034'],
    'Krystal Swift': ['HIKR-108'],
    'Kurea Hasumi': ['MBM-029'],
    'Kurumi Ohashi': ['NGD-053'],
    'Kyler Quinn': ['CRDD-002'],
    'Kyoko Maki': ['VSPDS-654', 'OYC-033', 'PPSD-052', 'RCT-508'],
    'Lana Sharapova': ['ANCI-038'],
    'Lily Glee': ['ANCI-038'],
    'Madi Collins': ['KTKL-112'],
    'Maika Kazane': ['RDT-213'],
    'Maiko Matsuura': ['MUKD-329'],
    'Maina Yuri': ['HUNTA-880'],
    'Mako Oda': ['DVDMS-627'],
    'Makoto Takeuchi': ['SCPX-020'],
    'Mami Sakurazaka': ['CHN-202'],
    'Mana Minami': ['HJMO-439'],
    'Manami Oura': ['HUNTB-070'],
    'Mao Hamasaki': ['HJMO-494', 'MBM-029', 'OYC-036'],
    'Mao Ito': ['HUNTB-070'],
    'Mao Kurata': ['HUNTA-880'],
    'Marika': ['OKAD-398'],
    'Marin Aihara': ['NNPJ-140'],
    'Mayu Otsuka': ['RCT-508'],
    'Megan Marx': ['CRDD-001'],
    'Megu Mio': ['HJMO-494'],
    'Megumi Shino': ['DANDY-593'],
    'Megumi Shino': ['OYC-030'],
    'Mei Matsumoto': ['RIX-014'],
    'Meisa Chibana': ['MBM-029'],
    'Miho Tachibana': ['HUNT-436'],
    'Miho Tono': ['HUNTA-880', 'OYC-036'],
    'Miina Wakatsuki': ['PPSD-052', 'SABA-181'],
    'Miki Sanada': ['USAG-029'],
    'Miki Sunohara': ['AOZ-212Z'],
    'Mikoto Yatsuka': ['UMSO-032'],
    'Miku Ikuta': ['HUNTB-035'],
    'Miku Maina': ['FONE-136'],
    'Mikuni Maisaki': ['MDB-433'],
    'Mikuru Shiiba': ['HUNTB-070'],
    'Mina Kitano': ['HJMO-486'],
    'Mina Kubotsuka': ['SABA-181'],
    'Mina Saotome': ['CHRV-139'],
    'Minami Ayase': ['DISM-003'],
    'Mio Kanai': ['OYC-034'],
    'Mio Katana': ['SG-005'],
    'Mio Kayama': ['OYC-033'],
    'Mio Morishita': ['DANDY-593'],
    'Mio Takahashi': ['NGD-065'],
    'Mion Hazuki': ['KATU-085', 'JYMA-004'],
    'Misa Kudo': ['OYC-029'],
    'Mitsuki An': ['DISM-003'],
    'Miu Kimura': ['RDT-214'],
    'Miwako Yamamoto': ['TYOD-146'],
    'Miyu Kanade': ['HUNTA-880', 'OYC-035'],
    'Mizuho Eiyama': ['MUKD-363'],
    'Mizuna Wakatsuki': ['CJOD-330'],
    'Momo Minami': ['HJMO-486'],
    'Momo Nohara': ['RCT-452'],
    'Momoka Nishina': ['KCDA-073'],
    'Mona Kasuga': ['NMP-006'],
    'Monami Takarada': ['HJMO-496'],
    'Nagi Kamiya': ['ABW-134'],
    'Nana Kurumi': ['SABA-181'],
    'Nana Usami': ['DANDY-275'],
    'Nanako Mori': ['SDMS-990'],
    'Nanami Matsumoto': ['DVDMS-635', 'MIMK-098'],
    'Nanase Hazuki': ['TDSU-071', 'RCT-527'],
    'Nao Mizuki': ['OYC-035'],
    'Narumi Sayaka': ['MOT-132'],
    'Natsuki Hasegawa': ['OYC-040', 'RCT-527'],
    'Natsuki Yokoyama': ['JYMA-001'],
    'Neiro Otoha': ['HUNTA-880'],
    'Nene Tanaka': ['JYMA-011', 'KAM-090'],
    'Nina Nishimura': ['JYMA-013', 'CLUB-651'],
    'Nozomi Arimura': ['CHRV-154', 'SAIT-023'],
    'Nozomi Azuma': ['OKSN-336'],
    'Nozomi Osawa': ['OKAD-398'],
    'Pamela Morrison': ['CRDD-007'],
    'Rara Unno': ['OYC-032'],
    'Rei Manami': ['MBM-029'],
    'Reia Miyasaka': ['SDMS-987', 'RDT-213', 'SCPX-018'],
    'Reika Hoshiumi': ['RCT-527'],
    'Reiko Kobayakawa': ['KCDA-073'],
    'Reiko Nakamori': ['TTKK-007', 'NASS-392'],
    'Reiko Sawamura': ['NASS-392'],
    'Ren Ayase': ['MDB-433', 'SAIT-003', 'OYC-041'],
    'Rena Aoi': ['SCPX-089'],
    'Renai Amane': ['CHRV-137'],
    'Ribon Yumesaki': ['RTP-015'],
    'Rie Matsuo': ['JUTA-132'],
    'Riko Honda': ['MBM-029'],
    'Rin Aoki': ['DISM-003'],
    'Rina Ebina': ['ONER-006', 'OYC-030'],
    'Rina Kawase': ['NNPJ-140'],
    'Rino Yuki': ['DVDMS-723'],
    'Rio Hamazaki': ['HUNT-430'],
    'Rion Nishikawa': ['RCT-508'],
    'Riona Minami': ['OYC-034', 'OYC-036'],
    'Ririka Hoshikawa': ['OYC-036'],
    'Risa Kamiki': ['IENE-148'],
    'Risa Kasumi': ['MDB-433'],
    'Risa Murakami': ['DANDY-275'],
    'Runa Nanami': ['OYC-030'],
    'Rurika Misato': ['HJMO-486'],
    'Ryo Arimori': ['OYC-029', 'RDT-213'],
    'Ryo Kurokawa': ['HUNT-436'],
    'Ryo Tsujimoto': ['OYC-033'],
    'Sae Aihara': ['OYC-041'],
    'Saki Shinoharabi': ['HUNT-430'],
    'Sakura Kirishima': ['WANZ-461'],
    'Sakura Kiryu': ['OKAD-398'],
    'Sally': ['OYC-034'],
    'Sana Moriho': ['OYC-040'],
    'Sara Mizusawa': ['ONER-006'],
    'Sara Saijo': ['OYC-035', 'OYC-029', 'OYC-039'],
    'Satoho Kodaka': ['ONER-006'],
    'Saya Takazawa': ['SGR-02'],
    'Seri Yuki': ['RDT-214'],
    'Shiiba Mikuru': ['KATU-087'],
    'Shino Tanaka': ['HUNTB-070', 'HUNTB-084'],
    'Shion Amane': ['HMGL-001'],
    'Shion Fujimoto': ['OYC-039'],
    'Shiori Tsukada': ['TNOZ-015', 'SVDVD-455', 'FLAV-277', 'CHRV-138', 'SVDVD-460', 'CJOD-330', 'KCDA-073'],
    'Shizuku Amayoshi': ['SCPX-089'],
    'Shizuku Hanai': ['HJMO-486'],
    'Shizuku Ueno': ['HUNT-436'],
    'Sumire Matsu': ['KCDA-073'],
    'Sumire Seto': ['SCPX-018'],
    'Suzu Akane': ['MUKD-364'],
    'Suzu Miyashita': ['BAB-028'],
    'Suzu Monami': ['HUNTB-035'],
    'Tiffany Tatum': ['CRDD-004'],
    'Tomoka Hamada': ['TMEM-052'],
    'Tomoko Kamisaka': ['HJMO-494'],
    'Tsubomi': ['WA-192', 'HUNT-436'],
    'Tsugumi Mutou': ['OYC-032'],
    'Umi Hinata': ['RCT-508'],
    'Umi Mitoma': ['NIKM-010'],
    'Uta Sachino': ['OYC-030'],
    'Vanna Bardot': ['CRDD-001'],
    'Waka Ninomiya': ['	NHDTB-151'],
    'Yu Shinoda': ['BF-118', 'ALB-195', 'DANDY-275', 'RCT-452'],
    'Yui Aoba': ['OYC-030'],
    'Yui Hatano': ['IENE-148'],
    'Yui Ishikawa': ['SVDVD-455'],
    'Yui Misaki': ['SAIT-001', 'TIN-017'],
    'Yui Nanase': ['HUNT-436'],
    'Yui Saotome': ['SCPX-020'],
    'Yui Suijo': ['PPSD-052'],
    'Yuka Hayama': ['OYC-031'],
    'Yuka Minase': ['MBM-029'],
    'Yuka Tachibana': ['OYC-041'],
    'Yukari Uno': ['PPSD-052'],
    'Yuki Maeda': ['NHDTA-609'],
    'Yuki Ozawa': ['SCPX-020'],
    'Yuki Sakurai': ['TTKK-005'],
    'Yukie Aono': ['TTKK-003'],
    'Yukina Futaba': ['OYC-030'],
    'Yukino Nagasawa': ['DVDMS-623'],
    'Yume Igarashi': ['NCYF-011'],
    'Yume Mizuki': ['PPSD-052'],
    'Yumi Kazama': ['MKCK-124'],
    'Yuni Katsuragi': ['SCPX-016'],
    'Yunon Hoshimiya': ['HJMO-494'],
    'Yuri Honma': ['JYMA-002', 'OYC-035', 'OYC-039'],
    'Yuri Hyuga': ['STAR-3102'],
    'Yuri Oshikawa': ['HJMO-496', 'HUNTB-084'],
    'Yuri Sasahara': ['SORA-428'],
    'Yuria Seto': ['RCT-452'],
    'Yurika Aoi': ['KATU-082'],
    'Yuu Kiriyama': ['HUNTB-084'],
}


actorsCorrectionDB = {
    'JUTA-132': ['Rie Matsuo'],
    'CRDD-007': ['Alicia Williams', 'Jillian Janson', 'Pamela Morrison']
}


censoredWordsDB = {
    'A***e': 'Abuse',
    'B******y': 'Brutally',
    'C***d': 'Child',
    'C*ck': 'Cock',
    'Cum-D***king': 'Cum-Drinking',
    'D******e': 'Disgrace',
    'D***k ': 'Drunk ',
    'D***k It': 'Drink It',
    'D***k-': 'Drunk-',
    'D***k.': 'Drunk.',
    'D***kest': 'Drunkest',
    'D***king': 'Drinking',
    'D**g': 'Drug',
    'Drunk It': 'Drink It',
    'F***e': 'Force',
    'G*******g': 'Gangbang',
    'H*******m': 'Hypnotism',
    'I****t': 'Incest',
    'K**l': 'Kill',
    'K*d': 'Kid',
    'M****t': 'Molest',
    'M************n': 'Mother and Son',
    'P****h': 'Punish',
    'R****g': 'Raping',
    'R**e': 'Rape',
    'S*********l': 'Schoolgirl',
    'S********l': 'Schoolgirl',
    'S*****t': 'Student',
    'S***e': 'Slave',
    'SK**led': 'Skilled',
    'SK**lful': 'Skillful',
    'SK**ls': 'Skills',
    'T******e': 'Tentacle',
    'T*****e': 'Torture',
    'U*********s': 'Unconscious',
    'V*****e': 'Violate',
    'V*****t': 'Violent',
    'Y********l\'s': 'Young Girl\'s',
}


crossSiteDB = {
    'DVAJ-': ['DVAJ-0', 'DVAJ-0003', 'DVAJ-0013', 'DVAJ-0021', 'DVAJ-0031', 'DVAJ-0039'],
    'DVAJ-0': ['DVAJ-00', 'DVAJ-0027', 'DVAJ-0032'],
    'STAR-128_2008-11-06': ['STAR-128'],
    'STAR-134_2008-12-18': ['STAR-134'],
}


ignoreList = {
    'SEXY', 'MEEL', 'SKOT', 'SCD', 'GDSC'
}
