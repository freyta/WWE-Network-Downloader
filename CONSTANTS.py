#!/usr/bin/python3

# USERNAME AND PASSWORD
USERNAME = ""
PASSWORD = ""

# TO GET THE EPISODE JSON INFORMATION
HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}

REALM_HEADERS = {
    'x-api-key': 'cca51ea0-7837-40df-a055-75eb6347b2e7',
    'realm': 'dce.wwe'
}

# FOR THE DOWNLOADER
DOWNLOAD_HEADERS = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}
OUTPUT_FOLDER = "output"
TEMP_FOLDER = "temp"


# VIDEO SIZE INFORMATION
VIDEO_QUALITY = [10000, # 1080p high
                 6500,  # 1080p low
                 4500,  # 720p high
                 2100,  # 720p low
                 1500,  # 504p
                 1000,  # 360p
                 600]   # 288p

if __name__ == "__main__":
    print("Please run python main.py instead.")
    pass
