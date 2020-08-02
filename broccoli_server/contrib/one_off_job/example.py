import time
from broccoli_server.interface.one_off_job import OneOffJob, OneOffJobContext


class ExampleOneOffJob(OneOffJob):
    def __init__(self, wait_seconds: int, print_str: str):
        self.wait_seconds = wait_seconds
        self.print_str = print_str

    def work(self, context: OneOffJobContext):
        time.sleep(self.wait_seconds)
        context.logger().info(f"{context.content_store().count({})} items in content store")
        context.logger().info(f"print_str={self.print_str}")
