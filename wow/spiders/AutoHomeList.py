# -*- coding: utf-8 -*-
# 汽车之家标题采集
import scrapy
from wow.items import AutoHomeListItem
from scrapy.spiders import Spider, Rule
from scrapy.selector import Selector
from scrapy.linkextractors import LinkExtractor
import re
from scrapy.spiders import CrawlSpider


class AutoHomeListSpider(CrawlSpider):
    name = "AutoHomeList"
    allowed_domains = ["www.autohome.com.cn"]
    start_urls = (
        'http://www.autohome.com.cn/culture/',
    )
    rules = (
        Rule(LinkExtractor(allow=('culture/([\d]+)/#', ), ), callback='parse_item',follow=True),
    )

    def parse_item(self,response):
        items = []
        for sel in response.xpath('//ul[@class="article"]/li'):
            item = AutoHomeListItem()
            item['link'] = sel.xpath('a/@href').extract()
            item['title'] = sel.xpath('a/h3/text()').extract()
            if len(item['title']):
                items.append(item)
            # print repr(item).decode("unicode-escape") + '\n'
        # print items
        return items
