import unittest, datetime, time
from run import Downloader, Timer
import timeout_decorator

class TestDownloader(unittest.TestCase):
    
    def setUp(self):
        # get instance
        self.downloader = Downloader()
        self.downloader.test_mode = True

    def test_init(self):
        # check if config is set
        self.assertTrue(isinstance(self.downloader.config, dict))

    def test_getVideoProvider(self):
        # check if example provider is loaded 
        self.assertTrue(self.downloader.getVideoProvider("example_provider"))

    def test_loadJobs(self):
        self.downloader.loadJobs()
        #check if there is at least one job loaded
        self.assertTrue("name" in self.downloader.jobs[0])

    #@unittest.SkipTest # needs very long
    def test_runJobs(self):
        self.downloader.jobs = [{
            "name": "Test",
            "shortname": "test",
            "provider": "example_provider",
            "tag": "test.youtube",
            "tagvalue": "nothing",
            "days_back": 1000,
            "type": "series",
            "category": "TVshows"
        }]
        # check if the example job is executed
        self.assertTrue(self.downloader.runJobs())

class TestZdf(unittest.TestCase):

    provider = None

    def setUp(self):
        try:
            from modules import zdf
            self.provider = zdf.Provider()
        except:
            pass

    def test_moduleAvailable(self):
        try:
            from modules import zdf
            self.provider = zdf.Provider()
        except:
            self.assertTrue(False)
        self.assertTrue(True)

    def test_tags(self):
        if self.provider is None:
            self.assertTrue(False)

        urls_category = self.provider.getUrlsByTag("category", "https://www.zdf.de/doku-wissen")

        self.assertTrue(len(urls_category) > 0)

        urls_overview1 = self.provider.getUrlsByTag("overview.teaser", "https://www.zdf.de/comedy/heute-show")

        self.assertTrue(len(urls_overview1) > 0)

        urls_overview2 = self.provider.getUrlsByTag("overview.new", "https://www.zdf.de/comedy/heute-show")

        self.assertTrue(len(urls_overview1) > 0)

class TestArd(unittest.TestCase):

    def setUp(self):
        try:
            from modules import ard
            self.provider = ard.Provider()
        except:
            pass

    def test_moduleAvailable(self):
        try:
            from modules import ard
            self.provider = ard.Provider()
        except:
            self.assertTrue(False)
        self.assertTrue(True)

    def test_tags(self):
        if self.provider is None:
            self.assertTrue(False)

        urls_search = self.provider.getUrlsByTag("search", "Wunder")

        self.assertTrue(len(urls_search) > 0)

class TestTimer(unittest.TestCase):
    
    def setUp(self):
        self.timer = Timer()
        self.timer.testing = True

    @timeout_decorator.timeout(180)
    def test_timer(self):
        now = datetime.datetime.now()+datetime.timedelta(minutes=1)
        then = now+datetime.timedelta(minutes=1)
        self.timer.runtimes = [now.strftime("%H:%M"), then.strftime("%H:%M"), ]
        

        self.assertEqual(self.timer.run(), 2)
    


if __name__ == '__main__':
    unittest.main()
