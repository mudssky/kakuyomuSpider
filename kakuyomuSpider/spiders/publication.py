# -*- coding: utf-8 -*-
import scrapy
import os
import pymongo
from kakuyomuSpider.items import PublicationSpiderItem

class PublicationSpider(scrapy.Spider):
    name = 'publication'
    allowed_domains = ['kakuyomu.jp']
    start_urls = ['https://kakuyomu.jp/publication/']
    collection_name = 'publication'

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client=pymongo.MongoClient('127.0.0.1:27017')
        self.db=self.client['kakuyomuSpider']
    def has_book(self,bookInfoUrl):
        count=self.db[self.collection_name].find({'bookInfoUrl':bookInfoUrl}).count()
        if count==0:
            return False
        return True
    def start_requests(self):
        if not os.path.exists('publication'):
            os.mkdir('publication')
        yield scrapy.Request(url='https://kakuyomu.jp/publication/',callback=self.parse_publicationpage)

    def parse_publicationpage(self,response):
        for bookInfoUrl in  response.css('#main-inner .work-title a::attr(href)').getall():
            item=PublicationSpiderItem()
            item['bookInfoUrl']=bookInfoUrl
            if not self.has_book(bookInfoUrl):
                yield scrapy.Request(url=bookInfoUrl,meta={'item':item},callback=self.parse_bookInfo)
        nextpage= response.css('.pager-next a::attr(href)').get()
        if nextpage is not None:
            yield scrapy.Request(url=nextpage,callback=self.parse_publicationpage)
    def getOneFromReList(self,relist):
        if len(relist)==0:
            return ''
        else:
            return relist[0]
    def parse_bookInfo(self,response):
        item=response.meta['item']
        detailView=response.css('.detailView')
        if len(detailView.css('.isComic'))!=0:
            item['isComic'] = True
        else:
            item['isComic'] = False
        item['coverUrl'] = detailView.css('.work-thumbnail img::attr(src)').get()
        item['catchphrase'] = detailView.css('.work-catchphrase::text').get()
        item['title'] = detailView.css('.work-title::text').get()
        # work-author = detailView.css('.work-author')
        item['author'] = detailView.css('.work-author a::text').get()
        item['other_authors'] = ' '.join(detailView.css('.work-author::text').getall())

        item['bookIndexUrl'] = detailView.css('.work-continueReading a::attr(href)').getall()[-1]
        work_info = detailView.css('.work-info')
        # info_list = work_info.css('div dd::text').getall()
        item['publisher'] = self.getOneFromReList(work_info.re('出版社[\s\S]*?dd>(.*?)</dd'))
        item['label'] = self.getOneFromReList(work_info.re('レーベル[\s\S]*?dd>(.*?)</dd'))
        item['on_sale'] = self.getOneFromReList(work_info.re('発売日[\s\S]*?dd>(.*?)</dd'))
        item['price'] = self.getOneFromReList(work_info.re('定価[\s\S]*?dd>(.*?)</dd'))
        item['ISBN'] = self.getOneFromReList(work_info.re('ISBN[\s\S]*?dd>(.*?)</dd'))
        item['shiyo'] = self.getOneFromReList(work_info.re('仕様[\s\S]*?dd>(.*?)</dd'))

        yield scrapy.Request(url=item['bookIndexUrl'],callback=self.parse_bookIndex,meta={'item':item})

    def parse_bookIndex(self, response):
        item=response.meta['item']
        workHeaderInner = response.css('#workHeader-inner')

        item['reviews'] = workHeaderInner.css('#workPoints span::text').get()
        item['genre'] = workHeaderInner.css('#workGenre a::text').get()

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
        tmpDict['content'] = ''.join(response.css('.widget-episodeBody *::text').getall())
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
