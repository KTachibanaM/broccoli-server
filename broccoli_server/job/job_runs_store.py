import pymongo
from typing import List
from .job_run import JobRun


class JobRunsStore(object):
    def __init__(self, connection_string: str, db: str):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[db]
        self.collection = self.db['job_runs']

    def add_job_run(self, job_run: JobRun):
        self.collection.insert_one(job_run.to_json())

    def get_job_runs_desc(self) -> List[JobRun]:
        job_runs = []
        for doc in self.collection.find().sort("_id", -1):
            job_runs.append(JobRun.from_json(doc))
        return job_runs

    def update_job_run(self, job_id: str, new_job_run: JobRun):
        self.collection.update_one(
            filter={"job_id": job_id},
            update={
                "$set": new_job_run.to_json()
            }
        )
