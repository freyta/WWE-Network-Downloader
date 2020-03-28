WWE Network 2.0 Downloader (Improved)

Freyta's WWE Network 2.0 Downloader using Python3. This was coded by me from scratch, ideas were taken from youtube-dl.

Features include the following:
- Downloading from set start times
- Ending at certain times (i.e. only downloading certain matches)
- Qualtiy selection (1 being 1080p, 6 being 288p)
- Kodi NFO file creations (TV episode and Series only at the moment - PPV needs to be added)
- Part downloading of files.

### Usage instructions

###### Basic video download:

`python3 main.py -t https://watch.wwe.com/episode/SmackDown-130268`

###### Download with start and end times, using custom file name:

`python3 main.py -st 1619.934 -et 1712.834 -of 'Tucker confronts Mandy Rose Smackdown 02-21-2020' -t https://watch.wwe.com/episode/SmackDown-130268`

###### Download chapterised 720p video with Kodi series and episode NFO files:

`python3 main.py -c -q 3 -s -e -t https://watch.wwe.com/episode/Bret-Hart-132278`


### Options

> **-t** - Link to the video you want to download\
> **-q** - Quality of the video you want to download. 1 is 1080p high (default) 6 being 288p (lowest)\
> **-c** - Add milestone chapters to the video.\
> **-k** - Keep temporary aac and ts files\
> **-e** - Write a Kodi episode NFO file\
> **-s** - Write a Kodi series NFO file with poster and fanart\
> **-st** - Start time in seconds from where you want to start downloading\
> **-et** - End time in seconds from where you want to finish downloading\
> **-of** - Custom output filename
