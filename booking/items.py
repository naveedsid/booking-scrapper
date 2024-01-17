# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PropertiesItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    rating_value = scrapy.Field()
    review_count = scrapy.Field()
    num_of_guests = scrapy.Field()
    accomodation_type = scrapy.Field()
    beds = scrapy.Field()
    beds_all = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()