from pymongo import MongoClient
import configparser

DB_CONNECTION_FILE = "db_connection/connection_params.ini"


class MongoDBConnection:
    def __init__(self, connection):
        config = configparser.ConfigParser()
        config.read(DB_CONNECTION_FILE)

        self.client = MongoClient(config[connection]["address"])

        self.database = self.client[config[connection]['database']]
        self.collection = self.database[config[connection]['collection']]

