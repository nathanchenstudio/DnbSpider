# -*- coding: utf-8 -*-
from typing import Optional
from tenacity import stop_after_attempt, wait_random_exponential, AsyncRetrying
from twisted.internet.defer import Deferred

from scrapy import signals
from scrapy.http import Request, Response, Headers
from scrapy.spiders import Spider
from scrapy.settings import Settings
from scrapy.crawler import Crawler
from scrapy.utils.defer import deferred_from_coro, deferred_f_from_coro_f
from scrapy.responsetypes import responsetypes
from scrapy.core.downloader.handlers.http import HTTPDownloadHandler
import httpx


class HttpxDownloadHandler(HTTPDownloadHandler):
    def __init__(self, settings: Settings, crawler: Optional[Crawler] = None):
        super().__init__(settings, crawler)
        self.client = None
        crawler.signals.connect(self._engine_started, signals.engine_started)

    @deferred_f_from_coro_f
    async def _engine_started(self, signal, sender):
        proxy_url = sender.settings.get('PROXY_URL')
        if proxy_url:
            proxies = {'http://': proxy_url, 'https://': proxy_url}
        else:
            proxies = None
        client = httpx.AsyncClient(http2=True,
                                   timeout=sender.settings.get('DOWNLOAD_TIMEOUT'),
                                   verify=False,
                                   proxies=proxies)
        self.client = await client.__aenter__()

    def download_request(self, request: Request, spider: Spider) -> Deferred:
        return deferred_from_coro(self._download_request(request, spider))

    async def _download_request(self, request: Request, spider: Spider) -> Response:
        async for attempt in AsyncRetrying(stop=stop_after_attempt(spider.settings.get('RETRY_TIMES')),
                                           wait=wait_random_exponential(multiplier=1, max=60)):
            with attempt:
                response = await self.client.request(request.method,
                                                     request.url,
                                                     content=request.body,
                                                     headers=request.headers.to_unicode_dict(),
                                                     cookies=request.cookies)
                headers = Headers(response.headers)
                resp_cls = responsetypes.from_args(headers=headers,
                                                   url=str(response.url),
                                                   body=response.content)
                return resp_cls(url=str(response.url),
                                status=response.status_code,
                                headers=headers,
                                body=response.content,
                                flags=["httpx"],
                                request=request,
                                protocol=response.http_version)

    @deferred_f_from_coro_f
    async def close(self):
        await self.client.__aexit__()
        await super().close()
