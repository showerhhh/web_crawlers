import json
import random
import time

import requests
from lxml import etree


class ZhiHuSpider:
    def __init__(self):
        self.pending_urls = [
            'https://www.zhihu.com/org/zuo-wen-zhi-tiao-6',
            'https://www.zhihu.com/people/jiu-yue-42-26-98',
            'https://www.zhihu.com/people/chen-bai-shi-97',
            'https://www.zhihu.com/org/zhi-hu-ri-bao-51-41',
        ]
        self.error_urls = []
        self.crawled_urls = []
        self.items = []

        headers = {
            # ':authority': 'www.zhihu.com',
            # ':method': 'GET',
            # ':scheme': 'https',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en,zh-CN;q=0.9,zh;q=0.8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36',
        }

        self.s = requests.Session()
        self.s.headers.update(headers)

    def get_one_page(self, url):
        time.sleep(random.random())
        response = self.s.get(url)
        if response.status_code == 200:
            # print(response)
            return response.text
        else:
            print('An error!')
            return None

    def test_parse_person_info(self):
        response = etree.parse('./test_parse_person_info.html', etree.HTMLParser())
        name = response.xpath('//span[@class="ProfileHeader-name"]/text()')[0]
        s_name = response.xpath('//a[@class="Button NumberBoard-item Button--plain"]/@href')[0].split('/')[2]
        follow = response.xpath(
            '//a[@class="Button NumberBoard-item Button--plain"]//strong[@class="NumberBoard-itemValue"]/text()')
        item = {
            'name': name,
            's_name': s_name,
            'following': follow[0],
            'followers': follow[1],
        }
        print(item)

    def parse_person_info(self, response):
        response = etree.HTML(response)
        name = response.xpath('//span[@class="ProfileHeader-name"]/text()')[0]
        s_name = response.xpath('//a[@class="Button NumberBoard-item Button--plain"]/@href')[0].split('/')[2]
        f = response.xpath(
            '//a[@class="Button NumberBoard-item Button--plain"]//strong[@class="NumberBoard-itemValue"]/text()')
        item = {
            'name': name,
            's_name': s_name,
            'following': f[0],
            'followers': f[1],
        }

        following_url = response.xpath('//a[@class="Button NumberBoard-item Button--plain"]/@href')[0]
        following_url = 'https://www.zhihu.com' + following_url
        following_response = self.get_one_page(following_url)
        if following_response is not None:
            self.parse_person_following(following_response)

        return item

    def test_parse_person_following(self):
        response = etree.parse('./test_parse_person_following.html', etree.HTMLParser())
        items = response.xpath('//div[@id="Profile-following"]//div[@class="List-item"]')
        for item in items:
            link = item.xpath('.//a[@class="UserLink-link"]/@href')[0]
            link = 'https:' + link
            print(link)

    def parse_person_following(self, response):
        response = etree.HTML(response)
        items = response.xpath('//div[@id="Profile-following"]//div[@class="List-item"]')
        for item in items:
            link = item.xpath('.//a[@class="UserLink-link"]/@href')[0]
            link = 'https:' + link
            self.pending_urls.append(link)

    def start(self):
        print('Start Crawl !')
        depth = 0
        while len(self.pending_urls) != 0 and depth < 3:
            for url in self.pending_urls:
                response = self.get_one_page(url)
                self.pending_urls.remove(url)
                if response is None:
                    self.error_urls.append(url)
                else:
                    self.crawled_urls.append(url)
                    item = self.parse_person_info(response)
                    self.items.append(item)
                    print(item)
            depth += 1
        with open('result.json', 'w', encoding="utf-8") as f:
            json.dump(self.items, f, ensure_ascii=False)
        print('Finish Crawl !')


if __name__ == '__main__':
    spider = ZhiHuSpider()
    spider.start()
