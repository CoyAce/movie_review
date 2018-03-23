# _*_ coding:utf-8 _*_
import scrapy
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
import sys

from tutorial.items import FilmItem

reload(sys)
sys.setdefaultencoding('utf8')


class SearchSpider(scrapy.Spider):
    name = "douban_search"
    allowed_domains = ["douban.com"]

    def __init__(self,search_text):
        self.search_text=search_text

    def start_requests(self):
        urls = [
            ur'https://movie.douban.com/subject_search?search_text=' + self.search_text + ur'&cat=1002',
        ]
        user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
        headers = {'User-Agent': user_agent}
        for url in urls:
            yield SplashRequest(url=url.encode('utf-8'), headers=headers, callback=self.parse)

    def parse(self, response):
        filename = '%s.html' % self.search_text
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
        try:
            item_loader = ItemLoader(item=FilmItem(), response=response)
            item_loader.add_xpath('film_name', '//div[@class="title"]/a/text()')
            item_loader.add_xpath('film_url', '//div[@class="title"]/a/@href')
            item=item_loader.load_item()
            item['previous_page']=response.urljoin(response.xpath('//a[@class="prev activate"]/@href').extract_first())
            item['next_page']=response.urljoin(response.xpath('//a[@class="next"]/@href').extract_first())
        except Exception as e:
            print e
        yield item
