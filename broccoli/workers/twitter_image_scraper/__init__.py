import os
import twitter
import datetime
from worker_manager.base_worker import BaseWorker
from workers.twitter import get_media_urls, get_tweet_url


SINCE_ID_KEY = 'since_id'


class TwitterImageScraper(BaseWorker):
    def __init__(self, screen_name: str, init_tweet_id: int):
        super(TwitterImageScraper, self).__init__(f"twitter_image_scraper.{screen_name}.{init_tweet_id}")
        self.screen_name = screen_name
        self.init_tweet_id = init_tweet_id
        # todo: customize count
        self.count = 10
        self.twitter_api = None

    def pre_work(self):
        self.twitter_api = twitter.Api(
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
            access_token_key=os.getenv("TWITTER_ACCESS_TOKEN_KEY"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )

    def work(self):
        if not self.metadata_store.exists(SINCE_ID_KEY):
            self.metadata_store.set(SINCE_ID_KEY, self.init_tweet_id)
        since_tweet_id = self.metadata_store.get(SINCE_ID_KEY)

        tweets = self.twitter_api.GetUserTimeline(
            screen_name=self.screen_name,
            since_id=since_tweet_id,
            count=self.count
        )
        if not tweets:
            self.logger.info(f"No tweet to process")
            return

        new_documents = []
        for tweet in tweets:
            for image_url in get_media_urls(tweet, "photo", self.logger):
                new_documents.append({
                    "image_url": image_url,
                    "source": get_tweet_url(tweet),
                    'created_at': datetime.datetime.utcnow()
                })
        for new_document in new_documents:
            self.rpc_client.blocking_append(idempotency_key="image_url", doc=new_document)

        max_tweet_id = max(tweets, key=lambda t: t.id).id
        self.metadata_store.set(SINCE_ID_KEY, max_tweet_id)
