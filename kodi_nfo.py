import json, random
import requests
import arrow
#from main import make_safe_filename

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
            show_json = requests.get('https://cdn.watch.wwe.com/api/page?path={}'.format(i)).json()

            entry = show_json['entries'][0]['item']

            #try:
            # .title() makes JUL turn into Jul - camelcase.
            title = '{} {} - {}'.format(entry['customFields']['Franchise'], entry['episodeName'], entry['metadataLines'][0]['lines'][1].title())
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
            file_name = '{} {} - S{}E{} - {}'.format(entry['customFields']['Franchise'],
                                            entry['episodeName'],
                                            entry['releaseYear'],
                                            ep_num,
                                            file_date)

            # FORMAT:
            # 0 = title
            # 1 - Year + Season
            # 2 - Episode
            # 3 - Outline
            # 4 - Plot
            # 5 - aired

            nfo_text = "<episodedetails>\n\
        <title>{0}</title>\n\
        <season>{1}</season>\n\
        <episode>{2}</episode>\n\
        <outline>{3}</outline>\n\
        <plot>{4}</plot>\n\
        <id></id>\n\
        <genre>Sport</genre>\n\
        <year>{1}</year>\n\
        <aired>{5}</aired>\n\
        <studio>WWE Network</studio>\n\
        <trailer></trailer>\n\
    </episodedetails>".format(title,season,episode,description,plot,aired)

            #f= open("{}.nfo".format(file_name),"w+")
            #f.write(nfo_text)
            #print("{} is done".format(file_name))
        except:
            print("failed")
            pass
    return nfo_text, file_name

def create_episode_nfo(show_list):
    id = []
    # Get the show JSON file
    show_json = requests.get('https://cdn.watch.wwe.com/api/page?path={}'.format(show_list)).json()

    entry = show_json['entries'][0]['item']

    #try:
    # .title() makes JUL turn into Jul - camelcase.
    title = '{} {} - {}'.format(entry['customFields']['Franchise'], entry['episodeName'], entry['metadataLines'][0]['lines'][1].title())
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
    file_name = '{} {} - S{}E{} - {}'.format(entry['customFields']['Franchise'],
                                    entry['episodeName'],
                                    entry['releaseYear'],
                                    ep_num,
                                    file_date)

    # FORMAT:
    # 0 = title
    # 1 - Year + Season
    # 2 - Episode
    # 3 - Outline
    # 4 - Plot
    # 5 - aired

    nfo_text = "<episodedetails>\n\
<title>{0}</title>\n\
<season>{1}</season>\n\
<episode>{2}</episode>\n\
<outline>{3}</outline>\n\
<plot>{4}</plot>\n\
<id></id>\n\
<genre>Sport</genre>\n\
<year>{1}</year>\n\
<aired>{5}</aired>\n\
<studio>WWE Network</studio>\n\
<trailer></trailer>\n\
</episodedetails>".format(title,season,episode,description,plot,aired)

    f= open("{}.nfo".format(file_name),"w+")
    f.write(nfo_text)
    print("{} is done".format(file_name))
    

def create_show_nfo(link):
    show_json = requests.get("https://cdn.watch.wwe.com/api/page?list_page_size=100&path={}".format(link)).json()

    i = show_json['entries'][0]['item']
    title = "{} {}".format(i['customFields']['Franchise'], i['title'])
    description = i['description']
    mpaa = i['classification']['name']
    # FORMAT:
    # 0 = title
    # 1 - description
    # 2 - mpaa

    nfo_text = "<tvshow>\n\
    <title>{0}</title>\n\
    <showtitle>{0}</showtitle>\n\
    <userrating>{3}</userrating>\n\
    <outline>{1}</outline>\n\
    <plot>{1}</plot>\n\
    <mpaa>{2}</mpaa>\n\
    <genre>Sports</genre>\n\
    <studio>WWE Network</studio>\n\
</tvshow>".format(title,description,mpaa,random.randint(5,10))

    f= open("tvshow.nfo".format(make_safe_filename(title)),"w+")
    f.write(nfo_text)
    print("Saved tvshow.nfo".format(title))

    # Download the fanart
    image = requests.get("{}".format(i['images']['wallpaper']))
    open('fanart.png','wb').write(image.content)
    print("Saved fanart")

    # Download the poster
    image = requests.get("{}".format(i['images']['poster']))
    open('poster.png','wb').write(image.content)
    print("Saved poster")


'''EPISODE_URL = 'https://vccapi.kayosports.com.au/v2/content/types/landing/names/show?showCategory=15241&seasonCategory=15242&evaluate=3'
SHOW_URL = 'https://vccapi.kayosports.com.au/v2/content/types/carousel/keys/v7l3en0Y8mzE?sport=motor&series=30'

HEADERS = {'User-Agent': 'au.com.foxsports.core.App/1.1.5 (Linux;Android 8.1.0) ExoPlayerLib/2.7.3'}


s = requests.Session()
s.headers = HEADERS
i = json.loads(s.get(SHOW_URL).text)

#create_episode_nfo(i)
create_show_nfo(i, "Final")'''
