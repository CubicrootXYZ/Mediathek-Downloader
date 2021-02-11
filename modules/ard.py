# You might want to import modules here, e.g. bs4 for extracting urls from webpages
from bs4 import BeautifulSoup as bs
import requests as r
import json, urllib

class Provider:
    version = "1.0"
    h = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'LOL I AM PYTHON'
    }

    prä = "[ARD]" # You can use this for debugging messages

    def getConfig(self):
        return []

    def setConfig(self, config_map):
        return True


    def getUrlsByTag(self, tag, value): # <-- this method will be called from the downloader
        """ coordinates tag handling

        Args:
            tag (string): the tag
            value (string): the value of the tag

        Returns:
            array: array with all urls to donwload
        """

        if tag == "search":
            try:
                urls = self._getUrlsBySearch(value)
            except Exception as e:
                print(f"{self.prä} Could not load page. Make sure you are connected to the internet and the provided url was correct. {e}")
                return []
            return urls
        else:
            return [] # make sure to always return at least an empty list
            
    def _getUrlsBySearch(self, keyword):
        urls = []
        url="https://www.ardmediathek.de/ard/suche/" + urllib.parse.quote_plus(keyword) + "/"

        try:
            req = r.get(url, self.h)
        except Exception as e:
            raise Exception("Can not access ARD search endpoint.")

        try:
            data = bs(req.content, 'html.parser')
            sections = data.findAll('section')
            section = sections[1]
            sections = section.findAll('section')
            section = sections[1]
        except Exception as e:
            raise ValueError(f"Can not parse content: {e}")

        for s in section:
            urls += self._getAllLinks(s)

        if len(urls) < 1:
            print(f"{self.prä} No videos found.")
            return []

        i = 1
        tot = len(urls)
        final_urls = []
        for url in urls:
            print(f"{self.prä} Checking url {i}/{tot}")
            try:
                req = r.get(url)
                if "FixedContainer" in str(req.content):
                    final_urls.append(url)
            except Exception as e:
                print(f"{self.prä} Could not open {url} due to: {e}")

            i+=1

        return final_urls

    def _getAllLinks(self, content):
        ret = []
        links = content.findAll('a')
        for l in links:
            try:
                ret.append("https://www.ardmediathek.de"+l.get('href'))
            except Exception as e:
                raise ValueError("There is no link.")

        return ret