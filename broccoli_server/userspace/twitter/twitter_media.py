import twitter.models
from typing import Optional


class TwitterMedia(object):
    def __init__(self,
                 media_type: str,
                 media_url: str,
                 parent_status: twitter.models.Status,
                 original_status: twitter.models.Status = None
                 ):
        self.media_type = media_type  # type: str
        self.media_url = media_url  # type: str
        self.parent_status = parent_status  # type: twitter.models.Status
        self.original_status = original_status  # type: Optional[twitter.models.Status]
