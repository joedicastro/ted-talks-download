# TED Talks Download

A pair of python scripts to download videos and subtitles for the popular
**[TED Talks](http://ted.com)**


### TEDTalks.py

This script automatically downloads (as a scheduled task) videos and subtitles
for the new TED Talks published. Gets a HD video by using the
[TED Talks (HD) RSS feed](http://feeds.feedburner.com/tedtalksHD)
to know the latest published

It's inspired by the idea of a
[previous python script](http://fci-h.blogspot.com/2010/05/python-script-to-download-ted-talks.html)
by [Shereef Sakr](http://www.blogger.com/profile/14485464016030085189).
Actually the mechanical of this is more similar to TEDSubs.py, but this
inspired mo to create that and later the other. Shereef, Thanks for you work!

### TEDSubs.py

This one downloads the video and/or the subtitles for a particular TED Talk,
which is established by its URL.  The subtitles are downloaded in English and
Spanish languages if available.


## Pre-Requisites & Dependencies

Obviously, first we need is [python](http://www.python.org/). If we are in Linux
or Mac, usually is installed by default. If we are in Windows, download it from
[here.](http://www.python.org/download/)

The python version needed for run both scripts is 2.6

TEDTalks.py uses several modules included in the python standard library, except
one, [feedparser](http://www.feedparser.org/), which needs to be installed

The marvelous python module feedparser by
[Mark Pilgrim](http://en.wikipedia.org/wiki/Mark_Pilgrim), usually is included
in the most popular linux distributions' repositories. Then, only needs to be
installed

For debian/Ubuntu is like that:

    sudo aptitude install python-feedparser

For Windows, get it from
[here](http://code.google.com/p/feedparser/downloads/list) and install:

    (path where you installed python)\python.exe setup.py install

TEDsubs.py only uses python standard library modules, no needs any more.

## Using them

### TEDTalks.py

This is the easiest to use, no needs any parameter, just run. It is meant to run
automatically on a scheduled basis, that is, to be run every day at the same time

This would use, e.g., the Scheduled Tasks in Windows and cron in Linux or Mac to
set a daily schedule of the script.

If we run it whithout any parameter, then it uses the current folder to store
the talks and the subtitles. If we instead want to store the talks in another
folder, we need to specify it as parameter.

The command line syntax is as folllows

    python TEDTalks.py [path]

where `path` is the optional path where we want to store the talks & subtitles.

If we run the script with the `-h` option, we get the help

    $ python TEDTalks.py -h
    usage: TEDTalks.py [-h] [-v] [path]

    Automate download new HD TED Talks by its RSS Feed

    positional arguments:
      path           The path to store the TED Talks videos

    optional arguments:
      -h, --help     show this help message and exit
      -v, --version  show program's version number and exit

Wen first run, it's downloaded the day before video (if any) and the subtitles
in English and Spanish languages that are available for the same. The following
runs will download the latest video released in the HD RSS feed, and also verify
the availability of subtitles (English and Spanish) for all newly downloaded
videos (which still appear at the entries of the RSS) that are still in the
folder. If available a subtitle has not been downloaded, download it.

If downloads anything, videos or subtitles, sends a mail to the machine's local
user with the log (this only runs in linux, not tested on a Mac)


### TEDSubs.py

This one needs a parameter to run, and have an option (download only subs).
The command line syntax is as folllows

    python TEDSubs.py [Options] TEDTalkURL

where option is  `-s` (or `--only_subs`) and `TEDTalkURL` is the Talk URL.

if run the script without parameters, we get the help

    $ python TEDSubs.py
    Usage: TEDSubs.py [Options] TEDTalkURL

    Where TEDTalkURL is the url of a TED Talk webpage

    For example:

    TEDSubs.py -s  http://www.ted.com/talks/lang/eng/jamie_oliver.html

    Downloads only the subs for the Jamie Oliver's TED Talk, if wants the video too
    only needs to remove the "-s" option

    Downloads the subtitles and the video (optional) for a TED Talk.

    Options:
      --version        show program's version number and exit
      -h, --help       show this help message and exit
      -s, --only_subs  download only the subs, not the video

Where displays a example of how to download only the subs for the
[Jamie Oliver's Talk](http://www.ted.com/talks/lang/eng/jamie_oliver.html)

    python TEDSubs.py -s  http://www.ted.com/talks/lang/eng/jamie_oliver.html

If we want to download the video too, only need to remove the `-s` option

    python TEDSubs.py http://www.ted.com/talks/lang/eng/jamie_oliver.html

And so with all the TED talks, all you need is to replace the web address
Oliver's talk for the one we want the download

## How to get them

The code is hosted in a Git repository at GitHub, use this to get a clone:

    git clone git://github.com/joedicastro/ted-talks-download.git


## Features

Videos are downloaded in .mp4 format, in HD quality (usually 850 x 450 pixels),
and subtitles are converted an stored from original .json format to common .srt
format

## Alternatives

if my scripts don't match what you want, here's a summary of alternatives (which I know)

* __TEDTalks.py__

  - Language: Python
  - Type: script
  - Features: Automate download new TED Talks & subtitles (eng/spa) by its HD RSS feed
  - Author: Me

* __TEDSubs.py__

  - Language: Python
  - Type: script
  - Features: Donwload TED Talks videos & subtitles (eng/spa) by its URL
  - Author: Me

* __[TEDSubtitles.py](http://fci-h.blogspot.com/2010/05/python-script-to-download-ted-talks.html)__

  - Language: Python
  - Type: script
  - Features: Download subtitles for TED Talks by its url for selected language
  - Author: [Shereef Sakr](http://www.blogger.com/profile/14485464016030085189)

* __[metaTED](http://bitbucket.org/petar/metated)__

  - Language: Python
  - Type: web
  - Features: Creates metalink files of TED talks for easier downloading
  - Author: [Petar Marić](http://www.petarmaric.com/)

* __[tedget.py](http://bitbucket.org/johannes/tedget)__

  - Language: Python
  - Type: script
  - Features: Download TED Talks videos by its url or id
  - Author: [Johannes Hoff](http://johanneshoff.com/)

* __[Ted Talk Subtitle Download](http://tedtalksubtitledownload.appspot.com/)__

  - Language: Python
  - Type: Web
  - Features: Download TED Talks subtitles by its URL
  - Author: [Esteban Ordano](http://estebanordano.com.ar/)

* __[Miro](http://www.getmiro.com)__

  - Language: Python & GTK
  - Type: Desktop App
  - Features: RSS Aggregator, Video Player & Bittorrent client. Can download TED Talks videos and play them
  - Author: [Participatory Culture Foundation](http://participatoryculture.org/)


## Contribution

Contributions and Feedback are most welcome.
To contribute to the improvement and development of this scripts, you can send
suggestions or bugs via the issues.

## License

Both scripts are distributed under the terms of the
[GPLv3 license](http://www.gnu.org/licenses/gpl.html)

##### Apologies for any misspelling or syntax error, English isn't my mother tongue.
