from .mongo_client import MongoDBClient


class Yad2DBClient:
    def __init__(self):
        self.client = MongoDBClient("yad2db")
        self.collection_name = "apartments"

    def save_apartment(self, apartment_data):
        self.client.insert_one(self.collection_name, apartment_data)

    def get_seen_apartments(self):
        return {
            apartment["item_id"]
            for apartment in self.client.find_all(self.collection_name)
        }
