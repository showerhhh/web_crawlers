import copy
import datetime

import scrapy

from ..items import WeiBoItem


class WeiboSpider(scrapy.Spider):
    name = 'weibo'
    allowed_domains = ['weibo.com']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keyword = '新冠疫情'
        self.start_date = '2022-03-01'
        self.end_date = '2022-03-28'
        self.start_url = 'https://s.weibo.com/weibo?q={}&typeall=1&suball=1&timescope=custom:{}:{}&Refer=g'
        self.start_date = datetime.datetime.strptime(self.start_date + ' 0:0:0', '%Y-%m-%d %H:%M:%S')
        self.end_date = datetime.datetime.strptime(self.end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        if self.end_date > datetime.datetime.now():
            self.end_date = datetime.datetime.now()

    def start_requests(self):
        date = self.start_date
        while (date < self.end_date):
            date_str = date.strftime('%Y-%m-%d')
            url = self.start_url.format(self.keyword, date_str, date_str)
            yield scrapy.Request(
                url=url,
                callback=self.parse_weibo,
                meta={'date_day': date_str}
            )
            date += datetime.timedelta(days=1)

    def parse_weibo(self, response):
        next_url = response.xpath('//a[@class="next"]/@href').get()
        # '//div[@id="pl_feedlist_index"]c'
        if next_url is not None:
            next_url = 'https://s.weibo.com' + next_url
            yield scrapy.Request(
                url=next_url,
                callback=self.parse_weibo,
                meta=response.meta
            )

        weibo_list = response.xpath('//div[@id="pl_feedlist_index"]//div[@action-type="feed_list_item"]')
        for weibo in weibo_list:
            user = weibo.xpath('.//div[@class="card-feed"]//div[@class="info"]')
            user_url = user.xpath('.//a[@class="name"]/@href').get()
            if user_url is not None:
                user_url = 'https:' + user_url
                yield scrapy.Request(
                    url=user_url,
                    dont_filter=True,
                    callback=self.parse_user
                )
            user_name = user.xpath('.//a[@class="name"]/text()').get()

            weibo_url = weibo.xpath('.//div[@class="card-feed"]//p[@class="from"]/a[1]/@href').get()
            weibo_url = 'https:' + weibo_url
            date = weibo.xpath('.//div[@class="card-feed"]//p[@class="from"]/a[1]/text()').get()

            content = weibo.xpath('.//div[@class="card-feed"]//p[@node-type="feed_list_content"]')
            content_list = content.xpath(
                './text() | ./em[@class="s-color-red"]/text() | ./a[contains(@href, "https://s.weibo.com")]//text()').getall()

            transmit = weibo.xpath('.//div[@class="card-act"]/ul/li[1]/a/text()').get()
            comment = weibo.xpath('.//div[@class="card-act"]/ul/li[2]/a/text()').get()
            like = weibo.xpath('.//div[@class="card-act"]/ul/li[3]/a/text()').get()

            weibo_item = WeiBoItem()
            weibo_item['weibo_url'] = weibo_url
            weibo_item['content'] = content_list
            weibo_item['date'] = [response.meta['date_day'], date]
            weibo_item['user_url'] = user_url
            weibo_item['user_name'] = user_name
            weibo_item['transmit'] = transmit
            weibo_item['comment'] = comment
            weibo_item['like'] = like
            yield weibo_item

    def parse_user(self, response):
        pass

    def parse(self, response):
        # set limitation (about 15-20 weibo in one page):
        weibo_list = response.xpath('//div[@id="pl_feedlist_index"]/div[2]/div')
        # 有效数累加
        self.data_num += len(weibo_list)
        if response.xpath('//*[@id="pl_feedlist_index"]/div[3]//li[last()]') and response.meta['page'] == 1:
            # 大于1页，总数累加
            page_num = int(response.xpath('//*[@id="pl_feedlist_index"]/div[3]//li[last()]//text()').get()[1:-1])
            self.all_num += page_num * 20
        else:
            # 只有一页
            self.all_num += len(weibo_list)
        for weibo in weibo_list:
            item = {}
            if weibo.xpath('./div/div[1]/div[2]/p[2]/@node-type'):
                content = weibo.xpath('./div/div[1]/div[2]/p[@node-type="feed_list_content_full"]')
            else:
                content = weibo.xpath('./div/div[1]/div[2]/p[@node-type="feed_list_content"]')
            ret_list = content.xpath(
                './text() | ./em[@class="s-color-red"]/text() | ./a[contains(@href, "https://s.weibo.com")]//text()').getall()
            item['title'] = ''.join(i.strip() for i in ret_list)
            item['date'] = response.meta['news_date']
            # mid2url
            uid = weibo.re(r'<a href="//weibo.com/(\d+?)\?refer_flag=')[0]
            mid = weibo.xpath('./@mid').get()
            item['url'] = 'https://weibo.com/' + uid + '/' + self._mid_to_url(mid)
            # repost comment like
            temp = [i.strip() for i in weibo.xpath('./div/div[2]/ul//text()').getall()]
            item['action'] = [0, 0, 0]
            if not temp[3].endswith('发'):
                item['action'][0] = int(temp[3].split(' ')[1])
            if not temp[5].endswith('论'):
                item['action'][1] = int(temp[5].split(' ')[1])
            if temp[8]:
                item['action'][2] = int(temp[8])
            self.action_num += item['action'][0] + item['action'][1] + item['action'][2]
            # redis saves only bytes, string, int or float, ont list
            item['action'] = '{} {} {}'.format(item['action'][0], item['action'][1], item['action'][2])
            # blogger's profile
            yield scrapy.Request(
                url=self.info_url.format(uid),
                callback=self.parse_info,
                dont_filter=True,
                meta={
                    'item': copy.deepcopy(item)
                }
            )
        # next page
        next_url = response.xpath('//a[@class="next"]/@href').get()
        if not response.meta.get('hot') and next_url and response.meta['page'] < 2:
            response.meta['page'] += 1
            yield scrapy.Request(
                url='https://s.weibo.com' + next_url,
                callback=self.parse,
                meta={
                    'news_date': response.meta['news_date'],
                    'page': response.meta['page']
                }
            )

    def parse_info(self, response):
        info_list = response.xpath('//div[@class="c"][3]/text()').getall()
        if not info_list:
            yield scrapy.Request(
                url=response.url,
                callback=self.parse_info,
                dont_filter=True,
                meta={
                    'item': copy.deepcopy(response.meta['item'])
                }
            )
        else:
            info = {}
            for item in info_list:
                if item.startswith('标签'):
                    break
                try:
                    key, value = item.split(':', 1)  # english mark
                except ValueError:
                    key, value = item.split('：', 1)  # chinese mark
                info[key] = value
            if info.get('生日') and (info['生日'].startswith('19') or info['生日'].startswith('20')):
                birth_year = int(info['生日'].split('-')[0])
                age = datetime.date.today().year - birth_year
            else:
                age = -1
            response.meta['item']['source'] = info['昵称']
            response.meta['item']['profile'] = '{} {} {}'.format(info['性别'], age, info['地区'].split(' ')[0])
            yield response.meta['item']

    def _mid_to_url(self, midint):
        '''convert mid to url

        In s.weibo.com, a weibo only contains the mid, like `<div class="card-wrap" action-type="feed_list_item" mid="4647174438651605">`.
        However, `https://weibo.com/2005817001/KjNdNAiG1` is the real url of this weibo, so we need to transform the mid to url.

        1. As for the url `https://weibo.com/2005817001/KjNdNAiG1`, `2005817001` is the uid, and `KjNdNAiG1` is the transformed mid based on 62
        2. 46 4717443 8651605 ==> K jNdN AiG1
        '''
        ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

        def base62_encode(num, alphabet=ALPHABET):
            if (num == 0):
                return alphabet[0]
            arr = []
            base = len(alphabet)
            while num:
                rem = num % base
                num = num // base
                arr.append(alphabet[rem])
            arr.reverse()
            return ''.join(arr)

        midint = str(midint)[::-1]
        size = len(midint) // 7 if len(midint) % 7 == 0 else len(midint) // 7 + 1
        result = []
        for i in range(size):
            s = midint[i * 7: (i + 1) * 7][::-1]
            s = base62_encode(int(s))
            s_len = len(s)
            if i < size - 1 and len(s) < 4:
                s = '0' * (4 - s_len) + s
            result.append(s)
        result.reverse()
        return ''.join(result)
