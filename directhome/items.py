# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
import re
from scrapy.loader.processors import MapCompose, Join, TakeFirst


def strip_processor(text):
    return re.sub(r'\s+', ' ', text).strip()


class DirecthomeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field(input_processor=MapCompose(strip_processor),
                         output_processor=Join())
    url = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(input_processor=MapCompose(strip_processor),
                         output_processor=TakeFirst())
    desc = scrapy.Field(input_processor=MapCompose(strip_processor),
                        output_processor=Join('|'))
    area = scrapy.Field(input_processor=MapCompose(strip_processor),
                        output_processor=TakeFirst())
    phone = scrapy.Field(output_processor=TakeFirst())
