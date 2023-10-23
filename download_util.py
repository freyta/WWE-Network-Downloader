#!/usr/bin/python3

import urllib3, certifi
import m3u8, json
import sys, subprocess, os
import CONSTANTS

class download:

    def __init__(self):
        self.http = urllib3.PoolManager(headers=CONSTANTS.DOWNLOAD_HEADERS,
                                   cert_reqs='CERT_REQUIRED',
                                   ca_certs=certifi.where())

    def create_dirs(self):
        # If the download directory doesn't exist, we need to create it
        if not os.path.isdir(f"./{CONSTANTS.OUTPUT_FOLDER}"):
            os.mkdir(f"./{CONSTANTS.OUTPUT_FOLDER}")
        if not os.path.isdir(f"./{CONSTANTS.TEMP_FOLDER}"):
            os.mkdir(f"./{CONSTANTS.TEMP_FOLDER}")

    def get_index_m3u8(self, link):
        # Return the contents of the m3u8 playlist
        return(self.http.request('GET', link))

    def get_playlist_object(self, link):
        # Return the playlist as an object
        return(m3u8.loads(self.http.request('GET', link).data.decode('utf-8')))

    def write_data(self, data, location):
        # Append the data to the file. Data is in bytes
        f = open(location,"ab+")
        f.write(data)
        # Flush the buffer - hopefully this keeps our script from using up too much ram
        f.flush()

    def write_upto(self, part, name):
        # Write which file we just downloaded to a temporary file in JSON format
        f = open(name+".part","w")
        json.dump({"current_time":part}, f)

    def read_part_file(self, filename):
        # Read which file we need to continue downloading from
        json_file = open(filename, "r")
        part = json.load(json_file)
        return float(part.get("current_time"))

    def combine_videos(self, title, file_folder, keep_files=False, has_subtitles=False):
        input_file = CONSTANTS.TEMP_FOLDER + "/" + title
        output_file = CONSTANTS.OUTPUT_FOLDER + "/" + file_folder + "/" + title
        metafile = CONSTANTS.TEMP_FOLDER + "/" + title + "-metafile"
        
        # If we have downloaded subtitles, add them to the command
        if has_subtitles:
            subtitles = CONSTANTS.TEMP_FOLDER + "/" + title + ".vtt"
            ffmpeg_command = (f'ffmpeg \
                -i "{subtitles}"\
                -i "{input_file}.ts"\
                -i "{input_file}.aac"\
                -i "{metafile}" -map_metadata 1\
                -c copy\
                -c:s mov_text\
                "{output_file}.mp4" -y')
        else:
            ffmpeg_command = (f'ffmpeg \
                -i "{input_file}.ts"\
                -i "{input_file}.aac"\
                -i "{metafile}" -map_metadata 1\
                -c copy\
                "{output_file}.mp4" -y')

        subprocess.call(ffmpeg_command, shell=True)
        if not keep_files:
            os.remove(f"{os.getcwd()}/{CONSTANTS.TEMP_FOLDER}/{title}.aac")
            os.remove(f"{os.getcwd()}/{CONSTANTS.TEMP_FOLDER}/{title}.aac.part")
            os.remove(f"{os.getcwd()}/{CONSTANTS.TEMP_FOLDER}/{title}.ts")
            os.remove(f"{os.getcwd()}/{CONSTANTS.TEMP_FOLDER}/{title}.ts.part")
            os.remove(f"{os.getcwd()}/{CONSTANTS.TEMP_FOLDER}/{title}-metafile")
            # Try to remove the subtitles file, we will error if it isn't found
            try:
                os.remove(f"{os.getcwd()}/{CONSTANTS.TEMP_FOLDER}/{title}.vtt")
            except FileNotFoundError:
                pass

    def download_playlist(self, playlist, base_url, title, **kwargs):
        # Check if the download directory exists
        self.create_dirs()
        # How many files we will be downloading. We will add to this 
        # when we get the total length
        files_to_download = 0
        # set the title to our title and output file
        title = os.getcwd() + "/" + CONSTANTS.TEMP_FOLDER + "/" + title

        # Get the format of the file we are downloading.
        # Result should either be aac or ts
        format = playlist.segments[0].uri.split(".")[1].rsplit("?",1)[0]

        # Timestamp of our current segment
        current_time = float(0)
        # Start and end times from the args that were passed
        end_time = float(kwargs['end_time'])
        start_from = float(kwargs['start_from'])
        # Total length of segments we want to download in seconds
        total_length = float(0)
        # Find the total length of a playlist.
        # As long as we are shorter than our end time, keep adding the segment length
        for length in playlist.segments:
            if total_length < end_time or end_time == 0:
                files_to_download += 1
                total_length += length.duration
            else:
                break

        try:
            # If we have already started to download a file and it still exists,
            # we will have a temp file called ".part". We will open it to see
            # where we will continue downloading from
            if os.path.exists(f"{title}.{format}"):
               start_from = self.read_part_file(f"{title}.{format}.part")
        except:
            pass

        # Sometimes the inputted end time is too long or if we want to download the whole video,
        # we just set the end_time to when the video itself ends.
        if end_time > total_length or end_time == 0:
            end_time = total_length

        # For as long as we haven't tried to quit the program
        try:
            for i in playlist.segments:
                if current_time >= start_from and current_time <= end_time:
                    current_file = i.uri.split(f".{format}")[0]
                    # Example: 66 ts files downloaded out of 121
                    # Note: there is a bug where it will show all of the files in the playlist
                    # even if we just want a portion of it.
                    sys.stdout.write(f"\r{current_file} {format} files downloaded out of {files_to_download}")

                    # Get the base link for the audio files and then open the URL
                    download_data = self.http.request('GET', base_url+i.uri)
                    # Now we append the data to the download file and clear the programs buffer
                    self.write_data(download_data.data, f"{title}.{format}")
                    # Clear the stdout internal buffer
                    sys.stdout.flush()
                # After adding the downloaded data, we increment the duration
                current_time += i.duration
                # Save where we are upto in the download process
                self.write_upto(current_time, f"{title}.{format}")
            # Since we downloaded the whole file we will delete out part
            #os.remove(title+"."+format+".part")
        except KeyboardInterrupt:
            # We want to cancel the current operation
            pass

        print(f"\r{format} files finished downloading")

if __name__ == "__main__":
    print("Please run python main.py instead.")
    pass
