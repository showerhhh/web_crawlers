import json
import random
import time

import requests
from lxml import etree


def get_one_page(session, url, params):
    time.sleep(random.random() * 5)
    response = session.get(url, params=params)
    if response.status_code == 200:
        print(response)
        return response.text
    else:
        print('An error!')
        return None


def test_parse():
    response = etree.parse('./test.html', etree.HTMLParser())
    items = response.xpath('//dl[@class="board-wrapper"]/dd')
    for item in items:
        img = item.xpath('.//img[@class="board-img"]/@data-src')[0].strip()
        name = item.xpath('.//div[@class="movie-item-info"]/p[@class="name"]/a/text()')[0].strip()
        star = item.xpath('.//div[@class="movie-item-info"]/p[@class="star"]/text()')[0].strip()
        releasetime = item.xpath('.//div[@class="movie-item-info"]/p[@class="releasetime"]/text()')[0].strip()
        inte = item.xpath('.//div[@class="movie-item-number score-num"]//i[@class="integer"]/text()')[0].strip()
        frac = item.xpath('.//div[@class="movie-item-number score-num"]//i[@class="fraction"]/text()')[0].strip()
        item = {
            'img': img,
            'name': name,
            'star': star,
            'releasetime': releasetime,
            'score': inte + frac
        }
        print(item)


def parse_one_page(response):
    response = etree.HTML(response)
    items = response.xpath('//dl[@class="board-wrapper"]/dd')
    for item in items:
        img = item.xpath('.//img[@class="board-img"]/@data-src')[0].strip()
        name = item.xpath('.//div[@class="movie-item-info"]/p[@class="name"]/a/text()')[0].strip()
        star = item.xpath('.//div[@class="movie-item-info"]/p[@class="star"]/text()')[0].strip()
        releasetime = item.xpath('.//div[@class="movie-item-info"]/p[@class="releasetime"]/text()')[0].strip()
        inte = item.xpath('.//div[@class="movie-item-number score-num"]//i[@class="integer"]/text()')[0].strip()
        frac = item.xpath('.//div[@class="movie-item-number score-num"]//i[@class="fraction"]/text()')[0].strip()
        item = {
            'img': img,
            'name': name,
            'star': star,
            'releasetime': releasetime,
            'score': inte + frac
        }
        print(item)
        yield item


def main():
    url = 'http://maoyan.com/board/4'
    params = {
        'offset': 0,
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8',
        'Host': 'maoyan.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
    }

    s = requests.Session()
    s.headers.update(headers)

    # # Selenium + Headless Chrome，获取cookies，将其设置到Session中
    # options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    # browser = webdriver.Chrome(options=options)
    # browser.get('http://maoyan.com/board/4')
    # time.sleep(5)
    # cookies = browser.get_cookies()
    # browser.close()
    # for cookie in cookies:
    #     s.cookies.set(cookie['name'], cookie['value'], path=cookie['path'], domain=cookie['domain'])

    # # 手动获取cookies，将其设置到Session中
    # cookies = '__mta=222016039.1631758984904.1631791103500.1631841195554.30; uuid_n_v=v1; uuid=051604B0169511ECA0E559E0D7C43E384E0BCA8D3A974487AF659C7247DD033F; _csrf=0404f705d51c3e2e961773c41e6721cb5b67b8868729ad64491b2e05dc7f418e; Hm_lvt_703e94591e87be68cc8da0da7cbd0be2=1631758985; _lxsdk_cuid=17bec6a2674c8-09c19ab240aa24-a7d193d-1fa400-17bec6a2674c8; _lxsdk=051604B0169511ECA0E559E0D7C43E384E0BCA8D3A974487AF659C7247DD033F; Hm_lpvt_703e94591e87be68cc8da0da7cbd0be2=1631841195; _lxsdk_s=17bf150958a-08f-532-b73%7C%7C2'
    # cookies = cookies.split('; ')
    # for cookie in cookies:
    #     cookie = cookie.split('=')
    #     k = cookie[0]
    #     v = cookie[1]
    #     s.cookies.set(k, v)

    items = []
    for i in range(10):
        params['offset'] = i * 10
        response = get_one_page(s, url, params)
        if response is None:
            continue
        for item in parse_one_page(response):
            items.append(item)
    with open('result.json', 'w', encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
    # test_parse()
