import json
import requests
import re
import subprocess

def search_list(term, list):
    for i in list:
        if(term in i):
            print(term)
            exit()


show = 1007
year = 1997
# Used for episode end points
episode_list = []
episode_title = []
start_point = []
end_point = []
event_url = []

my_terms = ['The Rock',
            'Rocky',
            'Maivia']


# Make our URL from the show and year needed
URL = "https://cdn.watch.wwe.com/api/filter/episodes?device=web_browser&showIds={}&year={}&page_size=53".format(show, year)
print(URL)
# Get our potential episodes from the URL above
year_url = requests.get(URL).json()

for episode in year_url.get("items"):
    episode_list.append(episode.get("watchPath"))
    print("{} - {}".format(episode.get("firstBroadcastDate"), episode.get("watchPath")))

for event in episode_list:
    URL = "https://cdn.watch.wwe.com/api/page?path={}".format(event)

    event_json = requests.get(URL).json()

    for milestone in event_json['entries'][0]['item']['relatedItems']:
        milestone_count = 0

        for i in milestone['item']['customFields']:
            for superstar in my_terms:
                #print(superstar)
                try:
                    if re.search(superstar, milestone['item']['customFields'].get(i),re.IGNORECASE):
                        milestone_count += 1
                        title = milestone['item']['title']
                        air_date = event_json['entries'][0]['item']['firstBroadcastDate'][:10]
                        series_name = event_json['entries'][0]['title']
                        print(title)
                        episode_title.append("{} {} - {} - {}".format(air_date, series_name, milestone_count, title))
                        start_point.append(milestone['item']['customFields']['StartPoint'])
                        end_point.append(milestone['item']['customFields']['EndPoint'])
                        event_url.append(event)
                        #print(event)
                        print("{} {} - {} - {}".format(air_date, series_name, milestone_count, title))
                except TypeError:
                    pass
        try:
            print(episode_title[-1])
            print(title)
            search_list(titlex)
            exit()
        except IndexError:
            pass
                
        for superstar in my_terms:
            if re.search(superstar, milestone['item'].get('title'),re.IGNORECASE):
                milestone_count += 1
                title = milestone['item']['title']
                air_date = event_json['entries'][0]['item']['firstBroadcastDate'][:10]
                series_name = event_json['entries'][0]['title']
                episode_title.append("{} {} - {} - {}".format(air_date, series_name, milestone_count, title))
                start_point.append(milestone['item']['customFields']['StartPoint'])
                end_point.append(milestone['item']['customFields']['EndPoint'])
                event_url.append(event)
                #print(event)
                print("{} {} - {} - {}".format(air_date, series_name, milestone_count, title))

        #if(milestone_count != 0):
        #    print("{} has {} milestones".format(URL, milestone_count))


my_list = list(zip(start_point, end_point, episode_title, event_url))

print("------")
for start, end, title, url in list(set(my_list)):
    subprocess.call("python3 main.py -t {} -q 3 -e -st {} -et {} -of \"{}\"".format(url, start, end, title),shell=True)
