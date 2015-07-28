# encoding: utf-8
# author:   Jan Hybs

import pymongo
from pymongo import MongoClient
client = MongoClient('127.0.0.1', 27017)
db = client.test
collection = db.test

def add_measurements (json_data):
    data = json_data.copy()
    data.pop('children', None)
    # data['_id'] = data['task-description']

    inserted_id = collection.insert_one (data).inserted_id

    if 'children' in json_data:
        for child in json_data['children']:
            add_measurement(child, inserted_id)

def add_measurement (json_data, parent_id):
    data = json_data.copy()
    data.pop('children', None)
    data['parent'] = parent_id
    # data['_id'] = data.pop('tag')
    inserted_id = collection.insert_one (data).inserted_id

    if 'children' in json_data:
        for child in json_data['children']:
            add_measurement(child, inserted_id)