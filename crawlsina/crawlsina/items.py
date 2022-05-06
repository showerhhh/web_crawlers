# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiBoItem(scrapy.Item):
    weibo_url = scrapy.Field()  # 微博url
    content = scrapy.Field()  # 内容

    date = scrapy.Field()  # 发布时间

    user_url = scrapy.Field()  # 发布者url
    user_name = scrapy.Field()  # 发布者昵称

    transmit = scrapy.Field()  # 转发数量
    comment = scrapy.Field()  # 评论数量
    like = scrapy.Field()  # 点赞数量

    senti = scrapy.Field()  # 情感标签
    rawWeiboId = scrapy.Field()  # 原微博ID（转发微博、评论微博特有字段）


class UserItem(scrapy.Item):
    user_url = scrapy.Field()  # 用户url

    fans = scrapy.Field()  # 粉丝数量
    follow = scrapy.Field()  # 关注数量
    blog = scrapy.Field()  # 微博数量
