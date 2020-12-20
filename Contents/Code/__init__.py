import os
import re
import random
import requests
import urllib
import urlparse
import json
from datetime import datetime
from PIL import Image
from cStringIO import StringIO
from dateutil.parser import parse
import time
import base64
import PAactors
import PAgenres
import PAsearchSites
import PAsiteList
import PAutils


def Start():
    HTTP.ClearCache()
    HTTP.CacheTime = CACHE_1MINUTE * 20
    HTTP.Headers['User-Agent'] = PAutils.getUserAgent()
    HTTP.Headers['Accept-Encoding'] = 'gzip'

    requests.packages.urllib3.disable_warnings()


class PhoenixAdultAgent(Agent.Movies):
    name = 'PhoenixAdult'
    languages = [Locale.Language.English]
    accepts_from = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.lambda']
    primary_provider = True

    def search(self, results, media, lang):
        if Prefs['strip_enable']:
            title = media.name.split(Prefs['strip_symbol'], 1)[0]
        else:
            title = media.name

        if media.primary_metadata is not None:
            title = media.primary_metadata.studio + ' ' + media.primary_metadata.title

        trashTitle = (
            'RARBG', 'COM', r'\d{3,4}x\d{3,4}', 'HEVC', 'H265', 'AVC', r'\dK',
            r'\d{3,4}p', 'TOWN.AG_', 'XXX', 'MP4', 'KLEENEX', 'SD', 'HD',
            'ForeverAloneDude'
        )

        title = re.sub(r'\W', ' ', title)
        for trash in trashTitle:
            title = re.sub(r'\b%s\b' % trash, '', title, flags=re.IGNORECASE)
        title = ' '.join(title.split())

        Log('*******MEDIA TITLE****** %s' % title)

        Log('Getting Search Settings for: %s' % title)
        searchSettings = PAsearchSites.getSearchSettings(title)
        siteNum = searchSettings[0]
        searchTitle = searchSettings[1]
        searchDate = searchSettings[2]
        Log('Search Title: %s' % searchTitle)
        if searchDate:
            Log('Search Date: %s' % searchDate)

        encodedTitle = urllib.quote(searchTitle)
        Log(encodedTitle)

        if siteNum is not None:
            # Blacked Raw
            if siteNum == 0:
                results = PAsiteList.networkStrike3.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Blacked
            elif siteNum == 1:
                results = PAsiteList.networkStrike3.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Brazzers
            elif siteNum == 2 or (54 <= siteNum <= 81) or siteNum == 582 or siteNum == 690:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Naughty America
            elif (5 <= siteNum <= 51) or siteNum == 341 or (393 <= siteNum <= 396) or (467 <= siteNum <= 468) or siteNum == 581 or siteNum == 620 or siteNum == 625 or siteNum == 691 or siteNum == 749:
                results = PAsiteList.siteNaughtyAmerica.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Vixen
            elif siteNum == 52:
                results = PAsiteList.networkStrike3.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # GirlsWay
            elif siteNum == 53 or (375 <= siteNum <= 379) or (795 <= siteNum <= 797):
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # 21Naturals
            elif siteNum == 183 or (373 <= siteNum <= 374):
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Evil Angel
            elif siteNum == 277 or siteNum == 975:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # XEmpire / Hardx
            elif siteNum == 278:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # XEmpire / Eroticax
            elif siteNum == 285:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # XEmpire / Darkx
            elif siteNum == 286:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # XEmpire / Lesbianx
            elif siteNum == 287:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Pure Taboo
            elif siteNum == 281:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Blowpass / Throated
            elif siteNum == 329:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Blowpass / Mommy Blows Best
            elif siteNum == 351:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Blowpass / Only Teen Blowjobs
            elif siteNum == 352:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Blowpass / 1000 Facials

            elif siteNum == 353:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Blowpass / Immoral Live
            elif siteNum == 354:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Blowpass / My XXX Pass
            elif siteNum == 861:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Mile High Media
            elif (361 <= siteNum <= 364) or siteNum == 852 or (914 <= siteNum <= 915):
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Fantasy Massage
            elif siteNum == 330 or (355 <= siteNum <= 360) or siteNum == 750:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # 21Sextury
            elif (365 <= siteNum <= 372) or siteNum == 466 or siteNum == 692:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Girlfriends Films
            elif siteNum == 380:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Burning Angel
            elif siteNum == 381:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Pretty Dirty
            elif siteNum == 382:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Devil's Film
            elif siteNum == 383:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Peter North
            elif siteNum == 384:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Rocco Siffredi
            elif siteNum == 385:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Tera Patrick
            elif siteNum == 386:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Sunny Leone
            elif siteNum == 387:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Lane Sisters
            elif siteNum == 388:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Dylan Ryder
            elif siteNum == 389:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Abbey Brooks
            elif siteNum == 390:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Devon Lee
            elif siteNum == 391:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Hanna Hilton
            elif siteNum == 392:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # 21Sextreme
            elif (460 <= siteNum <= 465):
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # X-Art
            elif siteNum == 82:
                results = PAsiteList.siteXart.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Bang Bros
            elif (83 <= siteNum <= 135):
                results = PAsiteList.siteBangBros.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Tushy
            elif siteNum == 136:
                results = PAsiteList.networkStrike3.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Reality Kings
            elif (137 <= siteNum <= 182) or (822 <= siteNum <= 828):
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # PornFidelity
            elif siteNum == 184:
                results = PAsiteList.networkPornFidelity.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # TeenFidelity
            elif siteNum == 185:
                results = PAsiteList.networkPornFidelity.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Kelly Madison
            elif siteNum == 186:
                results = PAsiteList.networkPornFidelity.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # TeamSkeet
            elif (187 <= siteNum <= 215) or (566 <= siteNum <= 567) or siteNum == 626 or siteNum == 686 or siteNum == 748 or siteNum == 807 or (845 <= siteNum <= 851) or siteNum == 875 or (997 <= siteNum <= 1011):
                results = PAsiteList.networkTeamSkeet.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Porndoe Premium
            elif (216 <= siteNum <= 259):
                results = PAsiteList.sitePorndoePremium.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Legal Porno
            elif siteNum == 260:
                results = PAsiteList.siteLegalPorno.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Mofos
            elif (261 <= siteNum <= 270) or siteNum == 583 or (738 <= siteNum <= 740) or (1059 <= siteNum <= 1064):
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Babes
            elif (271 <= siteNum <= 276):
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # GloryHoleSecrets
            elif siteNum == 279:
                results = PAsiteList.siteGloryHoleSecrets.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # NewSensations
            elif siteNum == 280:
                results = PAsiteList.siteNewSensations.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Swallowed
            elif siteNum == 282:
                results = PAsiteList.networkSteppedUp.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # TrueAnal
            elif siteNum == 283:
                results = PAsiteList.networkSteppedUp.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Nympho
            elif siteNum == 284:
                results = PAsiteList.networkSteppedUp.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Twistys
            elif (288 <= siteNum <= 291) or siteNum == 768:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Spizoo
            elif siteNum == 293 or (571 <= siteNum <= 577):
                results = PAsiteList.siteSpizoo.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Private
            elif (294 <= siteNum <= 305):
                results = PAsiteList.sitePrivate.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # PornPros Network
            elif (306 <= siteNum <= 327) or (479 <= siteNum <= 489) or siteNum == 624 or siteNum == 769 or siteNum == 844 or siteNum == 890:
                results = PAsiteList.networkPornPros.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # DigitalPlayground
            elif siteNum == 328:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # SexyHub
            elif (333 <= siteNum <= 339) or (406 <= siteNum <= 407):
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # FullPornNetwork
            elif (343 <= siteNum <= 350):
                results = PAsiteList.networkFullPornNetwork.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # DogfartNetwork
            elif (408 <= siteNum <= 431):
                results = PAsiteList.networkDogfart.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # FakeHub
            elif siteNum == 340 or (397 <= siteNum <= 407):
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # JulesJordan
            elif siteNum == 432:
                results = PAsiteList.siteJulesJordan.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Manuel Ferrara
            elif siteNum == 522:
                results = PAsiteList.siteJulesJordan.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # The Ass Factory
            elif siteNum == 523:
                results = PAsiteList.siteJulesJordan.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Sperm Swallowers
            elif siteNum == 524:
                results = PAsiteList.siteJulesJordan.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # GirlGirl
            elif siteNum == 782:
                results = PAsiteList.siteJulesJordan.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # DDF Network
            elif (440 <= siteNum <= 447):
                results = PAsiteList.networkDDFNetwork.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # PerfectGonzo
            elif (448 <= siteNum <= 459) or (908 <= siteNum <= 911):
                results = PAsiteList.networkPerfectGonzo.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # BadoinkVR Network
            elif (469 <= siteNum <= 473):
                results = PAsiteList.networkBadoinkVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VRBangers
            elif siteNum == 474:
                results = PAsiteList.siteVRBangers.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # SexBabesVR
            elif siteNum == 475:
                results = PAsiteList.networkHighTechVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # SinsVR
            elif siteNum == 569:
                results = PAsiteList.networkHighTechVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # StasyQ VR
            elif siteNum == 570:
                results = PAsiteList.networkHighTechVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # WankzVR
            elif siteNum == 476:
                results = PAsiteList.siteMilfVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # MilfVR
            elif siteNum == 477:
                results = PAsiteList.siteMilfVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Joymii
            elif siteNum == 478:
                results = PAsiteList.siteJoymii.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Kink
            elif (490 <= siteNum <= 521) or siteNum == 687 or (735 <= siteNum <= 736) or (873 <= siteNum <= 874) or (888 <= siteNum <= 889):
                results = PAsiteList.networkKink.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Nubiles
            elif (525 <= siteNum <= 545) or (755 <= siteNum <= 756) or siteNum == 766 or (995 <= siteNum <= 996):
                results = PAsiteList.networkNubiles.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # BellaPass
            elif (548 <= siteNum <= 563):
                results = PAsiteList.networkBellaPass.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # AllureMedia
            elif (564 <= siteNum <= 565):
                results = PAsiteList.siteAllureMedia.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Manyvids
            elif siteNum == 568:
                results = PAsiteList.siteManyvids.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VirtualTaboo
            elif siteNum == 292:
                results = PAsiteList.siteVirtualTaboo.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VirtualRealPorn
            elif siteNum == 342:
                results = PAsiteList.siteVirtualReal.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # CzechVR Network
            elif (578 <= siteNum <= 580):
                results = PAsiteList.networkCzechVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # FinishesTheJob
            elif (584 <= siteNum <= 586):
                results = PAsiteList.siteFinishesTheJob.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Wankz Network
            elif (587 <= siteNum <= 619):
                results = PAsiteList.networkWankz.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # MetArt Network
            elif (621 <= siteNum <= 623) or (753 <= siteNum <= 754) or (816 <= siteNum <= 821):
                results = PAsiteList.networkMetArt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Tonights Girlfriend
            elif siteNum == 627:
                results = PAsiteList.siteTonightsGirlfriend.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Karups
            elif (628 <= siteNum <= 630):
                results = PAsiteList.siteKarups.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # TeenMegaWorld
            elif (631 <= siteNum <= 666) or siteNum == 930:
                results = PAsiteList.networkTeenMegaWorld.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Screwbox
            elif siteNum == 668:
                results = PAsiteList.siteScrewbox.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # DorcelClub
            elif siteNum == 669:
                results = PAsiteList.siteDorcelClub.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Tushy
            elif siteNum == 670:
                results = PAsiteList.networkStrike3.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Deeper
            elif siteNum == 671:
                results = PAsiteList.networkStrike3.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # MissaX / AllHerLuv
            elif siteNum == 672 or siteNum == 673:
                results = PAsiteList.siteMissaX.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Mylf
            elif (674 <= siteNum <= 683) or siteNum == 757 or siteNum == 842 or (siteNum >= 853 and siteNum <= 858) or (881 <= siteNum <= 887):
                results = PAsiteList.siteMylf.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Manually Add Actors
            elif siteNum == 684:
                results = PAsiteList.addActors.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # First Anal Quest
            elif siteNum == 685:
                results = PAsiteList.siteFirstAnalQuest.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Hegre
            elif siteNum == 688:
                results = PAsiteList.siteHegre.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Femdom Empire
            elif siteNum == 689 or siteNum == 694:
                results = PAsiteList.networkFemdomEmpire.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Dorcel Vision
            elif siteNum == 693:
                results = PAsiteList.siteDorcelVision.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # XConfessions
            elif siteNum == 695:
                results = PAsiteList.siteXConfessions.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # CzechAV
            elif (696 <= siteNum <= 728):
                results = PAsiteList.networkCzechAV.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ArchAngel
            elif siteNum == 729:
                results = PAsiteList.siteArchAngel.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # We Are Hairy
            elif siteNum == 730:
                results = PAsiteList.siteWeAreHairy.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Love Her Feet
            elif siteNum == 731:
                results = PAsiteList.siteLoveHerFeet.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # MomPOV
            elif siteNum == 732:
                results = PAsiteList.siteMomPOV.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Property Sex
            elif siteNum == 733:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # FuelVirtual
            elif (546 <= siteNum <= 547):
                results = PAsiteList.networkFuelVirtual.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # TransAngels
            elif siteNum == 737:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Straplezz
            elif siteNum == 741:
                results = PAsiteList.siteStraplezz.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # LittleCaprice
            elif siteNum == 742:
                results = PAsiteList.siteLittleCaprice.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # WowGirls
            elif siteNum == 743:
                results = PAsiteList.siteWowGirls.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VIPissy
            elif siteNum == 744:
                results = PAsiteList.siteVIPissy.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # GirlsOutWest
            elif siteNum == 745:
                results = PAsiteList.siteGirlsOutWest.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Girls Rimming
            elif siteNum == 746:
                results = PAsiteList.siteGirlsRimming.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Gangbang Creampie
            elif siteNum == 747:
                results = PAsiteList.siteGangbangCreampie.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # StepSecrets
            elif siteNum == 751:
                results = PAsiteList.siteStepSecrets.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VRHush
            elif siteNum == 752:
                results = PAsiteList.siteVRHush.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Fitting-Room
            elif siteNum == 758:
                results = PAsiteList.siteFittingRoom.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # FamilyHookups
            elif siteNum == 759:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Clips4Sale
            elif siteNum == 760:
                results = PAsiteList.siteClips4Sale.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VogoV
            elif siteNum == 761:
                results = PAsiteList.siteVogoV.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Ultrafilms
            elif siteNum == 762:
                results = PAsiteList.siteUltrafilms.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # fuckingawesome.com
            elif siteNum == 763:
                results = PAsiteList.siteFuckingAwesome.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ToughLoveX
            elif siteNum == 764:
                results = PAsiteList.siteToughLoveX.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # cumlouder.com
            elif siteNum == 765:
                results = PAsiteList.siteCumLouder.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # AllAnal
            elif siteNum == 767:
                results = PAsiteList.networkSteppedUp.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ZeroTolerance
            elif siteNum == 770:
                results = PAsiteList.siteZTOD.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ClubFilly
            elif siteNum == 771:
                results = PAsiteList.siteClubFilly.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Intersec
            elif (772 <= siteNum <= 781):
                results = PAsiteList.networkIntersec.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Cherry Pimps
            elif (783 <= siteNum <= 792) or (1052 <= siteNum <= 1056):
                results = PAsiteList.networkCherryPimps.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Wicked
            elif siteNum == 793:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # 18OnlyGirls
            elif siteNum == 794:
                results = PAsiteList.site18OnlyGirls.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # LilHumpers
            elif siteNum == 798:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Bellesa Films
            elif siteNum == 799 or siteNum == 876:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ClubSeventeen
            elif siteNum == 800:
                results = PAsiteList.siteClubSeventeen.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Elegant Angel
            elif siteNum == 801:
                results = PAsiteList.siteElegantAngel.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Family Sinners
            elif siteNum == 802:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ReidMyLips
            elif siteNum == 803:
                results = PAsiteList.siteReidMyLips.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Playboy Plus
            elif siteNum == 804:
                results = PAsiteList.sitePlayboyPlus.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Meana Wolf
            elif siteNum == 805:
                results = PAsiteList.siteMeanaWolf.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Transsensual
            elif siteNum == 806:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Erito
            elif siteNum == 808:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # TrueAmateurs
            elif siteNum == 809:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Hustler
            elif siteNum == 810:
                results = PAsiteList.networkMetArt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # AmourAngels
            elif siteNum == 811:
                results = PAsiteList.siteAmourAngels.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # JAV
            elif siteNum == 812:
                results = PAsiteList.networkR18.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Bang
            elif siteNum == 813:
                results = PAsiteList.networkBang.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Vivid
            elif siteNum == 814:
                results = PAsiteList.siteVivid.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # JAY's POV
            elif siteNum == 815:
                results = PAsiteList.siteJaysPOV.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # PJGirls
            elif siteNum == 667:
                results = PAsiteList.sitePJGirls.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # PureCFNM Network
            elif (829 <= siteNum <= 834):
                results = PAsiteList.networkPureCFNM.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # BAMVisions
            elif siteNum == 835:
                results = PAsiteList.siteBAMVisions.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ATKGirlfriends
            elif siteNum == 836:
                results = PAsiteList.siteATKGirlfriends.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # TwoWebMedia
            elif (837 <= siteNum <= 839):
                results = PAsiteList.networkTwoWebMedia.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Interracial Pass
            elif siteNum == 840:
                results = PAsiteList.siteInterracialPass.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # LookAtHerNow
            elif siteNum == 841:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # XEmpire / AllBlackX
            elif siteNum == 843:
                results = PAsiteList.networkGammaEnt.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Deviant Hardcore
            elif siteNum == 859:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # She Will Cheat
            elif siteNum == 860:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # SinsLife
            elif siteNum == 862:
                results = PAsiteList.siteSinsLife.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Puffy Network
            elif siteNum == 863 or (867 <= siteNum <= 870):
                results = PAsiteList.networkPuffy.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # SinX
            elif (864 <= siteNum <= 866) or siteNum == 871:
                results = PAsiteList.networkSinX.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Kinky Spa
            elif siteNum == 872:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Reality Lovers
            elif siteNum == 877:
                results = PAsiteList.siteRealityLovers.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Adult Time
            elif siteNum == 878:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # RealJamVR
            elif siteNum == 879:
                results = PAsiteList.networkHighTechVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # BBC Paradise
            elif siteNum == 880:
                results = PAsiteList.siteMylf.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # HoloGirlsVR
            elif siteNum == 891:
                results = PAsiteList.siteHoloGirlsVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # LethalHardcoreVR
            elif siteNum == 892:
                results = PAsiteList.siteLethalHardcoreVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Gender X
            elif siteNum == 893:
                results = PAsiteList.networkGammaEntOther.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # WhoreCraftVR
            elif siteNum == 894:
                results = PAsiteList.siteLethalHardcoreVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Defeated
            elif siteNum == 895 or siteNum == 896:
                results = PAsiteList.siteDefeated.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # XVirtual
            elif siteNum == 897:
                results = PAsiteList.siteXVirtual.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Lust Reality
            elif siteNum == 898:
                results = PAsiteList.siteLustReality.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Sex Like Real
            elif siteNum == 899:
                results = PAsiteList.siteSexLikeReal.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # DoeGirls
            elif siteNum == 900:
                results = PAsiteList.sitePorndoePremium.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Xillimite
            elif siteNum == 901:
                results = PAsiteList.siteXillimite.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VRP Films
            elif siteNum == 902:
                results = PAsiteList.siteVRPFilms.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VR Latina
            elif siteNum == 903:
                results = PAsiteList.siteVRLatina.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # VRConk
            elif siteNum == 904:
                results = PAsiteList.siteVRConk.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # RealJamVR
            elif siteNum == 905:
                results = PAsiteList.networkHighTechVR.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Evolved Fights Network
            elif siteNum == 906 or siteNum == 907:
                results = PAsiteList.networkEvolvedFights.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # JavBus
            elif siteNum == 912:
                results = PAsiteList.networkJavBus.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Hucows
            elif siteNum == 913:
                results = PAsiteList.siteHucows.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Why Not Bi
            elif siteNum == 916:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # HentaiPros
            elif siteNum == 917:
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # PornPortal
            elif (918 <= siteNum <= 929):
                results = PAsiteList.network1service.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # AllAnalAllTheTime
            elif siteNum == 931:
                results = PAsiteList.siteAllAnalAllTheTime.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # QueenSnake
            elif siteNum == 932:
                results = PAsiteList.siteQueenSnake.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # QueenSect
            elif siteNum == 933:
                results = PAsiteList.siteQueenSnake.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Fetish Network
            elif (934 <= siteNum <= 937):
                results = PAsiteList.networkKink.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ScrewMeToo
            elif siteNum == 938:
                results = PAsiteList.siteScrewMeToo.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Box Truck Sex
            elif siteNum == 939:
                results = PAsiteList.siteBoxTruckSex.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Aussie Ass
            elif siteNum == 940:
                results = PAsiteList.siteAussieAss.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # 5Kporn
            elif (941 <= siteNum <= 942):
                results = PAsiteList.network5Kporn.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Teen Core Club
            elif (943 <= siteNum <= 974):
                results = PAsiteList.networkTeenCoreClub.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Exploited X
            elif (976 <= siteNum <= 978):
                results = PAsiteList.networkExploitedX.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Desperate Amateurs
            elif (siteNum == 979):
                results = PAsiteList.siteDesperateAmateurs.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Dirty Hard Drive
            elif (980 <= siteNum <= 987):
                results = PAsiteList.networkDirtyHardDrive.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Melone Challenge
            elif (siteNum == 988):
                results = PAsiteList.siteMeloneChallenge.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Holly Randall
            elif siteNum == 989:
                results = PAsiteList.siteHollyRandall.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # In The Crack
            elif siteNum == 990:
                results = PAsiteList.siteInTheCrack.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Angela White
            elif siteNum == 991:
                results = PAsiteList.siteAngelaWhite.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Cumbizz
            elif siteNum == 992:
                results = PAsiteList.siteCumbizz.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Pornstar Platinum
            elif siteNum == 993:
                results = PAsiteList.sitePornstarPlatinum.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Woodman Casting X
            elif siteNum == 994:
                results = PAsiteList.siteWoodmanCastingX.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ScoreGroup
            elif (1012 <= siteNum <= 1021):
                results = PAsiteList.networkScoreGroup.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # TwoTGirls
            elif siteNum == 1022:
                results = PAsiteList.siteTwoTGirls.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Sicflics
            elif siteNum == 1023:
                results = PAsiteList.siteSicflics.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # ModelCentro network
            elif (1024 <= siteNum <= 1039) or siteNum == 1051 or siteNum == 1058:
                results = PAsiteList.networkModelCentro.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Culioneros
            elif (1040 <= siteNum <= 1050):
                results = PAsiteList.siteCulioneros.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # PornWorld
            elif siteNum == 332 or (433 <= siteNum <= 439) or siteNum == 1057:
                results = PAsiteList.networkPornWorld.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # MormonGirlz
            elif siteNum == 1065:
                results = PAsiteList.siteMormonGirlz.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # PurgatoryX
            elif siteNum == 1066:
                results = PAsiteList.sitePurgatoryX.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Plumper Pass
            elif siteNum == 1067:
                results = PAsiteList.sitePlumperPass.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # FTV
            elif (1068 <= siteNum <= 1069):
                results = PAsiteList.networkFTV.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Jacquie & Michel
            elif siteNum == 1070:
                results = PAsiteList.siteJacquieEtMichel.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Data18 Content
            elif siteNum == 1071:
                results = PAsiteList.siteData18Content.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

            # Penthouse Gold
            elif siteNum == 1072:
                results = PAsiteList.sitePenthouseGold.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

        results.Sort('score', descending=True)

    def update(self, metadata, media, lang):
        movieGenres = PAgenres.PhoenixGenres()
        movieActors = PAactors.PhoenixActors()

        HTTP.ClearCache()
        metadata.genres.clear()
        metadata.roles.clear()

        Log('******UPDATE CALLED*******')

        siteNum = int(str(metadata.id).split('|')[1])
        Log(str(siteNum))

        # Blacked
        if siteNum == 1:
            metadata = PAsiteList.networkStrike3.update(metadata, siteNum, movieGenres, movieActors)

        # Blacked Raw
        elif siteNum == 0:
            metadata = PAsiteList.networkStrike3.update(metadata, siteNum, movieGenres, movieActors)

        # Brazzers
        elif siteNum == 2 or (siteNum >= 54 and siteNum <= 81) or siteNum == 582 or siteNum == 690:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # SexyHub
        elif (siteNum >= 333 and siteNum <= 339):
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # FakeHub
        elif siteNum == 340 or (siteNum >= 397 and siteNum <= 407):
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Naughty America
        elif (siteNum >= 5 and siteNum <= 51) or siteNum == 341 or (siteNum >= 393 and siteNum <= 396) or siteNum == 467 or siteNum == 468 or siteNum == 581 or siteNum == 620 or siteNum == 625 or siteNum == 691 or siteNum == 749:
            metadata = PAsiteList.siteNaughtyAmerica.update(metadata, siteNum, movieGenres, movieActors)

        # Vixen
        elif siteNum == 52:
            metadata = PAsiteList.networkStrike3.update(metadata, siteNum, movieGenres, movieActors)

        # X-Art
        elif siteNum == 82:
            metadata = PAsiteList.siteXart.update(metadata, siteNum, movieGenres, movieActors)

        # Bang Bros
        elif siteNum >= 83 and siteNum <= 135:
            metadata = PAsiteList.siteBangBros.update(metadata, siteNum, movieGenres, movieActors)

        # Tushy
        elif siteNum == 136:
            metadata = PAsiteList.networkStrike3.update(metadata, siteNum, movieGenres, movieActors)

        # Reality Kings
        elif (siteNum >= 137 and siteNum <= 182) or (siteNum >= 822 and siteNum <= 828):
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # PornFidelity
        elif siteNum >= 184 and siteNum <= 186:
            metadata = PAsiteList.networkPornFidelity.update(metadata, siteNum, movieGenres, movieActors)

        # TeamSkeet
        elif (187 <= siteNum <= 215) or (566 <= siteNum <= 567) or siteNum == 626 or siteNum == 686 or siteNum == 748 or siteNum == 807 or (845 <= siteNum <= 851) or siteNum == 875 or (997 <= siteNum <= 1011):
            metadata = PAsiteList.networkTeamSkeet.update(metadata, siteNum, movieGenres, movieActors)

        # Porndoe Premium
        elif siteNum >= 216 and siteNum <= 259:
            metadata = PAsiteList.sitePorndoePremium.update(metadata, siteNum, movieGenres, movieActors)

        # LegalPorno
        elif siteNum == 260:
            metadata = PAsiteList.siteLegalPorno.update(metadata, siteNum, movieGenres, movieActors)

        # Mofos
        elif (261 <= siteNum <= 270) or siteNum == 583 or (738 <= siteNum <= 740) or (1059 <= siteNum <= 1064):
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Babes
        elif siteNum >= 271 and siteNum <= 276:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # GloryHoleSecrets
        elif siteNum == 279:
            metadata = PAsiteList.siteGloryHoleSecrets.update(metadata, siteNum, movieGenres, movieActors)

        # NewSensations
        elif siteNum == 280:
            metadata = PAsiteList.siteNewSensations.update(metadata, siteNum, movieGenres, movieActors)

        # Stepped Up Media
        elif siteNum == 767 or (siteNum >= 282 and siteNum <= 284):
            metadata = PAsiteList.networkSteppedUp.update(metadata, siteNum, movieGenres, movieActors)

        # Twistys
        elif siteNum >= 288 and siteNum <= 291 or siteNum == 768:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Spizoo
        elif siteNum == 293 or (siteNum >= 571 and siteNum <= 577):
            metadata = PAsiteList.siteSpizoo.update(metadata, siteNum, movieGenres, movieActors)

        # Private
        elif siteNum >= 294 and siteNum <= 305:
            metadata = PAsiteList.sitePrivate.update(metadata, siteNum, movieGenres, movieActors)

        # PornPros Network
        elif (siteNum >= 306 and siteNum <= 327) or (siteNum >= 479 and siteNum <= 489) or (siteNum == 624) or (siteNum == 769) or (siteNum == 844) or (siteNum == 890):
            metadata = PAsiteList.networkPornPros.update(metadata, siteNum, movieGenres, movieActors)

        # DigitalPlayground
        elif siteNum == 328:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # FullPornNetwork
        elif siteNum >= 343 and siteNum <= 350:
            metadata = PAsiteList.networkFullPornNetwork.update(metadata, siteNum, movieGenres, movieActors)

        # Gamma Entertainment
        elif siteNum == 278 or (siteNum >= 285 and siteNum <= 287) or (siteNum >= 329 and siteNum <= 330) or (siteNum >= 351 and siteNum <= 360) or siteNum == 382 or siteNum == 384 or (siteNum >= 386 and siteNum <= 392) or siteNum == 750 or siteNum == 843 or siteNum == 861:
            metadata = PAsiteList.networkGammaEnt.update(metadata, siteNum, movieGenres, movieActors)

        # Gamma Entertainment Other
        elif siteNum == 53 or siteNum == 183 or siteNum == 277 or siteNum == 281 or (365 <= siteNum <= 379) or siteNum == 381 or siteNum == 383 or siteNum == 385 or (460 <= siteNum <= 466) or siteNum == 692 or siteNum == 793 or (795 <= siteNum <= 797) or siteNum == 878 or siteNum == 893 or siteNum == 975:
            metadata = PAsiteList.networkGammaEntOther.update(metadata, siteNum, movieGenres, movieActors)

        # MileHighMedia
        elif siteNum == 852 or (siteNum >= 361 and siteNum <= 364) or (914 <= siteNum <= 915):
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Dogfart Network
        elif siteNum >= 408 and siteNum <= 431:
            metadata = PAsiteList.networkDogfart.update(metadata, siteNum, movieGenres, movieActors)

        # Jules Jordan
        elif siteNum == 432 or (siteNum >= 522 and siteNum <= 524) or siteNum == 782:
            metadata = PAsiteList.siteJulesJordan.update(metadata, siteNum, movieGenres, movieActors)

        # DDF Network
        elif (siteNum >= 440 and siteNum <= 447):
            metadata = PAsiteList.networkDDFNetwork.update(metadata, siteNum, movieGenres, movieActors)

        # Perfect Gonzo
        elif (448 <= siteNum <= 459) or (908 <= siteNum <= 911):
            metadata = PAsiteList.networkPerfectGonzo.update(metadata, siteNum, movieGenres, movieActors)

        # BadoinkVR Network
        elif siteNum >= 469 and siteNum <= 473:
            metadata = PAsiteList.networkBadoinkVR.update(metadata, siteNum, movieGenres, movieActors)

        # VRBangers
        elif siteNum == 474:
            metadata = PAsiteList.siteVRBangers.update(metadata, siteNum, movieGenres, movieActors)

        # SexBabesVR
        elif siteNum == 475:
            metadata = PAsiteList.networkHighTechVR.update(metadata, siteNum, movieGenres, movieActors)

        # SinsVR
        elif siteNum == 569:
            metadata = PAsiteList.networkHighTechVR.update(metadata, siteNum, movieGenres, movieActors)

        # StasyQ VR
        elif siteNum == 570:
            metadata = PAsiteList.networkHighTechVR.update(metadata, siteNum, movieGenres, movieActors)

        # WankzVR
        elif siteNum == 476:
            metadata = PAsiteList.siteMilfVR.update(metadata, siteNum, movieGenres, movieActors)

        # MilfVR
        elif siteNum == 477:
            metadata = PAsiteList.siteMilfVR.update(metadata, siteNum, movieGenres, movieActors)

        # Joymii
        elif siteNum == 478:
            metadata = PAsiteList.siteJoymii.update(metadata, siteNum, movieGenres, movieActors)

        # Kink
        elif siteNum >= 490 and siteNum <= 521 or siteNum == 687 or siteNum == 735 or siteNum == 736 or (873 <= siteNum <= 875) or (888 <= siteNum <= 889):
            metadata = PAsiteList.networkKink.update(metadata, siteNum, movieGenres, movieActors)

        # Nubiles
        elif (siteNum >= 525 and siteNum <= 545) or (755 <= siteNum <= 756) or (siteNum == 766) or (995 <= siteNum <= 996):
            metadata = PAsiteList.networkNubiles.update(metadata, siteNum, movieGenres, movieActors)

        # BellaPass
        elif siteNum >= 548 and siteNum <= 563:
            metadata = PAsiteList.networkBellaPass.update(metadata, siteNum, movieGenres, movieActors)

        # AllureMedia
        elif siteNum == 564 or siteNum == 565:
            metadata = PAsiteList.siteAllureMedia.update(metadata, siteNum, movieGenres, movieActors)

        # Manyvids
        elif siteNum == 568:
            metadata = PAsiteList.siteManyvids.update(metadata, siteNum, movieGenres, movieActors)

        # VirtualTaboo
        elif siteNum == 292:
            metadata = PAsiteList.siteVirtualTaboo.update(metadata, siteNum, movieGenres, movieActors)

        # VirtualRealPorn
        elif siteNum == 342:
            metadata = PAsiteList.siteVirtualReal.update(metadata, siteNum, movieGenres, movieActors)

        # CzechVR Network
        elif (siteNum >= 578 and siteNum <= 580):
            metadata = PAsiteList.networkCzechVR.update(metadata, siteNum, movieGenres, movieActors)

        # FinishesTheJob
        elif (siteNum >= 584 and siteNum <= 586):
            metadata = PAsiteList.siteFinishesTheJob.update(metadata, siteNum, movieGenres, movieActors)

        # Wankz Network
        elif (siteNum >= 587 and siteNum <= 619):
            metadata = PAsiteList.networkWankz.update(metadata, siteNum, movieGenres, movieActors)

        # Tonights Girlfriend
        elif siteNum == 627:
            metadata = PAsiteList.siteTonightsGirlfriend.update(metadata, siteNum, movieGenres, movieActors)

        # Karups
        elif (siteNum >= 628 and siteNum <= 630):
            metadata = PAsiteList.siteKarups.update(metadata, siteNum, movieGenres, movieActors)

        # TeenMegaWorld
        elif (siteNum >= 631 and siteNum <= 666) or siteNum == 930:
            metadata = PAsiteList.networkTeenMegaWorld.update(metadata, siteNum, movieGenres, movieActors)

        # ScrewBox
        elif siteNum == 668:
            metadata = PAsiteList.siteScrewbox.update(metadata, siteNum, movieGenres, movieActors)

        # DorcelClub
        elif siteNum == 669:
            metadata = PAsiteList.siteDorcelClub.update(metadata, siteNum, movieGenres, movieActors)

        # TushyRaw
        elif siteNum == 670:
            metadata = PAsiteList.networkStrike3.update(metadata, siteNum, movieGenres, movieActors)

        # Deeper
        elif siteNum == 671:
            metadata = PAsiteList.networkStrike3.update(metadata, siteNum, movieGenres, movieActors)

        # MissaX / AllHerLuv
        elif siteNum == 672 or siteNum == 673:
            metadata = PAsiteList.siteMissaX.update(metadata, siteNum, movieGenres, movieActors)

        # Mylf
        elif (siteNum >= 674 and siteNum <= 683) or siteNum == 757 or siteNum == 842 or (siteNum >= 853 and siteNum <= 858) or (881 <= siteNum <= 887):
            metadata = PAsiteList.siteMylf.update(metadata, siteNum, movieGenres, movieActors)

        # Manually Add Actors
        elif siteNum == 684:
            metadata = PAsiteList.addActors.update(metadata, siteNum, movieGenres, movieActors)

        # First Anal Quest
        elif siteNum == 685:
            metadata = PAsiteList.siteFirstAnalQuest.update(metadata, siteNum, movieGenres, movieActors)

        # Hegre
        elif siteNum == 688:
            metadata = PAsiteList.siteHegre.update(metadata, siteNum, movieGenres, movieActors)

        # FemdomEmpire
        elif siteNum == 689 or siteNum == 694:
            metadata = PAsiteList.networkFemdomEmpire.update(metadata, siteNum, movieGenres, movieActors)

        # DorcelVision
        elif siteNum == 693:
            metadata = PAsiteList.siteDorcelVision.update(metadata, siteNum, movieGenres, movieActors)

        # XConfessions
        elif siteNum == 695:
            metadata = PAsiteList.siteXConfessions.update(metadata, siteNum, movieGenres, movieActors)

        # Czech AV
        elif (siteNum >= 696 and siteNum <= 728):
            metadata = PAsiteList.networkCzechAV.update(metadata, siteNum, movieGenres, movieActors)

        # ArchAngel
        elif siteNum == 729:
            metadata = PAsiteList.siteArchAngel.update(metadata, siteNum, movieGenres, movieActors)

        # We Are Hairy
        elif siteNum == 730:
            metadata = PAsiteList.siteWeAreHairy.update(metadata, siteNum, movieGenres, movieActors)

        # Love Her Feet
        elif siteNum == 731:
            metadata = PAsiteList.siteLoveHerFeet.update(metadata, siteNum, movieGenres, movieActors)

        # MomPOV
        elif siteNum == 732:
            metadata = PAsiteList.siteMomPOV.update(metadata, siteNum, movieGenres, movieActors)

        # Property Sex
        elif siteNum == 733:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # FuelVirtual
        elif (546 <= siteNum <= 547):
            metadata = PAsiteList.networkFuelVirtual.update(metadata, siteNum, movieGenres, movieActors)

        # TransAngels
        elif siteNum == 737:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Straplezz
        elif siteNum == 741:
            metadata = PAsiteList.siteStraplezz.update(metadata, siteNum, movieGenres, movieActors)

        # LittleCaprice
        elif siteNum == 742:
            metadata = PAsiteList.siteLittleCaprice.update(metadata, siteNum, movieGenres, movieActors)

        # WowGirls
        elif siteNum == 743:
            metadata = PAsiteList.siteWowGirls.update(metadata, siteNum, movieGenres, movieActors)

        # VIPissy
        elif siteNum == 744:
            metadata = PAsiteList.siteVIPissy.update(metadata, siteNum, movieGenres, movieActors)

        # GirlsOutWest
        elif siteNum == 745:
            metadata = PAsiteList.siteGirlsOutWest.update(metadata, siteNum, movieGenres, movieActors)

        # Girls Rimming
        elif siteNum == 746:
            metadata = PAsiteList.siteGirlsRimming.update(metadata, siteNum, movieGenres, movieActors)

        # Gangbang Creampie
        elif siteNum == 747:
            metadata = PAsiteList.siteGangbangCreampie.update(metadata, siteNum, movieGenres, movieActors)

        # StepSecrets
        elif siteNum == 751:
            metadata = PAsiteList.siteStepSecrets.update(metadata, siteNum, movieGenres, movieActors)

        # VRHush
        elif siteNum == 752:
            metadata = PAsiteList.siteVRHush.update(metadata, siteNum, movieGenres, movieActors)

        # MetArt Network
        elif (621 <= siteNum <= 623) or (753 <= siteNum <= 754) or (816 <= siteNum <= 821):
            metadata = PAsiteList.networkMetArt.update(metadata, siteNum, movieGenres, movieActors)

        # Fitting-Room
        elif siteNum == 758:
            metadata = PAsiteList.siteFittingRoom.update(metadata, siteNum, movieGenres, movieActors)

        # FamilyHookups
        elif siteNum == 759:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Clips4Sale
        elif siteNum == 760:
            metadata = PAsiteList.siteClips4Sale.update(metadata, siteNum, movieGenres, movieActors)

        # VogoV
        elif siteNum == 761:
            metadata = PAsiteList.siteVogoV.update(metadata, siteNum, movieGenres, movieActors)

        # Ultrafilms
        elif siteNum == 762:
            metadata = PAsiteList.siteUltrafilms.update(metadata, siteNum, movieGenres, movieActors)

        # fuckingawesome.com
        elif siteNum == 763:
            metadata = PAsiteList.siteFuckingAwesome.update(metadata, siteNum, movieGenres, movieActors)

        # ToughLoveX
        elif siteNum == 764:
            metadata = PAsiteList.siteToughLoveX.update(metadata, siteNum, movieGenres, movieActors)

        # cumlouder.com
        elif siteNum == 765:
            metadata = PAsiteList.siteCumLouder.update(metadata, siteNum, movieGenres, movieActors)

        # ztod.com
        elif siteNum == 770:
            metadata = PAsiteList.siteZTOD.update(metadata, siteNum, movieGenres, movieActors)

        # ClubFilly
        elif siteNum == 771:
            metadata = PAsiteList.siteClubFilly.update(metadata, siteNum, movieGenres, movieActors)

        # Intersec
        elif (siteNum >= 772 and siteNum <= 781):
            metadata = PAsiteList.networkIntersec.update(metadata, siteNum, movieGenres, movieActors)

        # Cherry Pimps
        elif (siteNum >= 783 and siteNum <= 792) or (siteNum >= 1052 and siteNum <= 1056):
            metadata = PAsiteList.networkCherryPimps.update(metadata, siteNum, movieGenres, movieActors)

        # 18OnlyGirls
        elif siteNum == 794:
            metadata = PAsiteList.site18OnlyGirls.update(metadata, siteNum, movieGenres, movieActors)

        # Lil Humpers
        elif siteNum == 798:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # BellesaFilms
        elif siteNum == 799 or siteNum == 876:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # ClubSeventeen
        elif siteNum == 800:
            metadata = PAsiteList.siteClubSeventeen.update(metadata, siteNum, movieGenres, movieActors)

        # Elegant Angel
        elif siteNum == 801:
            metadata = PAsiteList.siteElegantAngel.update(metadata, siteNum, movieGenres, movieActors)

        # Family Sinners
        elif siteNum == 802:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # ReidMyLips
        elif siteNum == 803:
            metadata = PAsiteList.siteReidMyLips.update(metadata, siteNum, movieGenres, movieActors)

        # Playboy Plus
        elif siteNum == 804:
            metadata = PAsiteList.sitePlayboyPlus.update(metadata, siteNum, movieGenres, movieActors)

        # Meana Wolf
        elif siteNum == 805:
            metadata = PAsiteList.siteMeanaWolf.update(metadata, siteNum, movieGenres, movieActors)

        # Transsensual
        elif siteNum == 806:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Erito
        elif siteNum == 808:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # TrueAmateurs
        elif siteNum == 809:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Hustler
        elif siteNum == 810:
            metadata = PAsiteList.networkMetArt.update(metadata, siteNum, movieGenres, movieActors)

        # AmourAngels
        elif siteNum == 811:
            metadata = PAsiteList.siteAmourAngels.update(metadata, siteNum, movieGenres, movieActors)

        # JAV
        elif siteNum == 812:
            metadata = PAsiteList.networkR18.update(metadata, siteNum, movieGenres, movieActors)

        # Bang
        elif siteNum == 813:
            metadata = PAsiteList.networkBang.update(metadata, siteNum, movieGenres, movieActors)

        # Vivid
        elif siteNum == 814:
            metadata = PAsiteList.siteVivid.update(metadata, siteNum, movieGenres, movieActors)

        # JAY's POV
        elif siteNum == 815:
            metadata = PAsiteList.siteJaysPOV.update(metadata, siteNum, movieGenres, movieActors)

        # Girlfriends Films
        elif siteNum == 380:
            metadata = PAsiteList.networkGammaEntOther.update(metadata, siteNum, movieGenres, movieActors)

        # PJGirls
        elif siteNum == 667:
            metadata = PAsiteList.sitePJGirls.update(metadata, siteNum, movieGenres, movieActors)

        # PureCFNM Network
        elif siteNum >= 829 and siteNum <= 834:
            metadata = PAsiteList.networkPureCFNM.update(metadata, siteNum, movieGenres, movieActors)

        # BAMVisions
        elif siteNum == 835:
            metadata = PAsiteList.siteBAMVisions.update(metadata, siteNum, movieGenres, movieActors)

        # ATK Girlfriends
        elif siteNum == 836:
            metadata = PAsiteList.siteATKGirlfriends.update(metadata, siteNum, movieGenres, movieActors)

        # TwoWebMedia
        elif (837 <= siteNum <= 839):
            metadata = PAsiteList.networkTwoWebMedia.update(metadata, siteNum, movieGenres, movieActors)

        # Interracial Pass
        elif siteNum == 840:
            metadata = PAsiteList.siteInterracialPass.update(metadata, siteNum, movieGenres, movieActors)

        # LookAtHerNow
        elif siteNum == 841:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # Deviant Hardcore
        elif siteNum == 859:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # She Will Cheat
        elif siteNum == 860:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # SinsLife
        elif siteNum == 862:
            metadata = PAsiteList.siteSinsLife.update(metadata, siteNum, movieGenres, movieActors)

        # Puffy Network
        elif siteNum == 863 or (siteNum >= 867 and siteNum <= 870):
            metadata = PAsiteList.networkPuffy.update(metadata, siteNum, movieGenres, movieActors)

        # SinX
        elif siteNum == 871 or (siteNum >= 864 and siteNum <= 866):
            metadata = PAsiteList.networkSinX.update(metadata, siteNum, movieGenres, movieActors)

        # Kinky Spa
        elif siteNum == 872:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # RealityLovers
        elif siteNum == 877:
            metadata = PAsiteList.siteRealityLovers.update(metadata, siteNum, movieGenres, movieActors)

        # RealJamVR
        elif siteNum == 879:
            metadata = PAsiteList.networkHighTechVR.update(metadata, siteNum, movieGenres, movieActors)

        # BBC Paradise
        elif siteNum == 880:
            metadata = PAsiteList.siteMylf.update(metadata, siteNum, movieGenres, movieActors)

        # HoloGirlsVR
        elif siteNum == 891:
            metadata = PAsiteList.siteHoloGirlsVR.update(metadata, siteNum, movieGenres, movieActors)

        # LethalHardcoreVR
        elif siteNum == 892:
            metadata = PAsiteList.siteLethalHardcoreVR.update(metadata, siteNum, movieGenres, movieActors)

        # WhoreCraftVR
        elif siteNum == 894:
            metadata = PAsiteList.siteLethalHardcoreVR.update(metadata, siteNum, movieGenres, movieActors)

        # Defeated
        elif siteNum == 895 or siteNum == 896:
            metadata = PAsiteList.siteDefeated.update(metadata, siteNum, movieGenres, movieActors)

        # XVirtual
        elif siteNum == 897:
            metadata = PAsiteList.siteXVirtual.update(metadata, siteNum, movieGenres, movieActors)

        # Lust Reality
        elif siteNum == 898:
            metadata = PAsiteList.siteLustReality.update(metadata, siteNum, movieGenres, movieActors)

        # Sex Like Real
        elif siteNum == 899:
            metadata = PAsiteList.siteSexLikeReal.update(metadata, siteNum, movieGenres, movieActors)

        # DoeGirls
        elif siteNum == 900:
            metadata = PAsiteList.sitePorndoePremium.update(metadata, siteNum, movieGenres, movieActors)

        # Xillimite
        elif siteNum == 901:
            metadata = PAsiteList.siteXillimite.update(metadata, siteNum, movieGenres, movieActors)

        # VRPFilms
        elif siteNum == 902:
            metadata = PAsiteList.siteVRPFilms.update(metadata, siteNum, movieGenres, movieActors)

        # VRLatina
        elif siteNum == 903:
            metadata = PAsiteList.siteVRLatina.update(metadata, siteNum, movieGenres, movieActors)

        # VRConk
        elif siteNum == 904:
            metadata = PAsiteList.siteVRConk.update(metadata, siteNum, movieGenres, movieActors)

        # RealJamVR
        elif siteNum == 905:
            metadata = PAsiteList.networkHighTechVR.update(metadata, siteNum, movieGenres, movieActors)

        # Evolved Fights Network
        elif siteNum == 906 or siteNum == 907:
            metadata = PAsiteList.networkEvolvedFights.update(metadata, siteNum, movieGenres, movieActors)

        # JavBus
        elif siteNum == 912:
            metadata = PAsiteList.networkJavBus.update(metadata, siteNum, movieGenres, movieActors)

        # Hucows
        elif siteNum == 913:
            metadata = PAsiteList.siteHucows.update(metadata, siteNum, movieGenres, movieActors)

        # Why Not Bi
        elif siteNum == 916:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # HentaiPros
        elif siteNum == 917:
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # PornPortal
        elif (918 <= siteNum <= 929):
            metadata = PAsiteList.network1service.update(metadata, siteNum, movieGenres, movieActors)

        # AllAnalAllTheTime
        elif siteNum == 931:
            metadata = PAsiteList.siteAllAnalAllTheTime.update(metadata, siteNum, movieGenres, movieActors)

        # QueenSnake
        elif siteNum == 932:
            metadata = PAsiteList.siteQueenSnake.update(metadata, siteNum, movieGenres, movieActors)

        # QueenSect
        elif siteNum == 933:
            metadata = PAsiteList.siteQueenSnake.update(metadata, siteNum, movieGenres, movieActors)

        # Fetish Network
        elif (934 <= siteNum <= 937):
            metadata = PAsiteList.networkKink.update(metadata, siteNum, movieGenres, movieActors)

        # ScrewMeToo
        elif siteNum == 938:
            metadata = PAsiteList.siteScrewMeToo.update(metadata, siteNum, movieGenres, movieActors)

        # Box Truck Sex
        elif siteNum == 939:
            metadata = PAsiteList.siteBoxTruckSex.update(metadata, siteNum, movieGenres, movieActors)

        # AussieAss
        elif siteNum == 940:
            metadata = PAsiteList.siteAussieAss.update(metadata, siteNum, movieGenres, movieActors)

        # 5Kporn
        elif (941 <= siteNum <= 942):
            metadata = PAsiteList.network5Kporn.update(metadata, siteNum, movieGenres, movieActors)

        # Teen Core Club
        elif (943 <= siteNum <= 974):
            metadata = PAsiteList.networkTeenCoreClub.update(metadata, siteNum, movieGenres, movieActors)

        # Exploited X
        elif (976 <= siteNum <= 978):
            results = PAsiteList.networkExploitedX.update(metadata, siteNum, movieGenres, movieActors)

        # Desperate Amateurs
        elif (siteNum == 979):
            results = PAsiteList.siteDesperateAmateurs.update(metadata, siteNum, movieGenres, movieActors)

        # Dirty Hard Drive
        elif (980 <= siteNum <= 987):
            results = PAsiteList.networkDirtyHardDrive.update(metadata, siteNum, movieGenres, movieActors)

        # Melone Challenge
        elif (siteNum == 988):
            results = PAsiteList.siteMeloneChallenge.update(metadata, siteNum, movieGenres, movieActors)

        # Holly Randall
        elif siteNum == 989:
            results = PAsiteList.siteHollyRandall.update(metadata, siteNum, movieGenres, movieActors)

        # In The Crack
        elif siteNum == 990:
            results = PAsiteList.siteInTheCrack.update(metadata, siteNum, movieGenres, movieActors)

        # Angela White
        elif siteNum == 991:
            results = PAsiteList.siteAngelaWhite.update(metadata, siteNum, movieGenres, movieActors)

        # Cumbizz
        elif siteNum == 992:
            results = PAsiteList.siteCumbizz.update(metadata, siteNum, movieGenres, movieActors)

        # Pornstar Platinum
        elif siteNum == 993:
            results = PAsiteList.sitePornstarPlatinum.update(metadata, siteNum, movieGenres, movieActors)

        # Woodman Casting X
        elif siteNum == 994:
            results = PAsiteList.siteWoodmanCastingX.update(metadata, siteNum, movieGenres, movieActors)

        # ScoreGroup
        elif (1012 <= siteNum <= 1021):
            results = PAsiteList.networkScoreGroup.update(metadata, siteNum, movieGenres, movieActors)

        # TwoTGirls
        elif siteNum == 1022:
            results = PAsiteList.siteTwoTGirls.update(metadata, siteNum, movieGenres, movieActors)

        # Sicflics
        elif siteNum == 1023:
            results = PAsiteList.siteSicflics.update(metadata, siteNum, movieGenres, movieActors)

        # ModelCentro network
        elif (1024 <= siteNum <= 1039) or siteNum == 1051 or siteNum == 1058:
            results = PAsiteList.networkModelCentro.update(metadata, siteNum, movieGenres, movieActors)

        # Culioneros
        elif (1040 <= siteNum <= 1050):
            results = PAsiteList.siteCulioneros.update(metadata, siteNum, movieGenres, movieActors)

        # PornWorld
        elif siteNum == 332 or (433 <= siteNum <= 439) or siteNum == 1057:
            results = PAsiteList.networkPornWorld.update(metadata, siteNum, movieGenres, movieActors)

        # MormonGirlz
        elif siteNum == 1065:
            metadata = PAsiteList.siteMormonGirlz.update(metadata, siteNum, movieGenres, movieActors)

        # PurgatoryX
        elif siteNum == 1066:
            metadata = PAsiteList.sitePurgatoryX.update(metadata, siteNum, movieGenres, movieActors)

        # Plumper Pass
        elif siteNum == 1067:
            metadata = PAsiteList.sitePlumperPass.update(metadata, siteNum, movieGenres, movieActors)

        # FTV
        elif (1068 <= siteNum <= 1069):
            metadata = PAsiteList.networkFTV.update(metadata, siteNum, movieGenres, movieActors)

        # Jacquie & Michel
        elif siteNum == 1070:
            metadata = PAsiteList.siteJacquieEtMichel.update(metadata, siteNum, movieGenres, movieActors)

        # Data18 Content
        elif siteNum == 1071:
            metadata = PAsiteList.siteData18Content.update(metadata, siteNum, movieGenres, movieActors)

        # Penthouse Gold
        elif siteNum == 1072:
            metadata = PAsiteList.sitePenthouseGold.update(metadata, siteNum, movieGenres, movieActors)

        # Cleanup Genres and Add
        Log('Genres')
        movieGenres.processGenres(metadata)
        metadata.genres = sorted(metadata.genres)

        # Cleanup Actors and Add
        Log('Actors')
        movieActors.processActors(metadata)

        # Add Content Rating
        metadata.content_rating = 'XXX'
