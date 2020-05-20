import twitter.models
import logging
from typing import List


def get_media_urls(tweet: twitter.models.Status, media_type: str, logger: logging.Logger) -> List[str]:
    if not tweet.media:
        logger.debug(f"{tweet} does not have media")
        return []
    urls = []
    for index, media in enumerate(tweet.media):
        if not media.type:
            logger.warning(f"Media {media} at index {index} for {tweet} does not have type")
            continue
        if media.type != media_type:
            logger.debug(f"Skip media {media} at index {index} for {tweet} of type {media.type}")
            continue
        if not media.media_url:
            logger.warning(f"Media {media} at index {index} for {tweet} does not have media_url")
            continue
        urls.append(media.media_url)
    return urls


def get_tweet_url(tweet: twitter.models.Status) -> str:
    return f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
