import re
from urllib.parse import urljoin

import scrapy
from itemloaders import ItemLoader
from w3lib.url import canonicalize_url

from DnbSpider.items import DnbItem


class DnbSpider(scrapy.Spider):
    name = 'dnb'
    allowed_domains = ['dnb.com']
    start_urls = ['https://www.dnb.com/business-directory.html']

    def parse(self, response, **kwargs):
        links = response.xpath('//div[contains(@class, "industry_browse-v2")]'
                               '/div[contains(@class, "accordion_list")]'
                               '/div[@class="item col-md-12"]/div[@class="detail clearfix"]'
                               '//a/@href').extract()
        for link in links:
            url = urljoin(response.url, link)
            yield scrapy.Request(url, callback=self.parse_category)
            break

    def parse_category(self, response):
        links = response.xpath('//div[contains(@class, "industry_country_crawl")]'
                               '/div[@class="container"]/div[@class="row"]'
                               '//a/@href').extract()
        for link in links:
            url = urljoin(response.url, link)
            yield scrapy.Request(url, callback=self.parse_country)
            break

    def parse_country(self, response):
        sub_areas = response.xpath('//div[@id="locationResults"]/div'
                                   '//div[@class="col-md-6 col-xs-6 data"]/a/@href').extract()
        if sub_areas:
            for link in sub_areas:
                url = urljoin(response.url, link)
                yield scrapy.Request(url, callback=self.parse_country)
                break
        else:
            yield from self.parse_sub_area(response)

    def parse_sub_area(self, response):
        result = re.findall(r'integrated_search.pagination\((.*?)\);', response.text)
        if not result:
            self.logger.error('No pagination data')
            return

        current_page = max_pages = None
        parts = result[0].split(',')
        if len(parts) == 4:
            current_page = int(parts[0])
            # results_returned = int(parts[1])
            max_pages = int(parts[2])
            # pageRange = int(parts[3])

        rows = response.xpath('//div[@id="companyResults"]/div[@class="col-md-12 data"]'
                              '//a/@href').extract()
        for link in rows:
            url = urljoin(response.url, link)
            url = canonicalize_url(url)
            yield scrapy.Request(url, callback=self.parse_company)
            break

        if current_page and current_page < max_pages:
            parts = str(response.url).split('?page=')
            next_page = f'{parts[0]}?page={current_page + 1}'
            yield scrapy.Request(next_page, callback=self.parse_country)

    def parse_company(self, response):
        item_loader = ItemLoader(item=DnbItem(), selector=response)
        item_loader.add_xpath('name', '//div[@class="company-profile-header-title"]/text()')
        item_loader.add_xpath('website', '//a[@class="ext-icon company-website-url"]/@href')
        item_loader.add_xpath('description', '//span[@name="company_description"]/span/text()')
        item_loader.add_value('url', response.url)
        yield item_loader.load_item()


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings
    from scrapy.utils.reactor import install_reactor

    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
    process = CrawlerProcess(get_project_settings())
    process.crawl('dnb')
    process.start()
