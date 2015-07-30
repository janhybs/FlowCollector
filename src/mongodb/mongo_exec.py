# encoding: utf-8
# author:   Jan Hybs

import pymongo
from pymongo import MongoClient


class MongoExec(object):
    def __init__(self):
        self.client = MongoClient('127.0.0.1', 27017)
        self.db = self.client.test

        self.ist = self.db.ist
        self.cond = self.db.cond
        self.metrics = self.db.metrics

    def process_file(self, json_data):
        whole_program = json_data['children'][0]
        self.ensure_structure(whole_program)
        cond_id = self.create_conditions(json_data)
        self.insert_data(whole_program, cond_id)

    def close(self):
        pass

    def commit(self):
        pass


    # ------------------------------


    def ensure_structure(self, json_data, parent=None):
        _id = json_data['tag']
        _parent_id = None if not parent else parent['_id']
        result = self.ist.find_one({ '_id': _id })

        # if no such tag exists
        if not result:
            # create one
            self.ist.insert_one({
                '_id': json_data['tag'],
                'parent': _parent_id,
                'children': [],
                'data': []
            })
        # if tag exists
        else:
            # and no parent is set and should be set
            if not result['parent'] and _parent_id:
                # ensure parent is set correctly
                result['parent'] = _parent_id
                self.ist.find_one_and_replace({ '_id': _id }, result)

        # if parent is valid
        if parent:
            # and current reference is not in parents children list
            if _id not in parent['children']:
                self.ist.update_one({ '_id': _parent_id }, {
                    "$push": {
                        "children": _id
                    }
                })

        if 'children' in json_data:
            for child in json_data['children']:
                self.ensure_structure(child, result)


    def create_conditions(self, json_data):
        data = json_data.copy()
        data.pop('children')
        return self.cond.insert_one(data).inserted_id

    def insert_data(self, json_data, cond_id):
        data = json_data.copy()
        data.pop('children', None)
        metric_id = self.metrics.insert_one(data).inserted_id

        _id = json_data['tag']
        self.ist.update_one({ '_id': _id }, {
            "$push": {
                'data': {
                    'metric_id': metric_id,
                    'cond_id': cond_id
                }
            }
        })

        if 'children' in json_data:
            for child in json_data['children']:
                self.insert_data(child, cond_id)

                # def add_measurements(self, json_data):
                # data = json_data.copy()
                # data.pop('children', None)
                # # data['_id'] = data['task-description']
                #
                # inserted_id = self.collection.insert_one(data).inserted_id
                #
                # if 'children' in json_data:
                #         for child in json_data['children']:
                #             self.add_measurement(child, inserted_id)
                #
                # def add_measurement(self, json_data, parent_id):
                #     data = json_data.copy()
                #     data.pop('children', None)
                #     data['parent'] = parent_id
                #     # data['_id'] = data.pop('tag')
                #     inserted_id = self.collection.insert_one(data).inserted_id
                #
                #     if 'children' in json_data:
                #         for child in json_data['children']:
                #             self.add_measurement(child, inserted_id)
