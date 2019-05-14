# -*- coding: utf-8 -*-
import scrapy


class PublicationSpider(scrapy.Spider):
    name = 'publication'
    allowed_domains = ['kakuyomu.jp']
    start_urls = ['http://kakuyomu.jp/']

    def parse(self, response):
        pass
