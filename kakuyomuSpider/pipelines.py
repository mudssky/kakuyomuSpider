# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import pymongo
import os
import re

class KakuyomuspiderPipeline(object):
    def process_item(self, item, spider):
        return item

class SaveNovelPipeline(object):
    def save_text(self,textStr,path):
        with open(path,'w',encoding='utf8')as f:
            f.write(textStr)
        f.close()
    def convert_windowsFileName(self,filename):
        return  re.sub(r'[\/:*?"<>|\s]', " ",filename)

    # tmpDict['pageNum']
    # tmpDict['datePublished']
    # tmpDict['pageTitle']
    # tmpDict['pageUrl']
    # tmpDict['content']
    def process_item(self,item,spider):
        textStr=''
        folderName = 'publication'
        for section in item['contentList']:
            textStr+=section['pageTitle']+'\n'+section['datePublished']+'\n'+section['content']+'\n'
        filename='{title}[{author}].txt'.format(title=item.get('title'),author=item.get('author'))
        filename=self.convert_windowsFileName(filename)
        path=os.path.join(folderName,filename)
        self.save_text(textStr,path)
        spider.logger.info('save file succeed:'+path)
        with open('downloadPic.ps1','a',encoding='utf8') as f:
            downloadStr="http --download   '{coverUrl}' --output '{path}'\n".format(coverUrl=item['coverUrl'],path=(path[:-3]+'jpg').replace('\\','/') )
            f.write(downloadStr)
        f.close()
        return item

class InnsertMongodbPipeline(object):
    collection_name='publication'
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
    def process_item(self, item, spider):
        # 添加小说过大的时候的错误处理，比如之前碰到一个小说大小有20m，但是小说最大我相信不会超过30m
        try:
            insert_result=self.db[self.collection_name].insert_one(dict(item))
        except pymongo.errors.DocumentTooLarge as e:
            spider.logger.error('insert too large bson,retry to insert novels to two or more  documents')
            contentList=item['contentList'][:]
            contentListLen=len(contentList)
            partLen=200
            # python3的除法不再是默认整除，不是整除的情况会返回一个float值，所以需要整除的时候要用//
            if contentListLen%partLen==0:
                partCounts=contentListLen//partLen
            else:
                partCounts=contentListLen//partLen+1
            spider.logger.info('large contentList length is {len}, it will be insert into {partNum} documents,per part {partLen} items '.format(len=contentListLen
                                                                                                                                                   , partNum=partCounts,partLen=partLen))
            for partNum in range(0,partCounts):
                spider.logger.info('insert part {partNum}'.format(partNum=partNum))
                startIndex=partNum*partLen
                endIndex=(partNum+1)*partLen
                if endIndex>contentListLen-1:
                    endIndex=contentListLen-1
                item['contentList']=contentList[startIndex:endIndex]
                self.db[self.collection_name].insert_one(dict(item))
                spider.logger.info('insert part {partNum} completed'.format(partNum=partNum))
            item['contentList']=contentList
        spider.logger.info('insert completed： '+str(item['bookIndexUrl']))
        return item

