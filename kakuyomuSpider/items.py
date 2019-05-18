# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PublicationSpiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    bookInfoUrl =  scrapy.Field()
    coverUrl = scrapy.Field()
    catchphrase = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    isComic = scrapy.Field()
    other_authors=scrapy.Field()

    bookIndexUrl = scrapy.Field()
    introduction = scrapy.Field()

    publisher = scrapy.Field()
    on_sale = scrapy.Field()
    price = scrapy.Field()
    label = scrapy.Field()
    ISBN = scrapy.Field()
    # 仕样信息
    shiyo = scrapy.Field()

    # 书籍目录页信息
    reviews=scrapy.Field()
    genre=scrapy.Field()
    commentsCount=scrapy.Field()
    followerCount=scrapy.Field()
    attentions=scrapy.Field()
    keywords=scrapy.Field()
    introduction=scrapy.Field()
    lastModifide=scrapy.Field()
    workStatus=scrapy.Field()
    pageCountStr = scrapy.Field()
    wordsCount = scrapy.Field()
    startDate = scrapy.Field()
    pageCount = scrapy.Field()
    contentList = scrapy.Field()
    # tmpDict['pageNum']
    # tmpDict['datePublished']
    # tmpDict['pageTitle']
    # tmpDict['pageUrl']
    # tmpDict['content']

