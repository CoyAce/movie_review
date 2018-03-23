# _*_ coding:utf-8 _*_
import logging

import sys
from scrapy import cmdline
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from tutorial.spiders.search_spider import SearchSpider


class MovieReview():

    def __init__(self):
        reload(sys)
        sys.setdefaultencoding('utf8')
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        logging.getLogger('scrapy').propagate = False
        pass

    def main(self):
        global search_text
        search_text = raw_input('请输入要搜索的关键词：')
        # # 爬取结果
        process = CrawlerProcess(get_project_settings())
        process.crawl(SearchSpider,search_text)
        process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    MovieReview().main()
