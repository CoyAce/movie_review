# _*_ coding:utf-8 _*_
from scrapy import Request, Spider
from scrapy.loader import ItemLoader

from tutorial.items import FilmComment


class CommentSpider(Spider):
    name = "douban_comment"
    allowed_domains = ["douban.com"]

    def __init__(self, film_name, subject_id, suffix):
        self.film_name = film_name
        self.subject_id = subject_id
        self.suffix = suffix

    def start_requests(self):
        urls = [
            ur'https://movie.douban.com/subject/' + self.subject_id + '/comments' + self.suffix,
        ]
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': user_agent}
        for url in urls:
            yield Request(url=url.encode('utf-8'), headers=headers, callback=self.parse)

    def parse(self, response):
        # filename = '%s.html' % self.film_name
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
        try:
            item_loader = ItemLoader(item=FilmComment(), response=response)
            item_loader.add_xpath('comments', '//div[@class="comment"]/p/text()')
            item_loader.add_xpath('scores','//span[contains(@class,"allstar")]/@title')
            item = item_loader.load_item()
            item['next_page'] = response.xpath('//a[@class="next"]/@href').extract_first()
        except Exception as e:
            print e
        yield item
