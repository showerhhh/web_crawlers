import random
import time

import requests
from pyquery import PyQuery as pq


def get_one_page(session, url, params):
    time.sleep(random.random() * 5)
    response = session.get(url, params=params)
    if response.status_code != 200:
        print('An error while requesting !')
        return None
    print(response)
    return response.json()


def parse_page(json):
    if json is None:
        print('An error while parsing !')
        return None
    items = json['data']['cards']
    for item in items:
        item = item['mblog']
        weibo = {}
        weibo['id'] = item['id']
        weibo['text'] = pq(item['text']).text()
        weibo['attitudes'] = item['attitudes_count']
        weibo['comments'] = item['comments_count']
        weibo['reposts'] = item['reposts_count']
        yield weibo


def main():
    url = 'https://m.weibo.cn/api/container/getIndex'

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://m.weibo.cn/u/2830678474',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }

    s = requests.Session()
    s.headers.update(headers)

    for page in range(5):
        params = {
            'type': 'uid',
            'value': 2830678474,
            'containerid': 1076032830678474,
            'page': page,
        }
        r = get_one_page(s, url, params)
        for item in parse_page(r):
            print(item)


if __name__ == '__main__':
    main()
