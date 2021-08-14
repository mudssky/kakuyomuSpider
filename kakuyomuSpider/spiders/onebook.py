# -*- coding: utf-8 -*-
import scrapy
import os
import pymongo
from kakuyomuSpider.items import PublicationSpiderItem

class OnebookSpider(scrapy.Spider):
    name = 'onebook'
    allowed_domains = ['kakuyomu.jp']
    start_urls = ['https://kakuyomu.jp/publication/']
    collection_name = 'publication'

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.logger.setLevel()
        self.client=pymongo.MongoClient('127.0.0.1:27017')
        self.db=self.client['kakuyomuSpider']

    def has_bookbyBookInex(self,bookIndex):
        count=self.db[self.collection_name].find({'bookIndex':bookIndex}).count()
        if count==0:
            return False
        return True
    def start_requests(self):
        if not os.path.exists('reading'):
            os.mkdir('reading')
        item = PublicationSpiderItem()
        item['bookInfoUrl'] = ''
        item['bookIndexUrl'] = 'https://kakuyomu.jp/works/1177354054881165840'
        yield scrapy.Request(url=item['bookIndexUrl'],callback=self.parse_bookIndex,meta={'item':item})

    def getOneFromReList(self,relist):
        if len(relist)==0:
            return ''
        else:
            return relist[0]


    def parse_bookIndex(self, response):
        item=response.meta['item']
        workHeaderInner = response.css('#workHeader-inner')
        if len(response.css('.isComic'))!=0:
            item['isComic'] = True
        else:
            item['isComic'] = False
        item['title'] = workHeaderInner.css('#workTitle a::text').get()
        item['catchphrase'] = response.css('#catchphrase-body::text').get()
        item['coverUrl'] = ''
        item['other_authors'] = ''
        item['author'] = workHeaderInner.css('#workAuthor-activityName a::text').get()
        item['reviews'] = workHeaderInner.css('#workPoints span::text').get()
        item['genre'] = workHeaderInner.css('#workGenre a::text').get()

        item['publisher'] = ''
        item['label'] = ''
        item['price'] = ''
        item['ISBN'] = ''
        item['shiyo'] = ''


        item['attentions'] = workHeaderInner.css('#workMeta-attention li::text').getall()
        item['keywords'] = workHeaderInner.css('#workMeta-tags li a::text').getall()
        item['introduction'] =''.join(response.css('#introduction::text').getall())+''.join(response.css('#introduction .ui-truncateTextButton-restText::text').getall())

        workInfoMain = response.css('#work-information-main')
        item['workStatus']  = self.getOneFromReList(workInfoMain.re('執筆状況[\s\S]*?dd>(.*?)</dd'))
        item['pageCountStr']  = self.getOneFromReList(workInfoMain.re('エピソード[\s\S]*?dd>(.*?)</dd'))
        item['wordsCount'] = self.getOneFromReList(workInfoMain.re('総文字数[\s\S]*?dd>(.*?)</dd'))
        item['startDate'] = workInfoMain.xpath('./div/dl/dd/time[@itemprop="datePublished"]/@datetime').get()
        item['lastModifide'] = workInfoMain.xpath('./div/dl/dd/time[@itemprop="dateModified"]/@datetime').get()
        item['commentsCount'] = self.getOneFromReList(workInfoMain.re('応援コメント[\s\S]*?<a.*?>(.*?)件</a'))
        item['followerCount'] = workInfoMain.css('.js-follow-button-follower-counter::text').get()

        toc=response.css('#table-of-contents')

        pageList = toc.css('.widget-toc-items  .widget-toc-episode-episodeTitle')

        item['pageCount'] = len(pageList)
        item['contentList'] = []
        for index,pageItem in enumerate(pageList):
            pageNum=index+1
            tmpDict={
                    'pageNum':pageNum,
                     }
            tmpDict['pageTitle'] = pageItem.css('.widget-toc-episode-titleLabel::text').get()
            tmpDict['datePublished'] = pageItem.css('.widget-toc-episode-datePublished::attr(datetime)').get()
            tmpDict['pageUrl'] = response.urljoin(pageItem.css('a::attr(href)').get())
            yield scrapy.Request(url=tmpDict['pageUrl'],callback=self.parse_contentpage,meta={'item':item,'tmpDict':tmpDict})

    def parse_contentpage(self,response):
        item = response.meta['item']
        tmpDict = response.meta['tmpDict']
        # tmpDict['content'] = ''.join(response.css('.widget-episodeBody *::text').getall())
        tmpDict['content'] = ''.join(response.css('.widget-episodeBody *').getall())
        item['contentList'].append(tmpDict)
        self.logger.info('download precessing:{currentPageNum}/{pageCount},pageUrl : {pageUrl}'.format(currentPageNum=len(item['contentList']),pageCount=item['pageCount'],pageUrl=tmpDict['pageUrl']))
        if len(item['contentList']) == item['pageCount']:
            item['contentList'] = sorted(item['contentList'], key=lambda l: l['pageNum'], reverse=False)
            yield item

        # tmpDict['pageNum']
        # tmpDict['datePublished']
        # tmpDict['pageTitle']
        # tmpDict['pageUrl']
        # tmpDict['content']

    def parse(self, response):
        pass
