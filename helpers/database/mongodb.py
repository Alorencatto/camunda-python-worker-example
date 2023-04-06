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
        Database.DATABASE[collection].insert(data)

    @staticmethod
    def find(collection : str, query : dict,) -> List[dict]:
        #TODO Mudar aqui o método de limit

        try:

            if query:
                return Database.DATABASE[collection].find(query)

            return Database.DATABASE[collection].find({})

        except TypeError as e:
            print(f"Error on database get... | {str(e)}")
            return []
