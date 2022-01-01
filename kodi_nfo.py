#!/usr/bin/python3

import CONSTANTS, os
import random
import requests
import arrow


def make_safe_filename(s):
    def safe_char(c):
        if c.isalnum():
            return c
        else:
            return "_"
    return "".join(safe_char(c) for c in s).rstrip("_")

def create_multi_ep_nfo(show_list):
    print(show_list)
    id = []
    for i in show_list:
        try:
            # Get the show JSON file
            show_json = requests.get(f'https://cdn.watch.wwe.com/api/page?path={i}').json()

            entry = show_json['entries'][0]['item']

            #try:
            # .title() makes JUL turn into Jul - camelcase.
            title = f"{entry['customFields']['Franchise']} {entry['episodeName']} - {entry['metadataLines'][0]['lines'][1].title()}"
            try:
                plot = entry['description']
            except:
                plot = ""
            description = entry['shortDescription']
            episode = entry['episodeNumber']
            mpaa = entry['classification']['name']
            aired = entry['firstBroadcastDate'][:10]
            season = entry['releaseYear']

            # WWE Raw - S20E01 - 1-02-2012.avi
            file_date = arrow.get(entry['firstBroadcastDate'],'YYYY-MM-DDTHH:mm:ss')
            file_date = file_date.format('M-DD-YYYY')
            if(entry['episodeNumber'] < 10):
                ep_num = "0" + str(entry['episodeNumber'])
            else:
                ep_num = entry['episodeNumber']
            file_name = f"{entry['customFields']['Franchise']} {entry['episodeName']}\
                - S{entry['releaseYear']}E{ep_num} - {file_date}"

            # FORMAT:
            # 0 = title
            # 1 - Year + Season
            # 2 - Episode
            # 3 - Outline
            # 4 - Plot
            # 5 - aired

            nfo_text = f"<episodedetails>\n\
        <title>{title}</title>\n\
        <season>{season}</season>\n\
        <episode>{episode}</episode>\n\
        <outline>{description}</outline>\n\
        <plot>{plot}</plot>\n\
        <id></id>\n\
        <genre>Sport</genre>\n\
        <year>{season}</year>\n\
        <aired>{aired}</aired>\n\
        <studio>WWE Network</studio>\n\
        <trailer></trailer>\n\
    </episodedetails>"

            #f= open("{}.nfo".format(file_name),"w+")
            #f.write(nfo_text)
            #print("{} is done".format(file_name))
        except:
            print("failed")
            pass
    return nfo_text, file_name

def create_episode_nfo(url, series_folder, file_name = None):
    id = []
    # Get the show JSON file
    show_json = requests.get(f'https://cdn.watch.wwe.com/api/page?path={url}').json()

    entry = show_json['entries'][0]['item']

    #try:
    # .title() makes JUL turn into Jul - camelcase.
    title = entry['title']
    try:
        plot = entry['description']
    except:
        plot = ""

    description = entry['shortDescription']
    if(description == "-1"):
        description = plot
    try:
        episode = entry['episodeNumber']
    except KeyError:
        episode = 0
    # Some episodes are specials which haven't got an episode number
    # i.e. https://watch.wwe.com/episode/Best-Stunner-reactions-WWE-Top-10-March-15-2020-132341
    if episode <= 0:
        episode = 0

    mpaa = entry['classification']['name']
    aired = entry['firstBroadcastDate'][:10]
    season = entry['releaseYear']

    # WWE Raw - S20E01 - 1-02-2012.avi
    file_date = arrow.get(entry['firstBroadcastDate'],'YYYY-MM-DDTHH:mm:ssZ')
    file_date = file_date.format('M-DD-YYYY')
    try:
        if(entry['episodeNumber'] < 10):
            ep_num = "0" + str(entry['episodeNumber'])
        else:
            ep_num = entry['episodeNumber']
    except KeyError:
        ep_num = 0

    if (entry.get('episodeNumber') == '0'):
        ep_num = "00"

    if not file_name:
        file_name = f"{entry['customFields']['Franchise']} {entry['episodeName']} -\
                      S{entry['releaseYear']}E{ep_num} - {file_date}"

    nfo_text = f"<episodedetails>\n\
    <title>{title}</title>\n\
    <season>{season}</season>\n\
    <episode>{episode}</episode>\n\
    <outline>{description}</outline>\n\
    <plot>{plot}</plot>\n\
    <id></id>\n\
    <genre>Sport</genre>\n\
    <year>{season}</year>\n\
    <aired>{aired}</aired>\n\
    <studio>WWE Network</studio>\n\
    <trailer></trailer>\n\
</episodedetails>"


    if not os.path.isdir(f"./{CONSTANTS.OUTPUT_FOLDER}/{series_folder}"):
        os.mkdir(f"./{CONSTANTS.OUTPUT_FOLDER}/{series_folder}")

    f = open(f"{CONSTANTS.OUTPUT_FOLDER}/{series_folder}/{file_name}.nfo","w+")
    f.write(nfo_text)


# Create a Kodi compliant NFO file
def create_show_nfo(nfo_text, title, wallpaper, poster):
    print(title)
    f = open(f"{CONSTANTS.OUTPUT_FOLDER}/{title}/tvshow.nfo", "w+").write(nfo_text)

    # Download the fanart
    image = requests.get(wallpaper)
    open(f"{CONSTANTS.OUTPUT_FOLDER}/{title}/fanart.png", "wb").write(image.content)
    print("Saved fanart")

    # Download the poster
    image = requests.get(poster)
    open(f"{CONSTANTS.OUTPUT_FOLDER}/{title}/poster.png", "wb").write(image.content)
    print("Saved poster")

# Get the basics for our Kodi NFO and the series name
def get_show_info(link):
    URL = f"https://cdn.watch.wwe.com/api/page?list_page_size=100&path={link}&item_detail_expand=all"
    show_json = requests.get(URL).json()

    i = show_json['entries'][0]['item']
    franchise = i['customFields']['Franchise']
    title = i['title']
    if franchise not in title[:len(franchise)]:
        title = f"{i['customFields']['Franchise']} {i['title']}"
    description = i['description']
    mpaa = i['classification']['name']
    # FORMAT:
    # 0 = title
    # 1 - description
    # 2 - mpaa

    nfo_text = f"<tvshow>\n\
    <title>{title}</title>\n\
    <showtitle>{title}</showtitle>\n\
    <userrating>{random.randint(5,10)}</userrating>\n\
    <outline>{description}</outline>\n\
    <plot>{description}</plot>\n\
    <mpaa>{mpaa}</mpaa>\n\
    <genre>Sports</genre>\n\
    <studio>WWE Network</studio>\n\
</tvshow>"

    wallpaper = i['images']['wallpaper']
    poster = i['images']['poster']
    return title, nfo_text, wallpaper, poster


if __name__ == "__main__":
    print("Please run python main.py instead.")
    pass