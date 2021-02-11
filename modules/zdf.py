from bs4 import BeautifulSoup as bs
import requests as r

class Provider:
    version = "1.0"
    h = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'LOL I AM PYTHON'
    }
    prä = "[ZDF]"

    def getConfig(self):
        return []

    def setConfig(self, config_map):
        return True

    def getUrlsByTag(self, tag, value):
        """ coordinates tag handling

        Args:
            tag (string): the tag
            value (string): the value of the tag

        Returns:
            array: array with all urls to donwload
        """
        if tag == "overview.new":
            try:
                urls = self._getUrlsByDiv(value, "cluster-showmore")
            except ValueError as e:
                print(f"{self.prä} Invalid page content: {e}")
                return False
            except Exception as e:
                print(f"{self.prä} Could not load page. Make sure you are connected to the internet and the provided url was correct. {e}")
                return []
            return urls
        elif tag == "overview.teaser":
            try:
                urls = self._getUrlsByDiv(value, "teaser-block-grid-container")
            except ValueError as e:
                print(f"{self.prä} Invalid page content: {e}")
                return []
            except Exception as e:
                print(f"{self.prä} Could not load page. Make sure you are connected to the internet and the provided url was correct. {e}")
                return []
            return urls
        elif tag == "category":
            try:
                urls = self._getUrlsByDiv(value, "cluster-showmore")
            except ValueError as e:
                print(f"{self.prä} Invalid page content: {e}")
                return []
            except Exception as e:
                print(f"{self.prä} Could not load page. Make sure you are connected to the internet and the provided url was correct. {e}")
                return []
            return urls


        else:
            return []
            
    def _getUrlsByDiv(self, url, divclass):
        try:
            req = r.get(url, self.h)
            content = bs(req.content, 'html.parser')
        except Exception as e:
            raise Exception("Can not find url.")

        div = content.findAll('div', {"class":divclass})
        if len(div) < 1:
            raise ValueError("There is no div {divclass}.") 

        return self._getAllLinks(div[0])

    def _getAllLinks(self, content):
        ret = []
        links = content.findAll('a')
        for l in links:
            try:
                ret.append("https://zdf.de"+l.get('href'))
            except Exception as e:
                raise ValueError("There is no link.")

        return ret