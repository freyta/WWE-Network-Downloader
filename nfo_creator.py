import json
import requests
import kodi_nfo

URL = 'https://cdn.watch.wwe.com/api/filter/episodes?showIds=1007&page_size=10&page='
page=1

new_url = URL+str(page)
print(new_url)

SHOWS = []

'''new_url = 'https://cdn.watch.wwe.com/api/filter/episodes?device=web_browser&ff=idp%2Cldp&lang=en-US&segments=au&showIds=1007&sub=l1&year=1994&page_size=100'
json_link = requests.get(new_url).json()
for i in json_link['items']:
    SHOWS.append(i['path'])
print(SHOWS)
print(kodi_nfo.create_episode_nfo(SHOWS))'''


print(kodi_nfo.create_show_nfo("/in-ring/Superstars-4837"))