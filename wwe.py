#!/usr/bin/python3

import re
import requests
import CONSTANTS

def time_to_seconds(time):
    time_to_seconds = 0
    time_matches =  re.match("\\b(\d{2}):\\b(\d{2}):\\b(\d{2})", time)

    if time_matches:
        # 1 Hour
        seconds = 3600
        for i in range(1, 4):
            # Multiply the hours/minutes by the corrosponding seconds
            t = int(time_matches.group(i)) * seconds
            time_to_seconds += t
            # Divide the seconds by 60 so we get 60 seconds per minute,
            # and then 1 for every second
            seconds = int(seconds / 60)
    else:
        print("Invalid time format. Please use HH:MM:SS.")
        exit()
    return time_to_seconds

class wwe_network:

    def __init__(self, user, password):

        with requests.Session() as self._session:
            self._session.headers.update(CONSTANTS.HEADERS)

        self.user = user
        self.password = password
        self.logged_in = False

    def refresh_token(self):
        if not self.refreshToken:
            print("No refresh token found")
            return
        xx = self._session.post('https://dce-frontoffice.imggaming.com/api/v2/token/refresh', json={'refreshToken': self.refreshToken})
        exit()


    def _set_authentication(self):

        access_token = self.authorisationToken
        if not access_token:
            print("No access token found.")
            return

        self._session.headers.update({'Authorization': f'Bearer {access_token}'})
        print("Succesfully logged in")
        self.logged_in = True

    def login(self):

        payload = {
            "id": self.user,
            "secret": self.password
        }

        token_data = self._session.post('https://dce-frontoffice.imggaming.com/api/v2/login', json=payload, headers=CONSTANTS.HEADERS).json()
        if 'code' in token_data:
            print("Error while logging in. Possibly invalid username/password")
            exit()


        self.authorisationToken = token_data['authorisationToken']
        self.refreshToken = token_data['refreshToken']

        self._set_authentication()

    

    def m3u8_stream(self, stream_link: str):
        """Get the subtitle and the HLS m3u8 stream links. Used in conjunction with get_video_info.

        Args:
            stream_link (str): Link to the JSON file where the stream information is stored.

        Returns:
            hls_stream: The link to the HLS m3u8 stream
            subtitles_stream: The link to the subtitles
            chapters_stream: The link to the video chapters
        """
        #https://dve-api.imggaming.com/video/500603/playback?customerId=16&auth=xxx&timestamp=1696322111900&ssai=0&uid=V3mtdi|75da92ff-e1b6-4288-b7c2-c9d85e98aa46&dty=BROWSER&realm=dce.wwe&sId=1cb683fb-a926-470d-b769-f48dcd2be408
        stream = self._session.get(stream_link, headers=CONSTANTS.HEADERS).json()

        # Get our subtitle stream
        for i in stream['hls'][0]['subtitles']:
            if i['format'] == "vtt":
                subtitle_stream = i['url']
                break
                
        # Some videos appear to not have chapters. Should fix https://github.com/freyta/WWE-Network-Downloader/issues/32
        try:
            chapters = stream['annotations']['titles']
        except TypeError:
            chapters = None
                    
        return stream['hls'][0]['url'], subtitle_stream, chapters


    # Download the subtitles to the temp folder
    def download_subtitles(self, link, episode_title):
        # Get the substitle file
        subtitle_data = self._session.get(link).content.decode('utf-8')
        print("\nStarting to write the subtitle file")

        # Open and write the subtitle data
        vtt_file = open(f"{CONSTANTS.TEMP_FOLDER}/{episode_title}.vtt", "w")
        vtt_file.write(subtitle_data)
        
        print("Finished writing the subtitle file")
        # Close the file
        vtt_file.close()



    def write_metadata(self, link, episode_title, chapterize=False, start=None, end=None):
        
        print("\nStarting to write the metadata file")
        meta_file = open(f"{CONSTANTS.TEMP_FOLDER}/{episode_title}-metafile", "w")
        meta_file.write(f";FFMETADATA1\n\
title={episode_title}\n")

        if chapterize:
            print("\nWriting chapter information")
            
            # Get the chapter data
            chapter_data = self._session.get(link).content.decode('utf-8')
            # Match the chapter information. Example is below
            #
            # 402712                                        <----- Ignored
            # 00:18:47.601 --> 00:31:26.334                 <----- Wanted
            # Steamboat vs Pillman: Halloween Havoc 1992    <----- Wanted
            
            chapters = re.findall(r'(\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3})\n(.*?)\n\n', chapter_data)
            
            # If we have set a custom end time
            if end or start:
                for i in chapters:
                    timestamp = re.findall(r'(\d{2}:\d{2}:\d{2})', i[0])
                    if (time_to_seconds(timestamp[1]) >= start and (end == 0 or time_to_seconds(timestamp[1]) <= end)):
                        print(f"{i[1]}: {time_to_seconds(timestamp[0])} - {time_to_seconds(timestamp[1])}")
                        meta_file.write(f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={str(time_to_seconds(timestamp[0]) * 1000)}\nEND={str(time_to_seconds(timestamp[1]) * 1000)}\ntitle={i[1]}\n\n")
                        
            print("Finished writing chapter information")

        print("\nStarting to write the stream title")
        meta_file.write(f"[STREAM]\ntitle={episode_title}")
        print("Finished writing the stream title\n")
        
        print("Finished writing the metadata file")
        meta_file.close()
        
    def get_video_info(self, link):
        """Gets the information needed to download a video

        Args:
            link (str): link to the video you want to get the information from

        Returns:
            file_name: The title of the video you are going to download
            stream_url: The URL of the JSON file used to obtain the m3u8 and subtitles
            season_information: The season and episode number of the video
        """
        # Link: https://dce-frontoffice.imggaming.com/api/v4/vod/500603?includePlaybackDetails=URL
        api_link = self._session.get(f'https://dce-frontoffice.imggaming.com/api/v4/vod/{link}?includePlaybackDetails=URL').json()
        
        # If we have an invalid link, quit
        try:
            if api_link["message"]:
                print("Video link is invalid. Exiting now..")
                return
        except KeyError:
            pass
        
        if api_link['accessLevel'] == "DENIED":
            print("You don't have access to this video. Invalid subscription?")
            exit()

        # The title of the show will be our filename
        file_name = api_link['title']
        # The URL for chapters, subtitles and our stream
        stream_url = api_link['playerUrlCallback']
        # Not currently used, but the season information - not every show/episode has one
        try:
            season_information = f"S{api_link['episodeInformation']['seasonNumber']}E{api_link['episodeInformation']['episodeNumber']}"
        except KeyError:
            season_information = ""
        
        return file_name, stream_url, season_information


if __name__ == "__main__":
    print("Please run python main.py instead.")
    pass
