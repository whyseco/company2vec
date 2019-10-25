import re
import enchant
from urllib.parse import urlparse
from scrapy.spiders import CrawlSpider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from ..items import WebsiteItem


class GenericSpider(CrawlSpider):

    """
    A generic spider, uses type() to make new spider classes for each domain.
    This is required so that different spiders can be created when more than
    one domain is scrapped.
    """

    name = 'generic'
    allowed_domains = []
    start_urls = []

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    lang_dictionary = enchant.Dict("en_GB")

    @classmethod
    def create(cls, link):

        """
        class method to create each new spider
        :param link: URL link of domain
        :return: insantiated spider class for that domain
        """

        domain = urlparse(link).netloc.lower()
        # generate a class name such that domain www.google.com results in class name GoogleComGenericSpider
        class_name = (domain if not domain.startswith('www.') else domain[4:]).title().replace('.', '') + cls.__name__
        return type(class_name, (cls,), {
            'allowed_domains': [domain],
            'start_urls': [link],
            'name': domain
        })

    # parse each url
    def parse_item(self, response):

        """
        Ordering the response from each URL
        :param response: response from URL
        :return: list of dictionaries, with each element of list with 'company_url' and 'company_name' keys
        """

        # extract text
        item = WebsiteItem()
        item['company_url'] = response.url
        web_text = ''.join(response.xpath(
            "//*[not(self::script or self::style or self::footer)]/text()").extract())

        # clean text
        web_text = web_text.replace('\n',' ')
        web_text = web_text.replace('\t',' ')
        web_text = " ".join(web_text.split())
        web_text = re.sub(r'[^\w\s]','',web_text).lower()

        # filter for english
        english_web_text = ' '.join([w for w in web_text.split() if self.lang_dictionary.check(w)])

        item['company_text'] = english_web_text

        yield item
