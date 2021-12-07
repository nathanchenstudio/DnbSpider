A Python web spider that crawls all of the companies listed on https://www.dnb.com.
[httpx](https://www.python-httpx.org/) is used to handle http2 network requests.

##Technologies
1. Python3.9
2. [Scrapy](https://scrapy.org/)
3. [httpx](https://www.python-httpx.org/)
4. [motor](https://www.google.com.hk/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjlvtjhhNH0AhV-sFYBHTpNCYkQFnoECA4QAQ&url=https%3A%2F%2Fmotor.readthedocs.io%2F&usg=AOvVaw05Zlbs02FN0QilCs7jG7_6)

##Installation
`pip install -r requirements.txt`

##Usage
Make sure "PROXY_URL" in "settings.py" is set to the URL of your proxy rotation service. To access this website, we must use residential proxies. A 403 error will be returned for non-residential proxies.

Then run the following command to start the spider:
`scrapy crawl dnb`