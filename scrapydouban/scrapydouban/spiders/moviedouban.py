# -*- coding: utf-8 -*-
import json, scrapy, pprint
from scrapy.selector import Selector
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule


class MoviedoubanSpider(CrawlSpider):
	name = "moviedouban"
	allowed_domains = ["movie.douban.com"]
	start_urls = ["https://movie.douban.com/"]

	rules = (
        Rule(LinkExtractor(allow=r"/subject/\d+/($|\?\w+)"), 
            callback="parse_movie", follow=True),
    )

	def __init__(self):
		self.page_number = 1


	def parse_movie(self, response):
		print("RESPONSE: {}".format(response))