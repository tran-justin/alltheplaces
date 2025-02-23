import re

from scrapy.spiders import SitemapSpider

from locations.categories import Categories, apply_category
from locations.hours import OpeningHours, sanitise_day
from locations.items import Feature
from locations.pipelines.address_clean_up import clean_address


class PizzaHutIESpider(SitemapSpider):
    name = "pizza_hut_ie"
    item_attributes = {"brand": "Pizza Hut", "brand_wikidata": "Q191615"}
    sitemap_urls = ["https://www.pizzahutdelivery.ie/sitemap.xml"]
    sitemap_rules = [(r"pizzahutdelivery\.ie\/locations\/(?!.*\.pdf)[^\/]+(?:\/)?", "parse")]

    def parse(self, response, **kwargs):
        if address := clean_address(response.xpath('.//*[@class="store-address"]/text()').get()):
            item = Feature()
            item["ref"] = item["website"] = response.url
            item["name"] = response.xpath('.//*[@class=" xs-text-center h1-store-name"]/text()').get()
            item["addr_full"] = address
            item["phone"] = response.xpath('//a[contains(@href, "tel:")]/text()').get()
            item["opening_hours"] = OpeningHours()
            if timing := response.xpath('//*[contains(text(),"OPENING HOURS")]/parent::div').get():
                for day, open_time, close_time in re.findall(
                    r"open-hrs-name\">\s*(\w+).+?(\d+:\d+)\s*-\s*(\d+:\d+)", timing, re.DOTALL
                ):
                    if day := sanitise_day(day):
                        item["opening_hours"].add_range(day, open_time, close_time)
            apply_category(Categories.FAST_FOOD, item)
            yield item
