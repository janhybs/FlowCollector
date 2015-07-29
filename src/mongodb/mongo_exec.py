# encoding: utf-8
# author:   Jan Hybs

import pymongo
from pymongo import MongoClient


class MongoExec(object):
    def __init__(self):
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client.test
        self.collection = self.db.test

    def process_file(self, json_data):
        self.add_measurements(json_data)

    def close(self):
        pass

    def commit(self):
        pass


    # ------------------------------


    def add_measurements(self, json_data):
        data = json_data.copy()
        data.pop('children', None)
        # data['_id'] = data['task-description']

        inserted_id = self.collection.insert_one(data).inserted_id

        if 'children' in json_data:
            for child in json_data['children']:
                self.add_measurement(child, inserted_id)

    def add_measurement(self, json_data, parent_id):
        data = json_data.copy()
        data.pop('children', None)
        data['parent'] = parent_id
        # data['_id'] = data.pop('tag')
        inserted_id = self.collection.insert_one(data).inserted_id

        if 'children' in json_data:
            for child in json_data['children']:
                self.add_measurement(child, inserted_id)