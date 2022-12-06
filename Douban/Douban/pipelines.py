# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql


class DoubanPipeline:
    def __init__(self):
        self.db = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            database='webwork',
            charset='utf8mb4'
        )
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        # elimination of duplication
        self.cursor.execute(
            'select * from rawbooks where url = %s;',
            item['url'])

        if self.cursor.fetchone():
            return item

        ins = 'insert into rawbooks values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        self.cursor.execute(ins, [
            item['url'],
            item['title'],
            item['author'],
            item['bigtype'],
            item['smalltype'],
            item['publisher'],
            item['publishDate'],
            item['price'],
            item['points'],
            item['commentNums'],
            item['describe'],
            item['imgurl'],
        ])
        self.db.commit()
        return item
