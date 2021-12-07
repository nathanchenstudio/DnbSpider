# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

class ProxyMiddleware:

    def process_request(self, request, spider):
        if 'dont_proxy' in request.meta and request.meta['dont_proxy']:
            return
        if 'proxy' in request.meta and request.meta['proxy']:
            return

        proxy_url = spider.settings.get('PROXY_URL')
        if not proxy_url:
            return

        request.meta['proxy'] = proxy_url
