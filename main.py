#!/usr/bin/python3

import wwe
import m3u8, os,re
import argparse
import download_util, kodi_nfo, CONSTANTS, db_util
import time
import threading

def clean_text(text):
    # Thanks to https://stackoverflow.com/a/27647173
    return re.sub(r'[\\\\\\\'/*?:"<>|]',"",text)

# GET ARGS FOR EPISODE TO DOWNLOAD
parser = argparse.ArgumentParser(description='Download videos off the WWE Network.')
parser.add_argument('-t','--title', help='Link of the video you want to download. Example: https://network.wwe.com/video/178225', required=True)
parser.add_argument('-q','--quality', help='Quality of the video you wish to download. Value between 1 (highest) and 6 (lowest). Defaults to 1080p.', required=False)
parser.add_argument('-c','--chapter', help='Add chapter "milestones" to the video.', required=False, action='store_true')
parser.add_argument('-s','--subtitles', help='Add subtitles to the video.', required=False, action='store_true')
parser.add_argument('-k','--keep_files', help='Keep the temporary download files.', required=False, action='store_true')
parser.add_argument('-st','--start_time', help='How far into the video you want to start, in seconds. Note: Will overide other start points.', required=False)
parser.add_argument('-et','--end_time', help='How far into the video you want to stop, in seconds.', required=False)
parser.add_argument('-of','--output_filename', help='Custom output file name.', required=False)
parser.add_argument('-f','--force', help='Overwrite previously downloaded files.', required=False, action='store_true')

args = vars(parser.parse_args())

keep_files = False
force_download = False
download_subtitles = False

# Set the default video quality to 1080p
QUALITY = CONSTANTS.VIDEO_QUALITY[0]

# Get the episode title
if args['title']:
    EPISODE = args['title']
    if "https://network.wwe.com/video/" in EPISODE:
        EPISODE = EPISODE.replace("https://network.wwe.com/video/", "")
    else:
        print("Invalid link format. It should contain \"https://network.wwe.com/video/\"")
        exit()

# If the title wasn't set
if not EPISODE:
	print("No episode found. Use the --title or -t parameter.")
	exit()

# Do we want to keep the downloaded files?
if args['keep_files']:
    keep_files = True

# Do we want to download the subtitles?
if args['subtitles']:
    download_subtitles = True

# Set the start and end times
if args['start_time']:
    START_FROM = wwe.time_to_seconds(args['start_time'])
if args['end_time']:
    END_TIME = wwe.time_to_seconds(args['end_time'])
    
# Set whether it is a partial download or not
try:
    if START_FROM:
        partial_download = True
except NameError:
    partial_download = False

# Set the custom output title
CUSTOM_FILENAME = ""
if args['output_filename']:
    CUSTOM_FILENAME = args['output_filename']

# Set the quality of the video we want
if args['quality']:
    if int(args['quality']) < 0 or int(args['quality']) >= len(CONSTANTS.VIDEO_QUALITY):
        print(f"Invalid quality choice. It must be between 0 (1080p) and {len(CONSTANTS.VIDEO_QUALITY)} (288p)")
        exit()

    QUALITY = CONSTANTS.VIDEO_QUALITY[int(args['quality'])]

if args['force']:
    force_download = True

# Login
if CONSTANTS.USERNAME == "" or CONSTANTS.PASSWORD == "":
    print("Please enter your username and/or password in CONSTANTS.py.")
    exit()

account = wwe.wwe_network(CONSTANTS.USERNAME,CONSTANTS.PASSWORD)
account.login()

# Get the video JSON which tells us the hls url link
video_link = account.get_video_info(EPISODE)

# Quit if the video information is empty
if not video_link:
    exit()

# Grab the m3u8
stream_url = account.m3u8_stream(video_link[1])

# Set a custom file name if one was requested
if not CUSTOM_FILENAME:
    title = video_link[0]
else:
    title = CUSTOM_FILENAME

print("Got the video information")

# Connect to the database where we store which videos we have downloaded
database = db_util.database()
database.db_connect()

# Check if we have already downloaded the video before.
db_q = database.db_query(video_link[2], is_partial_download=partial_download)

# If we haven't forced the download, then we will display an error and quit
if not force_download and db_q:
    print("You have already downloaded this video.")
    print("If you want to download this file anyway, please use --force or -f")
    print("Quitting.")
    exit()

# Get the base url of our video
base_url = stream_url[0].split(".m3u8")[0].rsplit("/", 1)

# Initialise the downloader
download = download_util.download()
index_m3u8 = download.get_index_m3u8(stream_url[0])

index_m3u8_obj = m3u8.loads(index_m3u8.data.decode('utf-8'))

# Get our audio playlist
audio_qualities = []
for i in index_m3u8_obj.media:
    # We want English audio, so any files with eng as its language is added to our list
    if "eng" in i.language:
        audio_qualities.append((int(i.group_id.split('audio-')[1]), base_url[0]+"/"+ i.uri))

# Sort the audio quality from high to low
audio_qualities.sort(reverse=True)
# Choose the playlist we want
audio_playlist = download.get_playlist_object(audio_qualities[0][1])

# The kwargs we will pass to the downloader
kwargs = {"playlist":audio_playlist,
          "base_url":audio_qualities[0][1].split("index.m3u8")[0],
          "title":clean_text(title)
          }

# If we have a start_time then add the set start time, otherwise default to 0
try:
    if START_FROM:
        kwargs.update({"start_from":START_FROM})
except NameError:
    START_FROM = 0
    kwargs.update({"start_from":0})

# If we have an end_time then add the set end time, otherwise default to 0
try:
    if END_TIME:
        kwargs.update({"end_time":END_TIME})
except NameError:
    END_TIME = 0
    kwargs.update({"end_time":0})

# Create a list where we will add our threads
download_threads = []

# Start the audio downloading thread
audio_thread = threading.Thread(target=download.download_playlist, kwargs=kwargs)
audio_thread.start()
# Add the audio to our thread list
download_threads.append(audio_thread)


# Get our video playlist
video_selections = []

for i in index_m3u8_obj.playlists:

    # Get all playlists that fit within our quality requirements
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

# Start the video downloading thread
video_thread = threading.Thread(target=download.download_playlist, kwargs=kwargs)
video_thread.start()

# Add the video thread to our thread list
download_threads.append(video_thread)

# Wait for all threads to be finished
for thread in download_threads:
    thread.join()

# Download the chapter information
account.write_metadata(stream_url[2], clean_text(title), args['chapter'], START_FROM, END_TIME)

# Create output folder if it doesn't exist
if not os.path.exists(CONSTANTS.OUTPUT_FOLDER + "/" + clean_text(video_link[0])):
    os.makedirs(CONSTANTS.OUTPUT_FOLDER + "/" + clean_text(video_link[0]))

if(download_subtitles):
    account.download_subtitles(stream_url[1], clean_text(title))

# Finally we want to combine our audio and video files
download.combine_videos(clean_text(title), clean_text(video_link[0]), keep_files=keep_files, has_subtitles=download_subtitles)

# Insert the downloaded video into our database
if db_q:
    database.db_upd(video_link[2], video_link[1], str(video_selections[0][0]), partial_download, int(time.time()))
    print("Updated database with the new video information")
else:
    database.db_ins(video_link[2], video_link[1], str(video_selections[0][0]), partial_download, int(time.time()))
    print("Inserted the video into the database")
