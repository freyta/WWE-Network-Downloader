#!/usr/bin/python3

import os, sys
import subprocess
from time import time
import json
import requests
import arrow
from urllib.parse import urlsplit, parse_qs
import urllib3
import m3u8
import certifi

HEADERS = {
    'User-Agent': 'okhttp/3.12.1'
}

REALM_HEADERS = {
    'x-api-key': '640a69fb-68b1-472c-ba4b-36f50288c984',
    'realm': 'dce.wwe'
}

DICE_MOBILE_API_KEY = '640a69fb-68b1-472c-ba4b-36f50288c984'


class wwe_network:

    def __init__(self, user, password):

        with requests.Session() as self._session:
            self._session.headers.update(HEADERS)

        self.user = user
        self.password = password
        self.logged_in = False



    def _set_authentication(self):

        access_token = self.authorisationToken
        if not access_token:
            print("No access token found.")
            return

        self._session.headers.update({'Authorization': 'Bearer {}'.format(access_token)})
        self.logged_in = True

    def login(self):

            payload = {
                "id": self.user,
                "secret": self.password
            }

            token_data = self._session.post('https://dce-frontoffice.imggaming.com/api/v2/login', json=payload, headers=REALM_HEADERS).json()

            if 'code' in token_data:
                print("Error - {}".format(token_data.get('messages')))
                exit()


            self.authorisationToken = token_data['authorisationToken']
            self.refreshToken = token_data['refreshToken']

            self._set_authentication()

    # Get the m3u8 stream
    def m3u8_stream(self, stream_link):

        #https://dve-api.imggaming.com/v/70800?customerId=16&auth=1f7512c7c2b7474abf723188038b32c1&timestamp=1564126721496
        stream = self._session.get(stream_link, headers=REALM_HEADERS).json()

        return stream['hls']['url']


    def _video_url(self, link):
        #playerUrlCallback=https://dve-api.imggaming.com/v/70800?customerId=16&auth=33d8c27ac15ff76b0af3f2fbfc77ba05&timestamp=1564125745670
        video_url = self._session.get('https://dce-frontoffice.imggaming.com/api/v2/stream/vod/{}'.format(link), headers=REALM_HEADERS).json()

        return video_url['playerUrlCallback']

    def get_video_info(self, link):
        # Link: https://cdn.watch.wwe.com/api/page?path=/episode/This-Tuesday-in-Texas-1991-11831
        # We need   DiceVideoId
        api_link = self._session.get('https://cdn.watch.wwe.com/api/page?path={}'.format(link)).json()

        entry = api_link['entries'][0]['item']

        # If our event is a weekly/episodic show, add the date, season and episode number to the file name
        if entry["customFields"].get("EventStyle") == "Episodic":
            if entry["episodeNumber"] < 10:
                ep_num = "0" + str(entry["episodeNumber"])
            else:
                ep_num = entry["episodeNumber"]

            file_date = arrow.get(
                    entry["firstBroadcastDate"], "YYYY-MM-DDTHH:mm:ssZ"
            )
            file_date = file_date.format("MM-DD-YYYY")

            file_name = "{} {} - S{}E{} - {}".format(
                entry["customFields"]["Franchise"],
                entry["episodeName"]
                .replace("&", "and")
                .replace(":", "- ")
                .replace("'", "")
                .replace("\"", "")
                .replace("/", " "),
                entry["releaseYear"],
                ep_num,
                file_date,
            )
        elif entry["customFields"].get("SeasonNumber"):
            if entry["episodeNumber"] < 10:
                ep_num = "0" + str(entry["episodeNumber"])
            else:
                ep_num = entry["episodeNumber"]

            file_date = arrow.get(
                    entry["firstBroadcastDate"], "YYYY-MM-DDTHH:mm:ssZ"
            )
            file_date = file_date.format("MM-DD-YYYY")

            file_name = "{} - S{}E{} - {}".format(
                entry["customFields"]["SeriesName"],
                entry["customFields"].get("SeasonNumber"),
                ep_num,
                entry["episodeName"]
                .replace("&", "and")
                .replace(":", "- ")
                .replace("'", "")
                .replace("\"", "")
                .replace("/", " "),
            )

        elif entry["customFields"].get("EventStyle") == "PPV":
            # If it is a PPV get the title and year into variables
            ppv_title = entry["episodeName"]
            ppv_year = entry["releaseYear"]
            # Check if the PPV already has the year in it. For example "This Tuesday in Texas 1991" has the year,
            # but "WrestleMania 35" doesn't. Since we don't want to have "This Tuesday in Texas 1991 1991" as
            # our filename we will just use the PPV title
            if str(ppv_year) in ppv_title:
                file_name = "{} {}".format(
                    entry["customFields"]["Franchise"], entry["episodeName"]
                )
            else:
                file_name = "{} {} {}".format(
                    entry["customFields"]["Franchise"],
                    entry["episodeName"],
                    entry["releaseYear"],
                )
        else:
            if not entry.get('title'):
                raise Exception("Unrecognized event type")
            file_name = (
                entry["title"]
                .replace("&", "and")
                .replace(":", "- ")
                .replace("'", "")
                .replace("\"", "")
                .replace("/", " ")
            )

        return self._video_url(api_link['entries'][0]['item']['customFields']['DiceVideoId']), file_name


    def get_m3u8(self, link, title, start_from = 0):
        # Get the base URL for future requests
        try:
            if "master.m3u8" in link:
                base_url = link.split("master.m3u8")
            elif "playlist-archive.m3u8" in link:
                base_url = link.split("playlist-archive.m3u8")

        except:
            print("Couldn't find a base url - exiting")
            exit()

        # Setup urllib3 for downloading the media files
        user_agent = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        http = urllib3.PoolManager(headers=user_agent,
                                   cert_reqs='CERT_REQUIRED',
                                   ca_certs=certifi.where())

        # Get the m3u8 file as a string so we can select a playlist
        m3u8_string = http.request('GET', link)
        m3u8_obj = m3u8.loads(m3u8_string.data.decode('utf-8'))
        # debugging - useful to see the playlists
        #print(json.dumps(m3u8_obj.data, indent=4, sort_keys=True))

        # Get our audio playlist
        data = m3u8.parse(m3u8_string.data.decode('utf-8'))
        for i in m3u8_obj.media:

            print("____")
            print(i)

            try:
                if "192000" in i.uri:
                    audio_m3u8 = base_url[0] + i.uri
                elif i.group_id == "aac-primary" or "YES" in i.default and i.name == "English":
                    audio_m3u8 = base_url[0] + i.uri
                    break
            except:
                print("Error: Couldn't find a suitable audio m3u8 file.")
                exit()

        # Get our playlist. We want 1080p
        video_selections = []

        for i in m3u8_obj.playlists:
            #print(i)

            '''
            1080p high = 10000
            1080p low  = 6500
            720p high  = 4500
            720p high  = 2100
            504p high  = 1500
            360p high  = 1000
            288p high  = 600

            '''
            if(i.stream_info.average_bandwidth <= 10000 * 1000):
                #video_m3u8 = base_url[0] + i.uri
                # Create a list of potential URIs
                video_selections.append((i.stream_info.bandwidth, base_url[0] + i.uri))

        # Select the first one
        video_selections.sort(reverse=True)
        for bw, uri in video_selections:
            print("{} - {}".format(bw, uri))

        video_m3u8 = video_selections[0][1]
        # Now we download our audio m3u8 file
        m3u8_string = http.request('GET', audio_m3u8)
        m3u8_obj = m3u8.loads(m3u8_string.data.decode('utf-8'))
        print("\n\n{} - Starting to download files\n\n".format(arrow.now()))



        # For every segment in the playlist
        files_to_download = len(m3u8_obj.segments)
        current_time = float(0)

        try:
            for i in m3u8_obj.segments:
                current_time += i.duration
                if(current_time >= start_from):
                    sys.stdout.write("\r{} audio files downloaded out of {}".format(i.uri.split('.aac')[0], files_to_download))
                    # Get the base link for the audio files and then open the URL
                    download_link = audio_m3u8.split("index.m3u8")[0] + i.uri
                    xx = http.request('GET', download_link)
                    # Now we append the audio files to the aac file and clear the programs buffer
                    f= open("/mnt/DATA/Python/wwe_network_2/out/{}.aac".format(title),"ab+")
                    f.write(xx.data)
                    f.flush()
                    sys.stdout.flush()
        except KeyboardInterrupt:
            pass

        # Close the aac file
        f.close()
        print("{} audio file(s) downloaded".format(files_to_download))


        m3u8_string = http.request('GET', video_m3u8)
        m3u8_obj = m3u8.loads(m3u8_string.data.decode('utf-8'))

        files_to_download = len(m3u8_obj.segments)

        #segment_length  = m3u8_obj.segments[0].duration
        current_time = float(0)
        try:
            for i in m3u8_obj.segments:
                #current_segment = i.uri.split(".ts")[0]
                #if(int(current_segment) >= start_from):
                current_time += i.duration
                if(current_time >= start_from):
                    sys.stdout.write("\r{} video files downloaded out of {}".format(i.uri.split('.ts')[0], files_to_download))
                    # Get the base link for the audio files and then open the URL
                    download_link = video_m3u8.split("index.m3u8")[0] + i.uri
                    xx = http.request('GET', download_link)
                    # Now we append the audio files to the aac file and clear the programs buffer
                    f= open("/mnt/DATA/Python/wwe_network_2/out/{}.ts".format(title),"ab+")
                    f.write(xx.data)
                    f.flush()
                    sys.stdout.flush()
        except KeyboardInterrupt:
            pass

        # Close the video ts file
        f.close()
        print("{} video file(s) downloaded".format(files_to_download))

        subprocess.call("ffmpeg -i out/{}.ts -i out/{}.aac -c copy out/{}.mp4".format(title, title, title), shell=True)
        print("\n\n{} - Finished all tasks".format(arrow.now()))

        return m3u8_obj
