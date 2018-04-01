# _*_ coding:utf-8 _*_
from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest

from tutorial.items import FilmItem


class SearchSpider(Spider):
    name = "douban_search"
    allowed_domains = ["douban.com"]

    def __init__(self, search_text, suffix):
        self.search_text = search_text
        self.suffix = suffix

    def start_requests(self):
        urls = [
            ur'https://movie.douban.com/subject_search?search_text=' + self.search_text + ur'&cat=1002' + self.suffix,
        ]
        for url in urls:
            yield SplashRequest(url=url.encode('utf-8'), callback=self.parse)

    def parse(self, response):
        # filename = '%s.html' % self.search_text
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
        try:
            item_loader = ItemLoader(item=FilmItem(), response=response)
            item_loader.add_xpath('film_name', '//div[@class="title"]/a/text()')
            item_loader.add_xpath('film_url', '//div[@class="title"]/a/@href')
            item = item_loader.load_item()
            item['previous_page'] = response.xpath('//a[@class="prev"]/@href').extract_first()
            item['next_page'] = response.xpath('//a[@class="next"]/@href').extract_first()
        except Exception as e:
            print e
        yield item
