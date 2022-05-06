import scrapy

from ..items import Movie


class MovieSpider(scrapy.Spider):
    # 爬虫名称
    name = 'movie_spider'
    # 设置允许爬取的域(可以指定多个)
    allowed_domains = ['movie.douban.com']
    # 设置起始url(设置多个)
    start_urls = [
        'https://movie.douban.com/typerank?type_name=%E5%96%9C%E5%89%A7%E7%89%87&type=24&interval_id=100:90&action=']

    def parse(self, response):
        '''
        是一个回调方法,起始url请求成功后,会回调这个方法
        '''
        print(response)
        movies = response.xpath('//div[@class="movie-list-panel list"]')[0]
        for movie in movies.xpath('./div'):
            movie = movie.xpath('./div[@class="movie-content-hover scaleY"]')[0]
            name = movie.xpath('.//span[@class="movie-name-text"]/a/text()').get()
            actor = movie.xpath('.//div[@class="movie-crew"]/text()').get()
            tag = movie.xpath('.//div[@class="movie-misc"]/text()').get()
            rating = movie.xpath('.//div[@class="movie-rating-hover"]/text()').get()

            movie_item = Movie()
            movie_item['name'] = name
            movie_item['actor'] = actor
            movie_item['tag'] = tag
            movie_item['rating'] = rating
            yield movie_item

            # 提取链接
            # yield scrapy.Request(url,callback=self.parse_tags_page)
