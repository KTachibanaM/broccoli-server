import os
import twitter
import datetime
from worker_manager.base_worker import BaseWorker
from workers.twitter import get_media_urls, get_tweet_url


MAX_ID_KEY = 'max_id'
CURRENT_ROUND_KEY = "current_round"
PAUSED_KEY = "paused"


class TwitterImageBackfiller(BaseWorker):
    def __init__(self, screen_name: str, init_tweet_id: int, round_count: int, pause_after_round: int):
        super(TwitterImageBackfiller, self).__init__(f"twitter_image_backfiller.{screen_name}.{init_tweet_id}")
        self.screen_name = screen_name
        self.init_tweet_id = init_tweet_id
        self.round_count = round_count
        self.pause_after_round = pause_after_round
        self.twitter_api = None

    def pre_work(self):
        self.twitter_api = twitter.Api(
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
            access_token_key=os.getenv("TWITTER_ACCESS_TOKEN_KEY"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        self.metadata_store.set(MAX_ID_KEY, self.init_tweet_id)
        self.metadata_store.set(CURRENT_ROUND_KEY, 0)
        self.metadata_store.set(PAUSED_KEY, True)

    def work(self):
        max_tweet_id = self.metadata_store.get(MAX_ID_KEY)
        current_round = self.metadata_store.get(CURRENT_ROUND_KEY)
        paused = self.metadata_store.get(PAUSED_KEY)
        should_pause = self.pause_after_round > 0 and current_round == self.pause_after_round and paused
        if should_pause:
            self.logger.info(f"Pause work because pause_after_round={self.pause_after_round} > 0 "
                             f"AND current_round={current_round} == pause_after_round={self.pause_after_round} "
                             f"AND paused")
            return
        if current_round == self.pause_after_round and not paused:
            self.logger.info(f"Resetting current_round to 0 and paused")
            current_round = 0
            self.metadata_store.set(CURRENT_ROUND_KEY, 0)
            self.metadata_store.set(PAUSED_KEY, True)

        tweets = self.twitter_api.GetUserTimeline(
            screen_name=self.screen_name,
            max_id=max_tweet_id,
            count=self.round_count
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
                    "source": get_tweet_url(tweet),
                    'created_at': datetime.datetime.utcnow()
                })
        for new_document in new_documents:
            self.rpc_client.blocking_append(idempotency_key="image_url", doc=new_document)

        self.metadata_store.set(MAX_ID_KEY, min_tweet_id - 1)
        if self.pause_after_round > 0 and current_round < self.pause_after_round:
            self.metadata_store.set(CURRENT_ROUND_KEY, current_round + 1)
