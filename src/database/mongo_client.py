import pymongo

from etc import config


class MongoDBClient:
    def __init__(self, database_name):
        self.client = pymongo.MongoClient(config.MONGO_CONNECTION)
        self.database = self.client[database_name]

    def insert_one(self, collection_name, document):
        collection = self.database[collection_name]
        result = collection.insert_one(document)
        return result.inserted_id

    def find_one(self, collection_name, query):
        collection = self.database[collection_name]
        document = collection.find_one(query)
        return document

    def find_all(self, collection_name, query={}):
        collection = self.database[collection_name]
        documents = collection.find(query)
        return list(documents)

    def update_one(self, collection_name, query, update):
        collection = self.database[collection_name]
        result = collection.update_one(query, update)
        return result.modified_count

    def delete_one(self, collection_name, query):
        collection = self.database[collection_name]
        result = collection.delete_one(query)
        return result.deleted_count

    def close(self):
        self.client.close()
