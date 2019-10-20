import urllib3, certifi
import m3u8, json
import datetime
import sys, subprocess, os

HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}
OUTPUT_FOLDER = "out"

class download:

    def __init__(self):
        self.http = urllib3.PoolManager(headers=HEADERS,
                                   cert_reqs='CERT_REQUIRED',
                                   ca_certs=certifi.where())

    def create_download_dir(self):
        # If the download directory doesn't exist, we need to create it
        if not os.path.isdir("./{}".format(OUTPUT_FOLDER)):
            os.mkdir("./{}".format(OUTPUT_FOLDER))

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

    def combine_videos(self, title):
        file = OUTPUT_FOLDER + "/" + title
        subprocess.call('ffmpeg -i "{}".ts -i "{}".aac -c copy "{}".mp4'.format(file, file, file), shell=True)

    def download_playlist(self, playlist, base_url, title, **kwargs):
        # Check if the download directory exists
        self.create_download_dir()
        # Get the amount of files in the playlist
        files_to_download = len(playlist.segments)
        # set the title to our title and output file
        title = OUTPUT_FOLDER + "/" + title

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
        # Find the total length of a playlist
        for length in playlist.segments:
            total_length += length.duration

        # Sometimes the inputted end time is too long or if we want to download the whole video,
        # we just set the end_time to when the video itself ends.
        if end_time > total_length or end_time == 0:
            end_time = total_length

        # For as long as we haven't tried to quit the program
        try:
            for i in playlist.segments:
                if current_time >= start_from and current_time <= end_time:
                    current_file = i.uri.split('.{}'.format(format))[0]
                    # Example: 66 ts files downloaded out of 121
                    # Note: there is a bug where it will show all of the files in the playlist
                    # even if we just want a portion of it.
                    sys.stdout.write("\r{} {} files downloaded out of {}".format(current_file, format, files_to_download))

                    # Get the base link for the audio files and then open the URL
                    download_data = self.http.request('GET', base_url+i.uri)
                    # Now we append the data to the download file and clear the programs buffer
                    self.write_data(download_data.data, "/mnt/DATA/Python/wwe_network_2/{}.{}".format(title, format))
                    # Save where we are upto in the download process
                    self.write_upto(current_file, "/mnt/DATA/Python/wwe_network_2/{}.{}".format(title, format))
                    # Clear the stdout internal buffer
                    sys.stdout.flush()
                # After adding the downloaded data, we increment the duration
                current_time += i.duration
            # Since we downloaded the whole file we will delete out part
            os.remove(title+"."+format+".part")
        except KeyboardInterrupt:
            # We want to cancel the current operation
            pass

        print("\r{} files finished downloading".format(format))
