import os
import twitter
from broccoli_plugin_base.base_worker import BaseWorker
from herr_ashi.workers.twitter import get_media_urls, get_tweet_url


class TwitterImageScraper(BaseWorker):
    SINCE_ID_KEY = 'since_id'

    def __init__(self, screen_name: str):
        super(TwitterImageScraper, self).__init__(f"twitter_image_scraper.{screen_name}")
        self.screen_name = screen_name
        # 200 is the max count we can get
        # if the user sends more than 200 tweets within a worker interval then we are going to miss some tweets
        self.count = 200
        self.twitter_api = None

    def pre_work(self):
        self.twitter_api = twitter.Api(
            consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
            consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
            access_token_key=os.getenv("TWITTER_ACCESS_TOKEN_KEY"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )

    def work(self):
        # Initialize a since_id
        if not self.metadata_store.exists(TwitterImageScraper.SINCE_ID_KEY):
            self.logger.info("since_id is not set, getting it")
            init_tweets = self.twitter_api.GetUserTimeline(screen_name=self.screen_name, count=1)
            if not init_tweets:
                raise Exception(f"Cannot obtain the initial tweets in order to get the initial since_id")
            init_since_id = max(init_tweets, key=lambda t: t.id).id
            self.metadata_store.set(TwitterImageScraper.SINCE_ID_KEY, init_since_id)

        # Get latest tweets since since_id
        since_id = self.metadata_store.get(TwitterImageScraper.SINCE_ID_KEY)
        tweets = self.twitter_api.GetUserTimeline(
            screen_name=self.screen_name,
            since_id=since_id,
            count=self.count
        )
        if not tweets:
            self.logger.info(f"No tweet to process")
            return

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

        # Write back a new since_id
        new_since_id = max(tweets, key=lambda t: t.id).id
        self.metadata_store.set(TwitterImageScraper.SINCE_ID_KEY, new_since_id)
