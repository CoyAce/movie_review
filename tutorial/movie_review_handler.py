# _*_ coding:utf-8 _*_
import json
import os
import sys
import urllib
from multiprocessing import Process

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor

from tutorial import text_processing

from tutorial.spiders.comment_spider import CommentSpider
from tutorial.spiders.search_spider import SearchSpider

SETTINGS = get_project_settings()


class MovieReview():

    def __init__(self):
        reload(sys)
        # configure_logging()
        sys.setdefaultencoding('utf8')
        self.svm_classifier = SVMClassifier()

    def main(self):
        film_name, film_url, next_page, number, previous_page, search_text, subject_ids = self.init_info()
        select_key = raw_input("请选择要分析的电影：")
        while select_key != 'q':
            if select_key == 'n':
                self.crawl_wrapper(search_text, next_page)
                search_result = self.load_result()
                film_name, film_url, next_page, previous_page = self.load_data(search_result)
                number += 1
                subject_ids, film_name = self.show_search_result(film_name, film_url, number)
            if select_key == 'p':
                self.crawl_wrapper(search_text, previous_page)
                search_result = self.load_result()
                film_name, film_url, next_page, previous_page = self.load_data(search_result)
                number -= 1
                subject_ids, film_name = self.show_search_result(film_name, film_url, number)
            if select_key == 'r':
                film_name, film_url, next_page, number, previous_page, search_text, subject_ids = self.init_info()
            if select_key.isdigit():
                return_code = self.sub_menu(film_name, subject_ids, int(select_key) - 1)
                if return_code == 'q':
                    return
            select_key = raw_input("请输入指令：q->quit r->reset:")
            os.system('clear')

    def init_info(self):
        search_text = self.search_film_by_keyword()
        # Reading data back
        search_result = self.load_result()
        film_name, film_url, next_page, previous_page = self.load_data(search_result)
        number = 1
        subject_ids, film_name = self.show_search_result(film_name, film_url, number)
        return film_name, film_url, next_page, number, previous_page, search_text, subject_ids

    def sub_menu(self, film_name, subject_ids, select_key):
        subject_id = subject_ids[select_key]
        print '你选择的影片的subject_id是' + subject_id
        subject_name = film_name[select_key]
        self.crawl_comments_wrapper(subject_name, subject_id)
        crawl_result = self.load_result()
        comments = crawl_result['comments']
        scores = crawl_result['scores']
        next_page = crawl_result['next_page']
        comments_number, positive_review_number = self.show_comments(comments, scores, 0, 0)
        number = 1
        print "page: %d n:下一页 q：退出 b:返回" % number
        select_key = raw_input("请输入指令：")
        while select_key != 'b' and select_key != 'q':
            if select_key == 'n':
                number += 1
                self.crawl_comments_wrapper(subject_name, subject_id, next_page)
                crawl_result = self.load_result()
                comments = crawl_result['comments']
                scores = crawl_result['scores']
                next_page = crawl_result['next_page']
                comments_number, positive_review_number = self.show_comments(comments, scores, comments_number,
                                                                             positive_review_number)
            print "page: %d n:下一页 q：退出 b:返回" % number
            select_key = raw_input("请输入指令：")
        if select_key == 'q':
            return 'q'

    def show_comments(self, comments, scores, comments_number, positive_review_number):
        target_review = text_processing.segments_all_sentences(comments)
        sentiments = self.svm_classifier.classify(target_review)
        comments_number += len(comments)
        for i in xrange(len(comments)):
            if sentiments[i] == 'pos':
                sentiment = '好评'
                positive_review_number += 1
            else:
                sentiment = '差评'
            # 处理没有评分的情况
            if i < len(scores):
                score = scores[i]
            else:
                score = '力荐'
            print "%d)评论：%s 情感分析结果：%s 用户打分：%s" % (i + 1, comments[i], sentiment, score)
        return comments_number, positive_review_number

    @staticmethod
    def load_data(search_result):
        film_name = search_result['film_name']
        film_url = search_result['film_url']
        previous_page = search_result['previous_page']
        next_page = search_result['next_page']
        return film_name, film_url, next_page, previous_page

    def show_search_result(self, film_name, film_url, number):
        filtered_subject_ids = []
        filtered_film_names = []
        try:
            sequence = 1
            for i in xrange(len(film_url)):
                if "subject" in film_url[i]:
                    subject_id = self.parse_subject_id(film_url, i)
                    print "%d) name=%s subject_id=%s" % (sequence, film_name[i], subject_id)
                    filtered_subject_ids.append(subject_id)
                    filtered_film_names.append(film_name[i])
                    sequence += 1
        except Exception as e:
            print e
        print "page: %d p:上一页 n:下一页 q：退出" % number
        return filtered_subject_ids, filtered_film_names

    @staticmethod
    def parse_subject_id(film_url, i):
        if 'subject' in film_url[i]:
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
        print film_name
        # print suffix
        # 爬取结果
        runner = CrawlerRunner(SETTINGS)
        d = runner.crawl(CommentSpider, film_name, subject_id, suffix)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()  # the script will block here until the crawling is finished

    def crawl_wrapper(self, search_text, suffix=''):
        p = Process(target=self.crawl, args=(search_text, suffix))
        p.start()
        p.join()

    @staticmethod
    def crawl(search_text, suffix):
        # 爬取结果
        runner = CrawlerRunner(SETTINGS)
        d = runner.crawl(SearchSpider, search_text, suffix)
        d.addBoth(lambda _: reactor.stop())
        reactor.run()  # the script will block here until the crawling is finished


class SVMClassifier:
    def __init__(self):
        import pickle
        self.svmclf = pickle.load(open(os.getcwd() + '/classifier.pkl'))
        with open('best_word.json', 'r') as f:
            self.best_words = set(json.load(f))

    def classify(self, target_review):
        from tutorial.feature_extractor import extract_features
        return self.svmclf.classify_many(extract_features(target_review, self.best_words))


if __name__ == '__main__':
    try:
        # MovieReview().crawl_wrapper('肖')
        # MovieReview.crawl_comments('肖申克的救赎','1292052','?start=20&limit=20&sort=new_score&status=P&percent_type=')
        # why? https://bugs.python.org/issue9405
        urllib.getproxies()
        MovieReview().main()
    except Exception as e:
        print e
