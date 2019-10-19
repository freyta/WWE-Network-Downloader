import wwe
import json
import subprocess
import m3u8
import argparse
import kodi_nfo

def make_safe_filename(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"
    return "".join(safe_char(c) for c in s).rstrip("_")


# GET ARGS FOR EPISODE TO DOWNLOAD
parser = argparse.ArgumentParser(description='Download videos off the WWE Network')
parser.add_argument('-t','--title', help='Link of the video you want to download. Example: /episode/Prime-Time-Wrestling-9283', required=True)
parser.add_argument('-e','--episode_nfo', help='Create a Kodi format NFO TV episode file.', required=False, action='store_true')
parser.add_argument('-s','--series_nfo', help='Create a Kodi format NFO TV show file.', required=False, action='store_true')
args = vars(parser.parse_args())

create_episode_nfo = False
create_series_nfo = False

# Get the episode title
if args['title']:
    EPISODE = args['title']

# If the title wasn't set
if not EPISODE:
	print("No episode found. Use the --title or -t parameter.")
	exit()

# Do we want to create an episode or series nfo file as well?
if(args['episode_nfo']):
    create_episode_nfo = True
if(args['series_nfo']):
    create_series_nfo = True

# Prefix a / if we haven't included it in our title
if not EPISODE.startswith("/"):
    EPISODE = "/" + EPISODE

# Login
account = wwe.wwe_network(email,password)
account.login()

print("Logged in")

# Get the video JSON which tells us the hls url link
print(EPISODE)
video_link = account.get_video_info(EPISODE)

# Grab the m3u8
stream_url = account.m3u8_stream(video_link[0])
title = video_link[1]

print("Got the video information")

# Download the video
zz = account.get_m3u8(stream_url, make_safe_filename(title),1100)

# Create the kodi NFO files
if(create_episode_nfo):
    kodi_nfo.create_episode_nfo(EPISODE)

if(create_series_nfo):
    kodi_nfo.create_show_nfo(EPISODE)


print(" wget -S -O -O index.m3u8 - \"{}\"".format(stream_url))

print('\n')
#print('ffmpeg -user_agent "WWE/4.0.13 (Linux;Android 9) ExoPlayerLib/2.9.3" -i "' + stream_url + '" -c copy ' + make_safe_filename(title) + '.mp4 -y')
#print('ffprobe -user_agent "WWE/4.0.13 (Linux;Android 9) ExoPlayerLib/2.9.3" -i "' + stream_url + '"')
#exit()
print('\n')
#print("\"/volume1/@appstore/py3k/usr/local/bin/youtube-dl\" -F --verbose --hls-prefer-native --fixup never --add-header User-Agent:\"WWE/4.0.13 (Linux;Android 9) ExoPlayerLib/2.9.3\" \"{}\" -o \"{}\".mp4".format(stream_url, make_safe_filename(title)))

print("youtube-dl --dump-headers --verbose --hls-prefer-native --fixup never --add-header User-Agent:\"WWE/4.0.13 (Linux;Android 9) ExoPlayerLib/2.9.3\" \"{}\" -o \"1{}\".mp4".format(stream_url, make_safe_filename(title)))


#subprocess.call("youtube-dl -k -f \"bestvideo[height<=512]+audio-192000-English\" --verbose --hls-prefer-native --fixup never --add-header User-Agent:\"WWE/4.0.13 (Linux;Android 9) ExoPlayerLib/2.9.3\" \"{}\" -o \"{}\".mp4".format(stream_url, make_safe_filename(title)), shell=True)
#subprocess.call("youtube-dl --verbose --hls-prefer-native --fixup never --add-header User-Agent:\"WWE/4.0.13 (Linux;Android 9) ExoPlayerLib/2.9.3\" \"{}\" -o \"{}\".mp4".format(stream_url, make_safe_filename(title)), shell=True)
