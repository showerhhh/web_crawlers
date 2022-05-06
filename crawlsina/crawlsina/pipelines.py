# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import re

from .items import UserItem
from .items import WeiBoItem


class CrawlsinaPipeline:
    def process_item(self, item, spider):
        if isinstance(item, WeiBoItem):
            # 处理date字段
            date_day = item['date'][0]
            date_minute = item['date'][1].strip()
            date_minute = date_minute.split(' ')[1]
            date = date_day + ' ' + date_minute
            item['date'] = date

            # 处理content字段
            item['content'] = ''.join(i.strip() for i in item['content'])

            # 处理转发数量、评论数量、点赞数量
            transmit = re.findall(r"\d+", item['transmit'])
            comment = re.findall(r"\d+", item['comment'])
            like = re.findall(r"\d+", item['like'])
            item['transmit'] = transmit[0] if len(transmit) != 0 else '0'
            item['comment'] = comment[0] if len(comment) != 0 else '0'
            item['like'] = like[0] if len(like) != 0 else '0'

        elif isinstance(item, UserItem):
            pass
        print(item)
        return item
