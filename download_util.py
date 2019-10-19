import urllib3
import m3u8

class download:

    def __init__(self):
        user_agent = {'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:69.0) Gecko/20100101 Firefox/69.0'}
        http = urllib3.PoolManager(headers=user_agent)
