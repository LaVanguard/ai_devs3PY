import os
import re

from dotenv import load_dotenv
from firecrawl import FirecrawlApp

load_dotenv()


class WebSearchService:
    def __init__(self):
        self.firecrawl_app = FirecrawlApp(api_key=os.environ.get("aidevs.firecrawl.api.key"))

    def scrape_url(self, url):
        try:
            url = re.sub(r'\/$', '', url)
            scrape_result = self.firecrawl_app.scrape_url(url, params={'limit': 10, 'formats': ['markdown']})
            {'crawlerOptions': {'excludes': ['blog/*']}}
            print('scrapeResult:', scrape_result)
            if scrape_result and 'markdown' in scrape_result:
                return {'url': url, 'content': scrape_result['markdown'].strip()}
            else:
                print(f'No markdown content found for URL: {url}')
                return {'url': url, 'content': ''}
        except Exception as error:
            print(f'Error scraping URL {url}:', error)
            return {'url': url, 'content': ''}
