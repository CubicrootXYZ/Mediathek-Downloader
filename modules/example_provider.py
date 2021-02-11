# You might want to import modules here, e.g. bs4 for extracting urls from webpages

class Provider:
    version = "1.0" # Version is required!!!

    prä = "[PROVIDER-EXAMPLE]" # You can use this for debugging messages

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

        if tag == "overview.new":
            try:
                urls = self.loadUrls() # I highly recommend just calling another method here, as it will get messy otherwise
            except Exception as e:
                print(f"{self.prä} Could not load page. Make sure you are connected to the internet and the provided url was correct. {e}")
                return []
            return urls
        elif tag == "test.youtube":
            try:
                urls = self.loadOtherUrls()
            except Exception as e:
                print(f"{self.prä} Could not load page. Make sure you are connected to the internet and the provided url was correct. {e}")
                return []
            return urls
        else:
            return [] # make sure to always return at least an empty list
            
    def loadUrls(self):
        return ['www.example.com/urltovideo']

    def loadOtherUrls(self):
        return ['https://www.youtube.com/watch?v=kt0g4dWxEBo']