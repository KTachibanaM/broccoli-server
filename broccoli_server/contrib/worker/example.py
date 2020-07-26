from broccoli_server.interface.worker import Worker, WorkContext


class ExampleWorker(Worker):
    def __init__(self, print_str: str):
        self.print_str = print_str
        self.counter = 0

    def get_id(self) -> str:
        return "example.worker"

    def pre_work(self, context: WorkContext):
        context.logger().info("Running pre_work")

    def work(self, context: WorkContext):
        context.logger().info(f"print_str={self.print_str}")
        context.logger().info(f"counter={self.counter}")
        self.counter += 1
