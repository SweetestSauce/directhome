import scrapy
import re
import os
from urllib.parse import urlencode, urljoin
from scrapy.loader import ItemLoader
from directhome.items import DirecthomeItem
from dotenv import load_dotenv


class HomeSpider(scrapy.Spider):
    name = 'homes'
    recursion_depth = 4

    def start_requests(self):
        params1 = urlencode({'q[listing_type_eq]': 1, 'page': 1})
        params2 = urlencode({'q[listing_type_eq]': 2, 'page': 1})
        urls = [
            'https://directhome.com.sg/listings?{}'.format(params1),
            'https://directhome.com.sg/listings?{}'.format(params2)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        load_dotenv('.env')
        email = os.environ.get('USER')
        password = os.environ.get('PWD')
        token = response.css('input[name="authenticity_token"]').attrib.get('value')
        return scrapy.FormRequest.from_response(response,
                                         formdata={'authenticity_token': token,
                                                             'user[email]': email,
                                                             'user[password]': password},
                                         callback=self.parse_listing, dont_filter=True)


    def parse_listing(self, response):
        homes = response.css('article.product-classic')
        for home in homes:
            home_url = urljoin('https://directhome.com.sg/', home.css('a::attr(href)').get())
            l = ItemLoader(item=DirecthomeItem(), selector=home)
            l.add_xpath('title', 'h4[@class="product-classic-title"]//text()')
            l.add_value('url', home_url)
            l.add_css('price', 'div.product-classic-price>span::text')
            l.add_css('desc', 'ul.product-classic-list>li>span:nth-child(2)::text')
            l.add_css('area', 'ul.product-classic-list>span:last-child::text')
            r = scrapy.Request(home_url, self.parse_home, meta={'item': l.load_item()})
            yield r
        page = int(re.search(r'(?<=&page=)\d+', response.url).group(0))
        if page >= self.recursion_depth and self.recursion_depth > 0:
            return
        next_url = re.sub(r'(?<=&page=)\d+', str(page + 1), response.url)
        yield response.follow(next_url, self.parse_listing)


    def parse_home(self, response):
        item = response.meta.get('item')
        l = ItemLoader(item=item, response=response)
        l.add_css('phone', 'p#ownerPhone>a::text')
        return l.load_item()