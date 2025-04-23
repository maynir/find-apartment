from .mongo_client import MongoDBClient


class ApartmentsDBClient:
    def __init__(self):
        self.client = MongoDBClient("apartmentsdb")
        self.collection_name = "apartments"

    def save_apartment(self, apartment_data):
        self.client.insert_one(self.collection_name, apartment_data)

    def get_seen_apartments(self):
        return {
            apartment["text"]
            for apartment in self.client.find_all(self.collection_name)
        }

    def get_apartments_by_text(self, text):
        return self.client.find_one(self.collection_name, {"text": text})
