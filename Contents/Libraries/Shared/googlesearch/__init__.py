"""googlesearch is a Python library for searching Google, easily."""

from time import sleep
try:
    from bs4 import BeautifulSoup
    is_bs4 = True
except ImportError:
    from BeautifulSoup import BeautifulSoup
    is_bs4 = False
from requests import get
from .user_agents import get_useragent
from urllib import quote_plus


def req(query, url, results, lang, tbs, start, proxies, timeout):
    resp = get(
        url='https://www.google.com/search?tbs=%s' % tbs,
        headers={
            'User-Agent': get_useragent()
        },
        params={
            'q': query,
            'num': results + 2,  # Prevents multiple requests
            'hl': lang,
            'start': start,
            'safe': 'off',
            'as_sitesearch': url,
        },
        proxies=proxies,
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return 'SearchResult(url={url})'.format(url=self.url)


def search(searchQuery, site, num_results=10, lang='en', tbs='', proxy=None, sleep_interval=0, timeout=5):
    """Search the Google search engine"""

    # Proxy
    proxies = None
    if proxy:
        if proxy.startswith('https'):
            proxies = {'https': proxy}
        else:
            proxies = {'http': proxy}

    # Fetch
    start = 0
    while start < num_results:
        # Send request
        resp = req(searchQuery, site, num_results - start,
                    lang, tbs, start, proxies, timeout)

        # Parse
        if is_bs4:
            soup = BeautifulSoup(resp.text, 'html.parser')
        else:
            soup = BeautifulSoup(resp.text)

        result_block = soup.findAll('div', attrs={'class': 'yuRUbf'})

        if len(result_block) == 0:
            start += 1

        for result in result_block:
            # Find link
            link = result.find('a', href=True)
            if link:
                start += 1
                yield link['href']

        sleep(sleep_interval)

        if start == 0:
            return
