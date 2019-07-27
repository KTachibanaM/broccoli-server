import pymongo


class Migration(object):
    SCHEMA_VERSION_COLLECTION_NAME = "schema_version"

    def __init__(self, admin_connection_string: str, db: str):
        self.client = pymongo.MongoClient(admin_connection_string)
        self.db = self.client[db]
        self.schema_version_collection = self.db[Migration.SCHEMA_VERSION_COLLECTION_NAME]

    def migrate(self):
        schema_version = self._get_schema_version()
        print(f"current schema version is {schema_version}")
        if schema_version == 0:
            print(f"performing schema migration 0 to 1")
            self._version_0_to_1()
            self._update_schema_version(1)
            print(f"performed schema migration 0 to 1")
        elif schema_version == 1:
            print(f"performing schema migration 1 to 2")
            self._version_1_to_2()
            self._update_schema_version(2)
            print(f"performed schema migration 1 to 2")
        elif schema_version == 2:
            print(f"performing schema migration 2 to 3")
            self._version_2_to_3()
            self._update_schema_version(3)
            print(f"performed schema migration 2 to 3")
        elif schema_version == 3:
            print("already on latest schema version, yay!")
        else:
            raise RuntimeError(f"unknown schema version {schema_version}, :(")

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

    def _get_schema_version(self):
        try:
            collection_names = self.db.list_collection_names()
        except Exception as e:
            print(f"fail to get collection names, {e}")
            raise e
        if Migration.SCHEMA_VERSION_COLLECTION_NAME not in collection_names:
            return 0
        try:
            v = self.schema_version_collection.find_one({"v": {"$exists": True}})
            return v["v"]
        except Exception as e:
            print(f"fail to get {Migration.SCHEMA_VERSION_COLLECTION_NAME} collection or retrieve schema version, {e}")
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
