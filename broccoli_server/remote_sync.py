from broccoli_server.utils import getenv_or_raise
from broccoli_server.content import ContentStore


class RemoteSync(object):
    def __init__(self):
        local_connection_string = getenv_or_raise("MONGODB_CONNECTION_STRING")
        local_db = getenv_or_raise("MONGODB_DB")
        self.local_content_store = ContentStore(
            connection_string=local_connection_string,
            db=local_db
        )

        remote_connection_string = getenv_or_raise("REMOTE_MONGODB_CONNECTION_STRING")
        remote_db = getenv_or_raise("REMOTE_MONGODB_DB")
        self.remote_content_store = ContentStore(
            connection_string=remote_connection_string,
            db=remote_db
        )

        self.actual_run = getenv_or_raise('ACTUAL_RUN') == 'true'
        self.content_idempotency_key = getenv_or_raise('CONTENT_IDEMPOTENCY_KEY')

    def run(self):
        self.local_content_store.delete_all(actual_run=self.actual_run)
        if self.actual_run:
            for content in self.remote_content_store.query({}):
                self.local_content_store.append(content, idempotency_key=self.content_idempotency_key)
