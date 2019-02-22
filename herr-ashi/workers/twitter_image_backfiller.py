import os
import twitter
from .twitter_image_scraper import TwitterImageScraper
from broccoli_plugin_base.base_worker import BaseWorker
from workers.twitter import get_media_urls, get_tweet_url


MAX_ID_KEY = 'max_id'
CURRENT_ROUND_KEY = "current_round"
MANUALLY_PAUSED_KEY = "manually_paused"


class TwitterImageBackfiller(BaseWorker):
    def __init__(self, screen_name: str, round_count: int, pause_after_round: int):
        super(TwitterImageBackfiller, self).__init__(f"twitter_image_backfiller.{screen_name}")
        self.screen_name = screen_name
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

    def work(self):
        # Initialize a max_id, round and pause metadata
        if not self.metadata_store.exists(MAX_ID_KEY):
            self.logger.info("max_id is not set, getting it")
            # todo: this is ugly
            scraper_worker_id = f"broccoli.workers.twitter_image_scraper.{self.screen_name}"
            if not self.metadata_store.exists_in_another_worker(scraper_worker_id, TwitterImageScraper.SINCE_ID_KEY):
                raise Exception(f"This worker depends on {scraper_worker_id} has done its work once and set since_id")
            init_max_id = self.metadata_store.get_from_another_worker(
                scraper_worker_id,
                TwitterImageScraper.SINCE_ID_KEY
            )
            self.metadata_store.set(MAX_ID_KEY, init_max_id)
            self.logger.info("round and pause metadata are not set, setting them")
            self.metadata_store.set(CURRENT_ROUND_KEY, 0)
            self.metadata_store.set(MANUALLY_PAUSED_KEY, True)

        # Pause processing if configured instructed
        current_round = self.metadata_store.get(CURRENT_ROUND_KEY)
        manually_paused = self.metadata_store.get(MANUALLY_PAUSED_KEY)
        should_pause = current_round == self.pause_after_round > 0 and manually_paused
        if should_pause:
            self.logger.info(f"Pause work because pause_after_round is configured (> 0) "
                             f"AND current_round has not reached pause_after_round "
                             f"AND manually_paused is true")
            return

        # Reset round and pause metadata
        if current_round == self.pause_after_round and not manually_paused:
            self.logger.info(f"Resetting current_round to 0 and manually_paused to true")
            current_round = 0
            self.metadata_store.set(CURRENT_ROUND_KEY, 0)
            self.metadata_store.set(MANUALLY_PAUSED_KEY, True)

        # Get some tweets earlier than max_id
        max_id = self.metadata_store.get(MAX_ID_KEY)
        tweets = self.twitter_api.GetUserTimeline(
            screen_name=self.screen_name,
            max_id=max_id,
            count=self.round_count
        )
        if not tweets:
            self.logger.warning(f"No tweet to process")
            return

        # Whether max_id has halted becoming smaller
        new_max_id = min(tweets, key=lambda t: t.id).id
        if new_max_id > max_id:
            raise Exception(f"max_id has halted becoming smaller, new_max_id={new_max_id} > max_id={max_id}")

        # Process the tweets
        self.logger.info(f"Going to process {len(tweets)} tweets")
        new_documents = []
        for tweet in tweets:
            for image_url in get_media_urls(tweet, "photo", self.logger):
                new_documents.append({
                    "image_url": image_url,
                    "source": get_tweet_url(tweet)
                })

        # Append the results
        self.logger.info(f"Going to append {len(new_documents)} new documents")
        for new_document in new_documents:
            self.rpc_client.blocking_append(idempotency_key="image_url", doc=new_document)

        # Write back a new max_id and increment round
        self.metadata_store.set(MAX_ID_KEY, new_max_id - 1)
        if self.pause_after_round > 0 and current_round < self.pause_after_round:
            self.metadata_store.set(CURRENT_ROUND_KEY, current_round + 1)
