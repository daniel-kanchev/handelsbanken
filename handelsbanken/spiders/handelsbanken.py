import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from handelsbanken.items import Article


class HandelsbankenSpider(scrapy.Spider):
    name = 'handelsbanken'
    start_urls = ['https://vp292.alertir.com/en/node/1']

    def parse(self, response):
        links = response.xpath('//span[@class="field-content"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="pager-next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="date-display-single"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('(//div[@class="field-items"])[2]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
