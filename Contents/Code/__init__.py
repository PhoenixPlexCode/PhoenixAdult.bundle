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

        for trash in trashTitle:
            title = re.sub(r'\b%s\b' % trash, '', title, flags=re.IGNORECASE)
        title = ' '.join(title.split())

        Log('*******MEDIA TITLE****** %s' % title)

        Log('Getting Search Settings for: %s' % title)
        searchSettings = PAsearchSites.getSearchSettings(title)
        siteNum = searchSettings[0]
        searchTitle = searchSettings[1]
        searchDate = searchSettings[2]

        if siteNum is not None:
            Log('Search Title: %s' % searchTitle)
            if searchDate:
                Log('Search Date: %s' % searchDate)

            encodedTitle = urllib.quote(searchTitle)
            Log(encodedTitle)

            provider = PAsiteList.getProviderFromSiteNum(siteNum)
            if provider is not None:
                provider.search(results, encodedTitle, searchTitle, siteNum, lang, searchDate)

        results.Sort('score', descending=True)

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
