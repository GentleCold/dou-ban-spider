import logging
import re

import scrapy
from Douban.items import DoubanItem


class DoubanSpiterSpider(scrapy.Spider):
    name = 'douban_spider'
    allowed_domains = ['book.douban.com']
    start_urls = []

    types1 = []
    types2 = []

    tmp = open('./tmp', 'r')
    index1 = int(tmp.readline())
    index2 = int(tmp.readline())
    offset = int(tmp.readline())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open('./types', 'r', encoding='utf-8') as f:
            tmp = []
            for v in f.readlines():
                v = v.strip().split('\t')
                if len(v) == 1:
                    self.types2.append(tmp)
                    tmp = []
                    self.types1.append(v[0])
                else:
                    for t in v:
                        tmp.append(t.split('(')[0])

        logging.warning(f'initialize: {self.types1}, {self.types2}')
        self.start_urls.append(
            f'https://book.douban.com/tag/{self.types2[self.index1][self.index2]}?start={self.offset}&type=T')

    def atoi(self, s):
        if not s:
            return 0
        n = list(map(int, map(float, re.findall("\d+\.?\d*", s))))
        if len(n) > 0:
            return n[0]
        return 0

    def atof(self, s):
        if not s:
            return 0
        n = list(map(float, re.findall("\d+\.?\d*", s)))
        if len(n) > 0:
            return n[0]
        return 0

    def record(self):
        with open('./tmp', 'w') as f:
            f.writelines([str(self.index1) + '\n', str(self.index2) + '\n', str(self.offset) + '\n'])

    def finish_log(self):
        logging.warning(
            f'page finished - {self.types1[self.index1]} - {self.types2[self.index1][self.index2]} - page {self.offset / 20 + 1}')

    def parse(self, response):
        items = response.xpath(".//ul/li[@class='subject-item']")
        if len(items) == 0:
            self.offset = 0
            self.index2 += 1
            if self.index2 == len(self.types2[self.index1]):
                self.index1 += 1
                if self.index1 == len(self.types1):
                    logging.warning('---All Finish---')
                    return
                self.index2 = 0
            self.record()
            yield scrapy.Request(
                url=f'https://book.douban.com/tag/{self.types2[self.index1][self.index2]}?start={self.offset}&type=T',
                callback=self.parse)
            return

        # parse information
        for item in items:
            douban_item = DoubanItem()
            douban_item['url'] = item.xpath(".//a[@title]/@href").get()
            douban_item['title'] = item.xpath(".//a[@title]/text()").get().strip()

            content = item.xpath(".//div[@class='pub']/text()").get().replace('\n', '').replace(' ', '').split('/')
            if len(content) < 4:  # ignore book lack of information
                continue
            if self.atoi(content[-2]) == 0:  # ignore book have not price
                continue

            douban_item['author'] = content[0]
            douban_item['publisher'] = content[-3]
            douban_item['publishDate'] = content[-2]
            douban_item['price'] = self.atof(content[-1])

            douban_item['bigtype'] = self.types1[self.index1]
            douban_item['smalltype'] = response.xpath(".//div[@id='content']//h1/text()").get().split(' ')[1]

            douban_item['points'] = self.atof(item.xpath(".//span[@class='rating_nums']/text()").get())
            douban_item['commentNums'] = self.atoi(item.xpath(".//span[@class='pl']/text()").get())

            content = item.xpath(".//div[@class='info']/p/text()").get()
            if not content:  # ignore book lack of describe
                continue
            if not content.replace(' ', ''):  # ignore describe that be void
                continue

            douban_item['describe'] = content.replace('\n', '')
            douban_item['imgurl'] = item.xpath(".//img/@src").get()

            yield douban_item

        self.finish_log()
        self.record()
        self.offset += 20
        yield scrapy.Request(
            url=f'https://book.douban.com/tag/{self.types2[self.index1][self.index2]}?start={self.offset}&type=T',
            callback=self.parse)
