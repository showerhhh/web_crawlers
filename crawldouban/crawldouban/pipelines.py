# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pandas as pd


class MoviePipeline_1:
    def __init__(self):
        # 可选实现，做参数初始化等
        # doing something
        pass

    def process_item(self, item, spider):
        # item (Item 对象) – 被爬取的item
        # spider (Spider 对象) – 爬取该item的spider
        # 这个方法必须实现，每个item pipeline组件都需要调用该方法，
        # 这个方法必须返回一个 Item 对象，被丢弃的item将不会被之后的pipeline组件所处理。
        actor = item['actor']
        actor_list = actor.split('/')
        actor_list = [actor.strip() for actor in actor_list]
        actor = '/'.join(actor_list)
        item['actor'] = actor

        tag = item['tag']
        tag_list = tag.split('/')
        tag_list = [tag.strip() for tag in tag_list]
        tag = '/'.join(tag_list)
        item['tag'] = tag

        self.res.append([item['name'], item['actor'], item['tag'], item['rating']])
        return item

    def open_spider(self, spider):
        # spider (Spider 对象) – 被开启的spider
        # 可选实现，当spider被开启时，这个方法被调用。
        self.res = []
        pass

    def close_spider(self, spider):
        # spider (Spider 对象) – 被关闭的spider
        # 可选实现，当spider被关闭时，这个方法被调用
        pd.read_csv()
        res_df = pd.DataFrame(self.res, columns=['name', 'actor', 'tag', 'rating'])
        res_df.to_csv('./movies.csv', sep='\t', index=False)


class MoviePipeline_2:
    def process_item(self, item, spider):
        name = item['name']
        actor = item['actor']
        tag = item['tag']
        rating = item['rating']
        print('name={} actor={} tag={} rating={}'.format(name, actor, tag, rating))
        return item
