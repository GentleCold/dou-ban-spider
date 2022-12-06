# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # 保证所抓数据包含以下内容, 且保证包含有描述, 但描述是截断的
    url = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    bigtype = scrapy.Field()
    smalltype = scrapy.Field()
    publisher = scrapy.Field()
    publishDate = scrapy.Field()
    price = scrapy.Field()
    points = scrapy.Field()
    commentNums = scrapy.Field()
    describe = scrapy.Field()
    imgurl = scrapy.Field()
