import urllib, json
import requests as r

class Provider:
    version = "1.0" 
    h = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    }
    prä = "[ARTE]" # You can use this for debugging messages

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
                urls = self._searchApi(value)
            except ValueError as e:
                print(f"{self.prä} Invalid page content: {e}")
                return []
            except Exception as e:
                print(f"{self.prä} Could not load page. Make sure you are connected to the internet and the provided url was correct. {e}")
                return []
            return urls
        else:
            return [] # make sure to always return at least an empty list
            
    def _searchApi(self, keyword):
        urls = []
        url="https://www.arte.tv/guide/api/emac/v3/de/web/pages/SEARCH/?mainZonePage=1&query=" + urllib.parse.quote_plus(keyword)

        try:
            req = r.get(url, self.h)
        except Exception as e:
            raise Exception("Can not access arte search api.")

        try:
            data = json.loads(req.content)
            video_list = data["zones"][0]["data"]
        except:
            raise ValueError("Can not parse content.")

        for v in video_list:
            urls.append(v["url"])

        i = 1
        tot = len(urls)
        for url in urls:
            print(f"{self.prä} Checking url {i}/{tot}")
            try:
                req = r.get(url)
                if not "program-player" in str(req.content):
                    urls.remove(url)
            except Exception as e:
                print(f"{self.prä} Could not open {url} due to: {e}")

            i+=1

        return urls

