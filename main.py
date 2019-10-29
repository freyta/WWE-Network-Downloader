import wwe
import json
import subprocess
import m3u8
import argparse
import download_util, kodi_nfo, CONSTANTS

email = ''
password = ''

# GET ARGS FOR EPISODE TO DOWNLOAD
parser = argparse.ArgumentParser(description='Download videos off the WWE Network.')
parser.add_argument('-t','--title', help='Link of the video you want to download. Example: /episode/Prime-Time-Wrestling-9283', required=True)
parser.add_argument('-q','--quality', help='Quality of the video you wish to download. Value between 1 (highest) and 6 (lowest). Defaults to 1080p.', required=False)
parser.add_argument('-c','--chapter', help='Add chapter "milestones" to the video.', required=False, action='store_true')
parser.add_argument('-e','--episode_nfo', help='Create a Kodi format NFO TV episode file.', required=False, action='store_true')
parser.add_argument('-s','--series_nfo', help='Create a Kodi format NFO TV show file.', required=False, action='store_true')
parser.add_argument('-st','--start_time', help='How far into the video you want to start, in seconds. Note: Will overide other start points.', required=False)
parser.add_argument('-et','--end_time', help='How far into the video you want to stop, in seconds.', required=False)

args = vars(parser.parse_args())

create_episode_nfo = False
create_series_nfo = False
# Set the default video quality to 1080p
QUALITY = CONSTANTS.VIDEO_QUALITY[0]

# Get the episode title
if args['title']:
    EPISODE = args['title']
    if "https://watch.wwe.com" in EPISODE:
        EPISODE = EPISODE.replace("https://watch.wwe.com", "")

# If the title wasn't set
if not EPISODE:
	print("No episode found. Use the --title or -t parameter.")
	exit()

# Some links have a starting point in their link, i.e https://watch.wwe.com/episode/Expect-The-Unexpected-9842?startPoint=371.701
if "?startPoint=" in EPISODE:
    START_FROM = EPISODE.split("?startPoint=")[1]
    # Remove the startPoint from our EPISODE - probably isn't needed
    EPISODE = EPISODE.split("?startPoint=")[0]

# Prefix a / if we haven't included it in our title otherwise we get an error
if not EPISODE.startswith("/"):
    EPISODE = "/" + EPISODE

# Do we want to create an episode or series nfo file as well?
if args['episode_nfo']:
    create_episode_nfo = True
if args['series_nfo']:
    create_series_nfo = True

# Set the start and end times
if args['start_time']:
    START_FROM = args['start_from']
if args['end_time']:
    END_TIME = args['end_time']
print(START_FROM)
# Set the quality of the video we want
if args['quality']:
    if int(args['quality']) < 0 or int(args['quality']) >= len(CONSTANTS.VIDEO_QUALITY):
        print("Invalid quality choice. It must be between 0 (1080p) and {} (288p)".format(len(CONSTANTS.VIDEO_QUALITY)))
        exit()

    QUALITY = CONSTANTS.VIDEO_QUALITY[int(args['quality'])]

# Login
account = wwe.wwe_network(email,password)
account.login()

print("Logged in")

# Get the video JSON which tells us the hls url link
video_link = account.get_video_info(EPISODE)

# Grab the m3u8
stream_url = account.m3u8_stream(video_link[0])
title = video_link[1]

print("Got the video information")

# Get the base url of our video
base_url = stream_url.split(".m3u8")[0].rsplit("/", 1)

# Initialise the downloader
download = download_util.download()
index_m3u8 = download.get_index_m3u8(stream_url)

index_m3u8_obj = m3u8.loads(index_m3u8.data.decode('utf-8'))

# Get our audio playlist
audio_qualities = []
for i in index_m3u8_obj.media:
    # We want English audio, so any files with eng as it's language is added to our list
    if "eng" in i.language:
        audio_qualities.append((int(i.group_id.split('audio-')[1]), base_url[0]+"/"+ i.uri))

# Sort the audio quality from high to low
audio_qualities.sort(reverse=True)
# Choose the playlist we want
audio_playlist = download.get_playlist_object(audio_qualities[0][1])

# The kwargs we will pass to the downloader
kwargs = {"playlist":audio_playlist,
          "base_url":audio_qualities[0][1].split("index.m3u8")[0],
          "title":title
          }

# If we have a start_time then add the set start time, otherwise default to 0
try:
    if START_FROM:
        kwargs.update({"start_from":START_FROM})
except NameError:
    kwargs.update({"start_from":0})

# If we have an end_time then add the set end time, otherwise default to 0
try:
    if END_TIME:
        kwargs.update({"end_time":END_TIME})
except NameError:
    kwargs.update({"end_time":0})

# Download the audio file
download.download_playlist(**kwargs)

#Get our playlist. We want 1080p
video_selections = []

for i in index_m3u8_obj.playlists:
   
    if (i.stream_info.average_bandwidth <= QUALITY * 1000):
        # Create a list of potential URIs
        video_selections.append((i.stream_info.bandwidth, base_url[0] + "/" + i.uri))

# Select the first one which has the highest bitrate
video_selections.sort(reverse=True)
# Get the playlist m3u8 we want to download
video_playlist = download.get_playlist_object(video_selections[0][1])

# Update the kwargs that we will send to the downloader
kwargs.update({"playlist":video_playlist})
kwargs.update({"base_url":video_selections[0][1].split("index.m3u8")[0]})

# Download the playlist
download.download_playlist(**kwargs)

# Download the chapter information\
account.get_chapter_information(EPISODE, video_link[1], args['chapter'])

# Finally we want to combine our audio and video files
download.combine_videos(title)
