# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FilmItem(scrapy.Item):
    # define the fields for your item here like:
    film_name = scrapy.Field()
    film_url = scrapy.Field()
    previous_page = scrapy.Field()
    next_page = scrapy.Field()
