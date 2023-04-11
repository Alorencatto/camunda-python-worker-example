import pymongo
import os
from dotenv import load_dotenv
from typing import Union, List

load_dotenv()


class Database(object):
    URI: str = os.environ.get("MONGO_DB_URI")
    DATABASE = None

    @staticmethod
    def initialize():
        client = pymongo.MongoClient(Database.URI)
        Database.DATABASE = client['dev']

    @staticmethod
    def insert(collection: str, data: Union[List[dict], dict]) -> None:
        # Database.DATABASE[collection].insert(data)
        Database.DATABASE['camunda_dev'].insert(data)

