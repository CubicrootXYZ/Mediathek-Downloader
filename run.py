from __future__ import unicode_literals
import youtube_dl
import os, importlib, yaml, glob, fnmatch, datetime, time, re, string
import importlib.machinery
from pathlib import Path

os.chdir("/opt/app")

class Downloader:
    """orchestrates downloads via youtube dl

    """

    prä = "[DOWNLOADER]"
    tag_to_provider = {
        "zdf": "zdf"
    }
    provider = None
    jobs = []
    test_mode = False

    def __init__(self):
        """loads config from file
        """
        required_fields = [
            "mediathek_path"
        ]

        with open("config.yml", 'r') as stream:
            self.config = yaml.safe_load(stream)

        for f in required_fields:
            if f not in self.config:
                print(f"{self.prä} FATAL ERROR: missing {f} in config.yml")
                exit()

    def getVideoProvider(self, tag):
        """loads the provider library 

        Args:
            tag ([type]): tag of the provider to load

        Returns:
            bool: true if provider is loaded, false otherwise
        """

        if tag in self.tag_to_provider:
            try:
                provider = __import__('modules.'+self.tag_to_provider[tag], globals(), locals(), fromlist=[''])
                self.provider = provider.Provider()
            except Exception as e:
                print(f"{self.prä} Can not load provider module: {e}")
                return False

            print(f"{self.prä} loaded Provider {tag} with version {self.provider.version}")
        else:
            try:
                provider = __import__('modules.'+tag, globals(), locals(), fromlist=[''])
                self.provider = provider.Provider()
            except Exception as e:
                print(f"{self.prä} Can not load provider module: {e}")
                return False

            print(f"{self.prä} loaded Provider {tag} with version {self.provider.version}")

        return True

    def loadJobs(self):
        """loads all jobs

        Returns:
            [bool]: false if something went wrong
        """

        required_fields = [
            "name",
            "shortname",
            "tag",
            "tagvalue",
            "days_back",
            "type",
            "category"
        ]

        files =  [os.path.join(dirpath, f) for dirpath, dirnames, files in os.walk("jobs") for f in fnmatch.filter(files, '*.yml')]

        print(f"{self.prä} {len(files)} jobs found.")

        for f in files:
            with open(f, 'r') as stream:
                data = yaml.safe_load(stream)

            allFields = True
            for fi in required_fields:
                if fi not in data:
                    print(f"{self.prä} ERROR: can not load job {f}, {fi} is missing.")
                    allFields = False 

            if allFields:
                self.jobs.append(data)
                    
        return True 

    def runJobs(self):
        """executes all loaded jobs
        """

        tot_jobs = len(self.jobs)
        suc_jobs = 0

        for job in self.jobs:
            provider_set = self.getVideoProvider(job["provider"]) # load the provider for this job

            if self.provider is None or not provider_set:
                print(f"{self.prä} Provider {job['provider']} is not available.")
                continue

            config_map = {}
            for t in self.provider.getConfig():
                if not t in self.config.keys():
                    print(f"{self.prä} Key {t} not set on config")
                config_map[t] = self.config[t]

            self.provider.setConfig(config_map)

            print(f"{self.prä} Load job \"{job['name']}\"")
            urls = self.provider.getUrlsByTag(job["tag"], job["tagvalue"])

            if not urls:
                continue

            for url in urls:
                ret = self.download(url, job)

                if ret:
                    suc_jobs += 1
            suc_jobs += 1 # if there is nothing to download we count it as success too.

        print(f"{self.prä} {suc_jobs} out of {tot_jobs} succeded.")

        if suc_jobs == tot_jobs:
            return True
        else:
            return False


    def download(self, url, job):
        """downloads videos via youtube dl

        Args:
            url (string): url of download page
            job (dict): the job object (dict)

        Returns:
            [type]: [description]
        """

        if self.provider is None:
            print(f"{self.prä} Provider {job['provider']} not loaded")
            return False

        print(f"{self.prä} Trying to download: {url}")

        try:
            ydl_opts = {}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                infos = ydl.extract_info(url, download=False)
                uploadtime = datetime.datetime.fromtimestamp(infos["timestamp"])

                name = job["shortname"] + " S" + uploadtime.strftime("%Y")  + " E" + uploadtime.strftime("%j") + " " + infos["title"]

            if uploadtime < datetime.datetime.now()-datetime.timedelta(days=job["days_back"]):
                print(f"{self.prä} Did not download one of {job['name']}'s videos, it is to old.")
                return False

            if 'title_regex' in job.keys():
                match = re.search(job["title_regex"], infos["title"])
                if match is None:
                    print(f"{self.prä} {infos['title']} does not match title regex")
                    return False

            if "min_duration" in job.keys():
                if int(job["min_duration"]) < int(infos["duration"]):
                    print(f"{self.prä} {infos['title']} {infos['duration']} does not match min duration ({job['min_duration']})")
                    return False

            if "max_duration" in job.keys():
                if int(job["max_duration"]) > int(infos["duration"]):
                    print(f"{self.prä} {infos['title']} {infos['duration']} does not match max duration ({job['max_duration']})")
                    return False

            path = self.config["mediathek_path"] + "/" + self._cleanFileName(str(job["category"])) + "/" + self._cleanFileName(str(job["shortname"]))

            if Path('path' + infos["ext"]).is_file():
                print(f"{self.prä} File already exists: {name}")
                return False

            if job["type"] == "series.short":
                path += "/All_Episodes"
            elif job["type"] == "series":
                path += "/Season " + str(uploadtime.strftime("%Y"))

            path += "/" + name

            ydl_opts = {
                'outtmpl': path + '.%(ext)s',
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                if not self.test_mode:
                    ydl.download([url])


        except Exception as e:
            print(f"{self.prä} FATAL ERROR: could not download video file: {e}")
            return False

        if not self.writeNfo(infos, path + ".nfo"):
            print(f"{self.prä} Failure when writing NFO")
            return False

        return True

    def writeNfo(self, data, filename):
        """writes the NFO file for a video

        Args:
            data (dict): data from youtube dl about the video
            filename (string): nfo file name

        Returns:
            bool: false if something went wrong
        """

        keys_to_tag = { # mapping from the keys used by youtube dl to keys used by nfo
            "title": "title",
            "description": "plot",
            "duration": "runtime",
            "thumbnail": "thumb"
        }

        uploadtime = datetime.datetime.fromtimestamp(data["timestamp"])

        if not self.test_mode:
            try:
                nfo = open(filename, "w")

                nfo.write("<tvshow>")

                for key, value in data.items():
                    if key in keys_to_tag.keys():
                        nfo.write("<" + keys_to_tag[key] + ">" + str(value) + "</" + keys_to_tag[key] + ">")

                nfo.write("<season>" + uploadtime.strftime("%Y") + "</season>")
                nfo.write("<episode>" + uploadtime.strftime("%j") + "</episode>")
                nfo.write("</tvshow>")

                return True
            except Exception as e:
                print(f"{self.prä} Could not write NFO: {e}")
                return False
        else:
            return True

    def _cleanFileName(self, name):
        name = name.replace("/", "-")
        name = name.replace("\\", "-")
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        return ''.join(c for c in name if c in valid_chars)

    def start(self):
        """starts the downloader
        """
        self.loadJobs()
        self.runJobs()


class Timer:
    lastrun = datetime.datetime.now()-datetime.timedelta(days=365)
    runtimes = []
    prä = "TIMER"
    testing = False

    def __init__(self):
        required_fields = [
            "mediathek_path",
            "scrape_times"
        ]

        with open("config.yml", 'r') as stream:
            config = yaml.safe_load(stream)

        for f in required_fields:
            if f not in config:
                print(f"{self.prä} FATAL ERROR: missing {f} in config.yml")
                exit()
        
        self.runtimes += config["scrape_times"]

    def _stringToTime(self, string):
        try:
            form = datetime.datetime.now().strftime("%Y.%m.%d ") + string
            res = datetime.datetime.strptime(form, "%Y.%m.%d %H:%M")
        except Exception as e:
            print(e)
            return False 
        return res



    def run(self):
        executions = 0

        while True:
            time.sleep(5)
            for r in self.runtimes:
                runtime = self._stringToTime(r)
                now = datetime.datetime.now()

                if not runtime:
                    pass

                if runtime > self.lastrun and runtime < now:
                    executions += 1
                    self.lastrun = datetime.datetime.now()
                    print("Running DOWNLOADER NOW")
                    print(f"Last run: {now.strftime('%Y-%m-%d %H:%M')}")
                    if not self.testing:
                        d = Downloader()
                        d.start()   
                        break    

            if self.testing and executions >= len(self.runtimes):
                break

        return executions



if __name__ == "__main__":
    t = Timer()
    t.run()

