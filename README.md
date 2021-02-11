# Mediathek Downloader

Mediathek Downloader is a small python applicatopn for automatically downloading videos from german public service broadcasting. 

The application is based on `youtube-dl`.

## How it works

The timer class in `run.py` shedules download times. It triggers the downloader class. This will then read all job files in `/jobs` and execute them. 

### Provider

Provider are the heart of this application. Based on the `tag` and the `tagvalue` the provider (a module in `/modules`) will select all urls that will be passed to `youtube-dl`. So make sure to use tags and tag values that are supported by the choosen provider. 

### Expand it yourself

You can easily expand the application with other providers. Just check the `example_provider.py` in `/modules` and copy it. The application will automatically try to load the module based on the provider name given in the job.

## Providers

### ZDF

Supported video types:
* `overwiew.new` is for new videos from a TV show
* `overview.teaser` is for teasers of a TV show
* `category` is for categories provided by ZDF

**New TV show:**

`tag: overview.new`
`tagvalue:` url of a overview page (search for a TV show, first result is usually the overview page)

**TV show teasers:**

`tag: overview.teaser`
`tagvalue:` url of a overview page (search for a TV show, first result is usually the overview page)

**Categories:**

`tag: category`
`tagvalue:` url of the category page (choose category from menu)

### ARD

Supported video types:
* `search` search for a video

**Search**

`tag: search`
`tagvalue: ` search keyword


