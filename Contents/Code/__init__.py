import os
import re
import random
import requests
import urllib
import urlparse
import json
import shutil
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

    dateNowObj = datetime.now()
    debug_dir = 'debug_data/'
    if os.path.exists(debug_dir):
        for directoryName in os.listdir(debug_dir):
            debugDateObj = parse(directoryName)
            if abs((dateNowObj - debugDateObj).days) > 3:
                debugLogs = debug_dir + directoryName
                shutil.rmtree(debugLogs)
                Log('Deleted debug data: %s' % directoryName)


class PhoenixAdultAgent(Agent.Movies):
    name = 'PhoenixAdult'
    languages = [Locale.Language.English]
    accepts_from = ['com.plexapp.agents.localmedia', 'com.plexapp.agents.lambda']
    primary_provider = True

    def search(self, results, media, lang):
        if media.primary_metadata is not None:
            title = media.primary_metadata.studio + ' ' + media.primary_metadata.title
        elif Prefs['strip_enable']:
            title = media.name.split(Prefs['strip_symbol'], 1)[0]
        else:
            title = media.name

        trashTitle = (
            'RARBG', 'COM', r'\d{3,4}x\d{3,4}', 'HEVC', 'H265', 'AVC', r'\dK',
            r'\d{3,4}p', 'TOWN.AG_', 'XXX', 'MP4', 'KLEENEX', 'SD', 'HD',
            'ForeverAloneDude'
        )

        title = self.getSearchTitle(title)

        Log('*******MEDIA TITLE****** %s' % title)

        searchSettings = PAsearchSites.getSearchSettings(title)

        if searchSettings[0] is None and media.filename:
            filename = urllib.unquote(media.filename)
            # unable to identify a studio from the given string,
            # try to get a site match from the parent directory name
            path = filename[1:] if filename[0] == '/' else filename
            pathComponents = path.strip().split('/')
            if len(pathComponents) >= 2:
                # we have a path
                parent = pathComponents[-2]
                parentWords = ' '.join(re.split(r'[^A-Za-z0-9]+', parent))
                parentTitle = self.getSearchTitle(parentWords)
                searchSettings = PAsearchSites.getSearchSettings(parentTitle)

                if searchSettings[0] is not None and searchSettings[1].lower() == PAsearchSites.getSearchSiteName(searchSettings[0]).lower():
                    # maybe the parent directory name contained just the studio name?
                    # try to search for the parent directory name and the file name
                    parentTitlePlusTitle = '%s %s' % (parentTitle, title)
                    searchSettings = PAsearchSites.getSearchSettings(parentTitlePlusTitle)

        siteNum = searchSettings[0]
        searchTitle = searchSettings[1]
        searchDate = searchSettings[2]

        if siteNum is not None:
            Log('Search Title: %s' % searchTitle)
            if searchDate:
                Log('Search Date: %s' % searchDate)

            encodedTitle = urllib.quote(searchTitle)
            Log('Encoded title: %s' % encodedTitle)

            provider = PAsiteList.getProviderFromSiteNum(siteNum)
            if provider is not None:
                provider.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate, media)

        results.Sort('score', descending=True)

    def getSearchTitle(self, title):
        trashTitle = (
            'RARBG', 'COM', r'\d{3,4}x\d{3,4}', 'HEVC', 'H265', 'AVC', r'\dK',
            r'\d{3,4}p', 'TOWN.AG_', 'XXX', 'MP4', 'KLEENEX', 'SD', 'HD',
            'KTR', 'IEVA', 'WRB', 'NBQ', 'ForeverAloneDude',
        )

        for trash in trashTitle:
            title = re.sub(r'\b%s\b' % trash, '', title, flags=re.IGNORECASE)

        return ' '.join(title.split())

    def update(self, metadata, media, lang):
        movieGenres = PAgenres.PhoenixGenres()
        movieActors = PAactors.PhoenixActors()

        HTTP.ClearCache()
        metadata.genres.clear()
        metadata.roles.clear()

        Log('******UPDATE CALLED*******')

        metadata_id = str(metadata.id).split('|')
        siteNum = int(metadata_id[1])
        Log(str(siteNum))

        provider = PAsiteList.getProviderFromSiteNum(siteNum)
        if provider is not None:
            provider.update(metadata, siteNum, movieGenres, movieActors)

        # Cleanup Genres and Add
        Log('Genres')
        movieGenres.processGenres(metadata)
        metadata.genres = sorted(metadata.genres)

        # Cleanup Actors and Add
        Log('Actors')
        movieActors.processActors(metadata)

        # Add Content Rating
        metadata.content_rating = 'XXX'
