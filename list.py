import json
import requests

URL = 'https://cdn.watch.wwe.com/api/filter/episodes?showIds=1007&page_size=100&page='
page=1

new_url = URL+str(page)
print(new_url)

json_link = requests.get(new_url).json()

total_items = json_link['size']
total_pages = json_link['paging']['total']

while(page <= total_pages):
    for i in json_link['items']:
        print('{} - {}'.format(i['firstBroadcastDate'][:10],i['metadataLines'][1]['lines'][2]))
    page += 1
    new_url = URL+str(page)

    json_link = requests.get(new_url).json()
