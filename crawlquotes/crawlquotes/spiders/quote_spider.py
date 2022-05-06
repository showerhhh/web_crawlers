import scrapy

from ..items import Quote


class QuoteSpider(scrapy.Spider):
    # 爬虫名称
    name = 'quote_spider'
    # 设置允许爬取的域(可以指定多个)
    allowed_domains = ['quotes.toscrape.com']
    # 设置起始url(设置多个)
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        for item in response.xpath('//div[@class="col-md-8"]/div[@class="quote"]'):
            text = item.xpath('./span[@class="text"]/text()').get()
            author = item.xpath('.//small[@class="author"]/text()').get()
            author_link = item.xpath('./span/a/@href').get()
            author_link = 'http://quotes.toscrape.com{}'.format(author_link)
            tags = item.xpath('.//a[@class="tag"]/text()').getall()

            i = Quote()
            i['text'] = text
            i['author'] = author
            i['author_link'] = author_link
            i['tags'] = tags
            yield i

        url = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if url is not None:
            url = 'http://quotes.toscrape.com' + url
            yield scrapy.Request(url, callback=self.parse)
