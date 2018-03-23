# _*_ coding:utf-8 _*_
import json
import logging
import os
import sys
from multiprocessing import Process

from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from tutorial.spiders.comment_spider import CommentSpider
from tutorial.spiders.search_spider import SearchSpider


class MovieReview():

    def __init__(self):
        reload(sys)
        sys.setdefaultencoding('utf8')
        logging.getLogger('scrapy').setLevel(logging.ERROR)
        logging.getLogger('scrapy').propagate = False
        pass

    def main(self):
        search_text = self.search_film_by_keyword()
        # Reading data back
        search_result = self.load_result()
        film_name, film_url, next_page, previous_page = self.load_data(search_result)
        number = 1
        self.show_search_result(film_name, film_url, number)
        select_key = raw_input("请选择要分析的电影：")
        while select_key != 'q':
            if select_key == 'n':
                self.crawl_wrapper(search_text, next_page)
                search_result = self.load_result()
                film_name, film_url, next_page, previous_page = self.load_data(search_result)
                number += 1
                self.show_search_result(film_name, film_url, number)
            if select_key == 'p':
                self.crawl_wrapper(search_text, previous_page)
                search_result = self.load_result()
                film_name, film_url, next_page, previous_page = self.load_data(search_result)
                number -= 1
                self.show_search_result(film_name, film_url, number)
            if select_key.isdigit():
                print '你选择的影片的subject_id是' + self.parse_subject_id(film_url, int(select_key))

            select_key = raw_input("请输入指令：")
            os.system('clear')

    def load_data(self, search_result):
        film_name = search_result['film_name']
        film_url = search_result['film_url']
        previous_page = search_result['previous_page']
        next_page = search_result['next_page']
        return film_name, film_url, next_page, previous_page

    def show_search_result(self, film_name, film_url, number):
        try:
            sequence = 1
            for i in xrange(len(film_url)):
                if "subject" in film_url[i]:
                    subject_id = self.parse_subject_id(film_url, i)
                    print "%d) name=%s subject_id=%s" % (sequence, film_name[i], subject_id)
                    sequence += 1
        except Exception as e:
            print e
        print "page: %d p:上一页 n:下一页 q：退出" % number

    @staticmethod
    def parse_subject_id(film_url, i):
        return film_url[i].split('subject')[1].replace('/', '')

    @staticmethod
    def load_result():
        with open('film_search_result.json', 'r') as f:
            search_result = json.load(f)
        return search_result

    def search_film_by_keyword(self):
        search_text = raw_input('请输入要搜索的关键词：')
        self.crawl_wrapper(search_text)
        return search_text

    def crawl_comments_wrapper(self, film_name, subject_id, suffix=''):
        p = Process(target=self.crawl_comments, args=(film_name, subject_id, suffix))
        p.start()
        p.join()

    @staticmethod
    def crawl_comments(film_name, subject_id, suffix):
        # 爬取结果
        runner = CrawlerRunner(get_project_settings())
        d = runner.crawl(CommentSpider, film_name, subject_id, suffix)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()  # the script will block here until the crawling is finished

    def crawl_wrapper(self, search_text, suffix=''):
        p = Process(target=self.crawl, args=(search_text, suffix,))
        p.start()
        p.join()

    @staticmethod
    def crawl(search_text, suffix):
        # 爬取结果
        runner = CrawlerRunner(get_project_settings())
        d = runner.crawl(SearchSpider, search_text, suffix)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    MovieReview().main()
