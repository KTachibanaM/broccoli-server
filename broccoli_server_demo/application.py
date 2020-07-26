from broccoli_server.contrib.worker import ExampleWorker
from broccoli_server.contrib.one_off_job import ExampleOneOffJob
from broccoli_server.application import Application

application = Application()
application.add_worker("example", "ExampleWorker", ExampleWorker)
application.register_one_off_job_module("example.one_off_job", ExampleOneOffJob)
