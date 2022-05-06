import copy
import datetime
import json
import logging

import scrapy

logger = logging.getLogger(__name__)


class SinaSpider(scrapy.Spider):
    '''crawl hot news through sina.cn and chinaso.com

    1. search news with keyword(s) in sina.cn during start_date and end_date
    2. for a certain news, search its title in chinaso.com to obtain its report status in the whole network
        such as the number and info of these similar report
    3. if similar number of this news >= 10, regard it as a hot news
        then obtain its detail content in sina.cn

    shell cmd: scrapy crawl sina -a search_level=1 -a keyword="新冠疫情" -a start_date=2020-1-1 -a end_date=2021-5-15
    '''
    name = 'sina'
    allowed_domains = ['sina.cn', 'chinaso.com']
    # start_urls = ['http://sina.com.cn/']
    start_url = 'https://sapi.sina.cn/search/list?newsId=HB-1-snhs/index_v2-search&page={}&keyword={}&tab=news'
    chinaso_cont = 'http://www.chinaso.com/v5/general/v1/web/search?q={}&pn=1&ps=1'
    chinaso_similar = 'http://www.chinaso.com/v5/general/v1/search?cont={}&rn=1000&start_index=0'

    def __init__(self, search_level, keyword, start_date, end_date, **kwargs):
        super().__init__(**kwargs)
        self.page = 1  # first news page
        self.search_level = search_level  # 0: find topic; 1: topic evolution
        self.keyword = keyword
        self.keywords = keyword.split(' ')  # split different keywords with spacing if more than one word
        self.start_date = datetime.datetime.strptime(start_date + ' 0:0:0', '%Y-%m-%d %H:%M:%S')
        self.end_date = datetime.datetime.strptime(end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S')

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_url.format(self.page, self.keyword),
            callback=self.parse,
        )

    def parse(self, response):
        '''crawl news date from sina.cn with keyword

        Args:
            response: json data
        '''
        news_list = json.loads(response.text)['data'].get('feed')
        # no news data in response, return
        if not news_list:
            return
        flag_next = False  # set flag, avoid over-searching if no suitable news in one response
        logger.info('【sina.cn】：『{}』，第 {} 页'.format(self.keyword, self.page))
        # parse news
        for news in news_list:
            # may have 'live category data' in newslist, pass it
            if news['category'] == 'live':
                continue
            item = {}
            # date of news isn't completed in sina.cn, so complete it with format 'xxxx-xx-xx'
            if not news['showTimeStr']:
                continue
            elif news['showTimeStr'].endswith('前') or news['showTimeStr'].startswith('今天'):
                news['showTimeStr'] = datetime.datetime.today()  # today
            elif news['showTimeStr'].find('月') != -1:
                news['showTimeStr'] = datetime.datetime.strptime(
                    str(datetime.date.today().year) + '年' + news['showTimeStr'], '%Y年%m月%d日 %H:%M')  # this year
            else:
                news['showTimeStr'] = datetime.datetime.strptime(
                    news['showTimeStr'], '%Y-%m-%d %H:%M')
            # only handle news in appointed range
            if not self.start_date <= news['showTimeStr'] <= self.end_date:
                continue
            # remove highlight
            news['title'] = news['title'].replace('&lt;em&gt;', '')
            news['title'] = news['title'].replace('&lt;/em&gt;', '')
            # title must contain all keyword
            flag_all = True
            for keyword in self.keywords:
                if news['title'].find(keyword) == -1:
                    flag_all = False
                    break
            if not flag_all:
                continue
            item.update({
                'title': news['title'],
                'date': news['showTimeStr'].strftime('%Y-%m-%d'),
                'source': news['source'],
                'url': news['link']
            })

            # search title in chinaso.com to get similar_num
            flag_next = True  # update flag, contain suitable news in this response
            yield scrapy.Request(
                url=self.chinaso_cont.format(item['title']),
                callback=self.parse_chinaso_cont,
                meta={
                    'item': copy.deepcopy(item),  # 深拷贝，防止结果错乱，下同
                }
            )

        # no suitable news data in response, return
        if not flag_next:
            return
        # next page
        self.page += 1
        # set limitation (20 news in one page):
        # crawl 100 pages at most for finding topics, and 20 pages for topic evolution
        if (self.search_level == '0' and self.page > 100) or (self.search_level == '1' and self.page > 20):
            return
        yield scrapy.Request(
            url=self.start_url.format(self.page, self.keyword),
            callback=self.parse,
        )

    def parse_chinaso_cont(self, response):
        '''search news title in chinaso.com to get the whole network info about this news

        the site chinaso.com will crawl news from the whole network, providing the similar report information,
        which can help us know whether a news is popular or not (by the similar_report_num)

        Args:
            response: json data
        '''
        # use method 'get' to avoid KeyError if no result
        data = json.loads(response.text)['data'].get('data')
        # title must contain all keyword
        flag_all = True
        if data:
            logger.info('【chinaso.com cont】：『{}』，相似报道数共 {} 条'.format(
                response.meta['item']['title'], data[0]['same_news_num']))
            for keyword in self.keywords:
                if data[0]['title'].find(keyword) == -1:
                    flag_all = False
                    break
        if data and flag_all and data[0]['same_news_num'] != '' and int(data[0]['same_news_num']) >= 5:
            # hot news ('flag_all == True' and 'same_news_num >= 8')
            # continue to search news' sign, for getting detail similar report info
            yield scrapy.Request(
                url=self.chinaso_similar.format(data[0]['content_sign']),
                callback=self.parse_chinaso_similar,
                meta={
                    'item': copy.deepcopy(response.meta['item']),
                    'content_sign': data[0]['content_sign'],  # could respond with blank data owing to anti-crawl
                }
            )

    def parse_chinaso_similar(self, response):
        '''parse the similar reports information

        parse to get specific number of similar reports, and source, link of these news

        Args:
            response: json data
        '''
        # for anti-crawl, the chinaso.com could respond with blank date
        # if so, request it again
        try:
            data = json.loads(response.text)['data']['data']
        except Exception:
            logger.error('【chinaso.com similar】 『{}』 返回的相似报道数据为空'.format(response.meta['item']['title']))
            # request again
            yield scrapy.Request(
                url=self.chinaso_similar.format(response.meta['content_sign']),
                callback=self.parse_chinaso_similar,
                dont_filter=True,
                meta={
                    'item': copy.deepcopy(response.meta['item']),
                    'content_sign': response.meta['content_sign'],
                }
            )
        else:
            # source and link of similar news
            similar_info = []
            for news in data:
                similar_info.append({
                    'title': news['title'],
                    'source': news['source'],
                    'url': news['url']
                })
            response.meta['item']['similar_info'] = similar_info
            # continue to crawl news' content
            yield scrapy.Request(
                url=response.meta['item']['url'],
                callback=self.parse_detail,
                meta={
                    'item': copy.deepcopy(response.meta['item']),
                }
            )

    def parse_detail(self, response):
        '''get the detail content of news in sina.cn

        Args:
            response: html data
        '''
        content_list = response.xpath('//section[contains(@class, "s_card")]//p//text()').getall()
        # for anti-crawl, the sina.cn could respond with blank date
        # if so, request it again
        if content_list:
            logger.info('【sina.cn content】 『{}』 success'.format(response.meta['item']['title']))
            response.meta['item']['content'] = ''.join(i.strip() for i in content_list)
            # yield response.meta['item']
        else:
            logger.info('【sina.cn content】 『{}』 empty'.format(response.meta['item']['title']))
            response.meta['item']['content'] = ''
            # yield scrapy.Request(
            #     url=response.meta['item']['url'],
            #     callback=self.parse_detail,
            #     dont_filter=True,
            #     meta={
            #         'item': copy.deepcopy(response.meta['item']),
            #     }
            # )
        yield response.meta['item']

