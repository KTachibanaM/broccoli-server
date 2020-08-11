import pymongo


class DatabaseMigration(object):
    SCHEMA_VERSION_COLLECTION_NAME = "schema_version"

    def __init__(self, admin_connection_string: str, db: str):
        self.client = pymongo.MongoClient(admin_connection_string)
        self.db = self.client[db]
        self.schema_version_collection = self.db[DatabaseMigration.SCHEMA_VERSION_COLLECTION_NAME]
        self.upgrade_map = {
            0: self._version_0_to_1,
            1: self._version_1_to_2,
            2: self._version_2_to_3,
            3: self._version_3_to_4,
            4: self._version_4_to_5,
            5: self._version_5_to_6,
            6: self._version_6_to_7,
            7: self._version_7_to_8,
            8: self._version_8_to_9
        }
        self.latest_schema_version = max(self.upgrade_map.keys()) + 1

    def migrate(self):
        current_schema_version = self._get_schema_version()
        print(f"Current schema version is {current_schema_version}")

        if current_schema_version == self.latest_schema_version:
            print(f"Already on latest schema version {self.latest_schema_version}")
            return

        upgrade_from_versions = [v for v in range(current_schema_version, self.latest_schema_version)]
        for schema_version in upgrade_from_versions:
            if schema_version not in self.upgrade_map:
                raise RuntimeError(f"Schema upgrade undefined for version {schema_version}, :(")

        for schema_version in upgrade_from_versions:
            next_schema_version = schema_version + 1
            print(f"Performing schema migration {schema_version} to {next_schema_version}")
            self.upgrade_map[schema_version]()
            self._update_schema_version(next_schema_version)
            print(f"Performed schema migration {schema_version} to {next_schema_version}")

    def assert_latest(self):
        current_schema_version = self._get_schema_version()
        if current_schema_version != self.latest_schema_version:
            raise RuntimeError(f"Aborting unless schema version is on {self.latest_schema_version}. "
                               f"Current schema version is {current_schema_version}")
        else:
            print(f"Already on latest schema version {self.latest_schema_version}")

    def _version_0_to_1(self):
        try:
            self.db["broccoli.server"].rename("repo.default")
        except Exception as e:
            print(f"fail to rename broccoli.server to repo.default, {e}")
            raise e

    def _version_1_to_2(self):
        try:
            self.db["broccoli.api.boards"].rename("boards")
        except Exception as e:
            print(f"fail to rename broccoli.api.boards to boards, {e}")
            raise e

    def _version_2_to_3(self):
        try:
            self.db["broccoli.workers"].rename("workers")
        except Exception as e:
            print(f"fail to rename broccoli.workers to workers, {e}")
            raise e

    def _version_3_to_4(self):
        try:
            for collection_name in self.db.list_collection_names():
                if collection_name.startswith("broccoli.worker"):
                    worker_states = {}
                    old_worker_collection = self.db[collection_name]
                    for worker_state in old_worker_collection.find({}):
                        worker_states[worker_state["key"]] = worker_state["value"]
                    self.db["workers"].update_one(
                        {"worker_id": collection_name},  # old worker collection name happens to be worker id
                        {"$set": {"state": worker_states}},
                        upsert=False
                    )
        except Exception as e:
            print(f"fail to migrate individual broccoli.worker.* to workers collection")
            raise e

    def _version_4_to_5(self):
        try:
            for collection_name in self.db.list_collection_names():
                if collection_name.startswith("broccoli.worker"):
                    self.db.drop_collection(collection_name)
        except Exception as e:
            print(f"fail to drop individual broccoli.worker.* collections")
            raise e

    def _version_5_to_6(self):
        try:
            old_prefix = 'broccoli.worker.'
            workers_collection = self.db['workers']
            for d in workers_collection.find():
                old_worker_id = d['worker_id']
                new_worker_id = old_worker_id
                if new_worker_id.startswith(old_prefix):
                    new_worker_id = new_worker_id[len(old_prefix):]
                workers_collection.update_one(
                    filter={'worker_id': old_worker_id},
                    update={"$set": {"worker_id": new_worker_id}}
                )
        except Exception as e:
            print("fail to remove broccoli.worker. prefix for workers")
            raise e

    def _version_6_to_7(self):
        try:
            self.db['boards'].drop()
        except Exception as e:
            print("fail to drop boards collection")
            raise e

    def _version_7_to_8(self):
        try:
            workers_collection = self.db['workers']
            for d in workers_collection.find():
                module = d['module']
                class_name = d['class_name']
                workers_collection.update_one(
                    filter={"_id": d['_id']},
                    update={
                        "$unset": {"module": "", "class_name": ""},
                        "$set": {"module_name": f"{module}.{class_name}"}
                    }
                )
        except Exception as e:
            print('fail to merge module and class name into module name for workers')
            raise e

    def _version_8_to_9(self):
        try:
            repo_collection = self.db['repo.default']
            for d in repo_collection.find():
                repo_collection.update_one(
                    filter={"_id": d['_id']},
                    update={"$unset": {"created_at": ''}}
                )
        except Exception as e:
            print('fail to remove created_at field from repo')
            raise e

    def _get_schema_version(self):
        try:
            collection_names = self.db.list_collection_names()
        except Exception as e:
            print(f"fail to get collection names, {e}")
            raise e
        if DatabaseMigration.SCHEMA_VERSION_COLLECTION_NAME not in collection_names:
            raise RuntimeError(f"schema version collection {DatabaseMigration.SCHEMA_VERSION_COLLECTION_NAME} "
                               f"is not found. Please create one with self.latest_schema_version")
        try:
            v = self.schema_version_collection.find_one({"v": {"$exists": True}})
            return v["v"]
        except Exception as e:
            print(f"fail to get {DatabaseMigration.SCHEMA_VERSION_COLLECTION_NAME} "
                  f"collection or retrieve schema version, {e}")
            raise e

    def _update_schema_version(self, new_version: int):
        try:
            self.schema_version_collection.update_one(
                {"v": {"$exists": True}},
                {"$set": {"v": new_version}},
                upsert=True
            )
        except Exception as e:
            print(f"fail to upsert schema version {new_version}, {e}")
            raise e
