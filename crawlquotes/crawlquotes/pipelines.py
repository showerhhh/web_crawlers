# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json


class QuotePipeline:
    def process_item(self, item, spider):
        self.res.append(
            {
                'text': item['text'],
                'author': item['author'],
                'author_link': item['author_link'],
                'tags': item['tags'],
            }
        )

    def open_spider(self, spider):
        # 开启爬虫时调用一次
        self.res = []

    def close_spider(self, spider):
        # 关闭爬虫时调用一次
        with open('./test.json', 'w') as f:
            json.dump(self.res, f)
