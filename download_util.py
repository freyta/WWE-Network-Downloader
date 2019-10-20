import urllib3, certifi
import m3u8
import datetime
import sys
import subprocess

HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}

class download:

    def __init__(self):
        self.http = urllib3.PoolManager(headers=HEADERS,
                                   cert_reqs='CERT_REQUIRED',
                                   ca_certs=certifi.where())


    def get_index_m3u8(self, link):
        # Return the contents of the m3u8 playlist
        return(self.http.request('GET', link))

    def get_playlist_object(self, link):
        # Return the playlist as an object
        return(m3u8.loads(self.http.request('GET', link).data.decode('utf-8')))

    def download_playlist(self, playlist, base_url, title, start_from=0, end_time=336):
        # Get the amount of files in the playlist
        files_to_download = len(playlist.segments)
        # Timestamp of our current segment
        current_time = float(0)
        # Get the format of the file we are downloading.
        # Result should either be aac or ts
        format = playlist.segments[0].uri.split(".")[1].rsplit("?",1)[0]

        # For as long as we haven't tried to quit the program
        try:
            for i in playlist.segments:
                current_time += i.duration
                if(current_time >= start_from and current_time <= end_time):
                    sys.stdout.write("\r{} {} files downloaded out of {}".format(i.uri.split('.{}'.format(format))[0], format, files_to_download))

                    # Get the base link for the audio files and then open the URL
                    download_data = self.http.request('GET', base_url+i.uri)

                    # Now we append the data to the download file and clear the programs buffer
                    f= open("/mnt/DATA/Python/wwe_network_2/out/{}.{}".format(title, format),"ab+")
                    f.write(download_data.data)
                    f.flush()
                    sys.stdout.flush()

        except KeyboardInterrupt:
            pass
