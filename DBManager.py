from pymongo import MongoClient

import Logger
from DataModel import User


logger = Logger.GetLogger(__name__)


class DBManager:
    def __init__(self, host="localhost", port=27017, testing=False):
        self.client = MongoClient(host, port)  # Connects to the mongo client
        try:
            address = self.client.address
            logger.info("Connected to MongoDB in %s:%d", *address)
        except:
            logger.critical("Could not connect to MongoDB, check if "
                            "is running in %s:%d", host, port)
            exit()
        if testing:
            # self.client.drop_database("test")
            self.db = self.client["test"]
        else:
            self.db = self.client["chatdb"]

    def Insert(self, obj):
        if isinstance(obj, User):
            collection = self.db["users"]
            if collection.find_one({"user": obj.user}) is not None:
                return False  # Already exist
            doc = {
                "name": obj.name, "last_name": obj.last_name,
                "user": obj.user, "password": obj.password,
                "age": obj.age, "gender": obj.gender
            }
            collection.insert_one(doc)
        return True

    def GetUser(self, user):
        if not isinstance(user, str):
            return None

        collection = self.db["users"]
        doc = collection.find_one({"user": user})
        if doc is not None:
            return User(**doc)
        else:
            return None
