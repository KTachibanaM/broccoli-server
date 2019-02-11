import datetime
import feedparser
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from worker_manager.base_worker import BaseWorker


LAST_CRAWLED_ID_KEY = 'last_crawled_id'


class LofterImageScraper(BaseWorker):
    def __init__(self, subdomain: str):
        super(LofterImageScraper, self).__init__(f"lofter_image_scraper.{subdomain}")
        self.rss_url = f"http://{subdomain}.lofter.com/rss"

    def pre_work(self):
        pass

    def work(self):
        # todo: timeout
        entries = feedparser.parse(self.rss_url).entries
        if not entries:
            self.logger.warning("No entries to process")
            return
        if not self.metadata_store.exists(LAST_CRAWLED_ID_KEY):
            self.logger.debug('First crawl')
            crawl_from_position = len(entries)
        else:
            last_crawled_id = self.metadata_store.get(LAST_CRAWLED_ID_KEY)
            self.logger.debug(f"Subsequent crawl with last crawled id {last_crawled_id}")
            ids = list(map(lambda e: e['link'], entries))
            if last_crawled_id in ids:
                crawl_from_position = ids.index(last_crawled_id)
                self.logger.debug(f"Last crawled position at {crawl_from_position}")
            else:
                self.logger.warning(f"Last crawled id {last_crawled_id} is not found in the feed! "
                                    f"Assuming this position is already rotated out. "
                                    f"Increase crawling frequency.")
                crawl_from_position = len(entries)

        # scrape the image urls
        new_documents = []
        new_entries = entries[: crawl_from_position]
        if not new_entries:
            self.logger.info("No new entries to process")
            return
        self.logger.info(f"{len(new_entries)} entries to process")
        for entry in new_entries:
            description = entry['description']
            source = entry['link']
            soup = BeautifulSoup(description, 'html.parser')
            for img_tag in soup.find_all('img'):
                img_src = img_tag['src']
                parsed_url = urlparse(img_src)
                sanitized_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                new_documents.append({
                    'image_url': sanitized_url,
                    'source': source,
                    'created_at': datetime.datetime.utcnow()
                })

        for new_document in new_documents:
            self.rpc_client.blocking_append(idempotency_key="image_url", doc=new_document)

        # update crawled position for next crawl
        self.metadata_store.set(key=LAST_CRAWLED_ID_KEY, value=entries[0]['link'])
