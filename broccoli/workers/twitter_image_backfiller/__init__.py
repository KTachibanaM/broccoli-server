import os
import twitter
from worker_manager.base_worker import BaseWorker
from workers.twitter import get_media_urls, get_tweet_url


MAX_ID_KEY = 'max_id'


class TwitterImageBackfiller(BaseWorker):
    def __init__(self, screen_name: str, init_tweet_id: int):
        super(TwitterImageBackfiller, self).__init__(f"twitter_image_backfiller.{screen_name}.{init_tweet_id}")
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
        if not self.metadata_store.exists(MAX_ID_KEY):
            self.metadata_store.set(MAX_ID_KEY, self.init_tweet_id)
        max_tweet_id = self.metadata_store.get(MAX_ID_KEY)

        tweets = self.twitter_api.GetUserTimeline(
            screen_name=self.screen_name,
            max_id=max_tweet_id,
            count=self.count
        )
        if not tweets:
            self.logger.warning(f"No tweet to process")
            return
        self.logger.info(f"Going to process {len(tweets)} tweets")

        min_tweet_id = min(tweets, key=lambda t: t.id).id
        if min_tweet_id > max_tweet_id:
            self.logger.warning(f"min_tweet_id={min_tweet_id} > from_tweet_id={max_tweet_id}")
            return
        new_documents = []
        for tweet in tweets:
            for image_url in get_media_urls(tweet, "photo", self.logger):
                new_documents.append({
                    "image_url": image_url,
                    "source": get_tweet_url(tweet)
                })
        for new_document in new_documents:
            self.rpc_client.blocking_append(idempotency_key="image_url", doc=new_document)

        self.metadata_store.set(MAX_ID_KEY, min_tweet_id - 1)
