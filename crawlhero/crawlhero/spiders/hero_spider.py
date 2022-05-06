import scrapy

from ..items import Hero


class HeroSpider(scrapy.Spider):
    name = 'hero_spider'
    allowed_domains = ['pvp.qq.com']
    start_urls = ['https://pvp.qq.com/web201605/herolist.shtml']
    base_url = 'https://pvp.qq.com/web201605/'

    def parse(self, response):
        for hero in response.xpath('//ul[@class="herolist clearfix"]/li'):
            name = hero.xpath('./a/text()').get()

            heroItem = Hero()
            heroItem['name'] = name
            yield heroItem

            nextUrl = hero.xpath('./a/@href').get()
            nextUrl = HeroSpider.base_url + nextUrl
            # print(nextUrl)
            yield scrapy.Request(url=nextUrl, callback=self.parse_profile, meta={'heroItem': heroItem})

    def parse_profile(self, response):
        heroItem = response.meta.get('heroItem')
        # skin_list = []
        # for skin in response.xpath('//ul[@class="pic-pf-list pic-pf-list3"]/li'):
        #     s = skin.xpath('./p/text()').get()
        #     skin_list.append(s)
        # heroItem['skin'] = '/'.join(skin_list)
        heroItem['skin'] = response.xpath('//ul[@class="pic-pf-list pic-pf-list3"]/@data-imgname').get()
        print(heroItem)
        yield heroItem
