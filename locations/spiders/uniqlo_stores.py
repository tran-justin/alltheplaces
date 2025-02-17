import scrapy

from locations.json_blob_spider import JSONBlobSpider
from locations.items import Feature

class UniqloStoreSpider(JSONBlobSpider):
    name = "uniqlo_stores"
    item_attributes = {"brand": "Uniqlo", "brand_wikidata": "Q26070"}
    locations_key = ["result", "stores"]
    limit = 50

    country_list = ["us", "eu", "th", "id", "ph", "ca", "kr", "au", "my", "sg"]

    def start_requests(self):
        for country in self.country_list:
            yield from self.fetch_page(country, 0)

    def fetch_page(self, country, offset):
        request_url = (
            f"https://map.uniqlo.com/{country}/api/storelocator/v1/en/stores?"
            f"limit={self.limit}&offset={offset}"
        )
        yield scrapy.Request(
            url=request_url,
            callback=self.parse,
            meta={"country": country, "offset": offset},
        )

    def parse(self, response):
        features = self.extract_json(response)
        yield from self.parse_feature_array(response, features)
        
        next_offset = response.meta["offset"] + self.limit
        if len(response.json().get("result", {}).get("stores", [])) == self.limit:
            yield from self.fetch_page(response.meta["country"], next_offset)

    def post_process_item(self, item: Feature, response, feature: dict):
        item["website"] = f'https://map.uniqlo.com/{response.meta["country"]}/en/detail/{feature["id"]}'
        
        yield item