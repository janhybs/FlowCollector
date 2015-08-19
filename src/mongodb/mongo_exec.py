# encoding: utf-8
# author:   Jan Hybs
import re

from bson.regex import Regex
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
        cond_id = self.create_conditions(json_data)

        self.ensure_structure_path(whole_program, path=None, cond_id=cond_id)
        # self.insert_data(whole_program, cond_id)

    def close(self):
        pass

    def commit(self):
        pass

    def clean_database (self):
        print self.ist.remove ({})
        print self.metrics.remove ({})
        print self.cond.remove ({})


    # ------------------------------ // db.cond.aggregate({$group: {_id: "", max: {$avg: "$task-size"}


    def ensure_structure_path(self, json_data, cond_id, path=None):
        tag = json_data['tag']
        if not path:
            ist_id = ",{:s},".format(tag)
        else:
            ist_id = "{:s}{:s},".format(path, tag)
            parent = self.ist.find_one({ '_id': path })
            # if parent is valid
            if parent:
                # and current reference is not in parents children list
                if ist_id not in parent['children']:
                    self.ist.update_one({ '_id': path }, {
                        "$push": {
                            "children": ist_id
                        }
                    })

        result = self.ist.find_one({ '_id': ist_id })

        # if no such tag exists
        if not result:
            # create one
            self.ist.insert_one({
                '_id': ist_id,
                'tag': json_data['tag'],  # save parsing path
                'children': [],  # save one potential query for children lookup
                'parent': path
            })

        data = json_data.copy()
        data.update({
            'ist_id': ist_id,
            'cond_id': cond_id
        })
        data.pop('children', None)
        self.metrics.insert_one(data)

        if 'children' in json_data:
            for child in json_data['children']:
                self.ensure_structure_path(child, cond_id, ist_id)

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
                'children': []  # save one potential query for children lookup
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
        data.update({
            'ist_id': json_data['tag'],
            'cond_id': cond_id
        })
        data.pop('children', None)
        self.metrics.insert_one(data)

        if 'children' in json_data:
            for child in json_data['children']:
                self.insert_data(child, cond_id)

    def get_ist_item(self, path=",Whole Program,", starting=False, ending=True):
        if type(path) is not list:
            path = [path]

        patterns = []
        for p in path:
            patterns.append(("^" if starting else "") + p + ("$" if ending else ""))

        pattern = re.compile("|".join(patterns))
        regex = Regex.from_native(pattern)
        regex.flags ^= re.UNICODE
        return self.ist.find({ "_id": regex })

    def get_ist_by_id(self, id=",Whole Program,"):
        return self.ist.find_one({ "_id": id })

    def pluck_fields(self, collection=None, fields=['cumul-time', 'call-count'], group=None, match=None):
        collection = self.metrics if collection is None else collection

        # single fields converts to list
        # simple string match converts to _id search
        fields = [fields] if type(fields) is not list else fields
        match = {'_id': match} if type(match) is str else match

        # create match and group object
        match_dict = { '$match': match }
        group_dict = { '$group': { '_id': group }}

        # add fields
        for field in fields:
            group_dict['$group']['data' if field == '_id' else field] = { '$push':'$' + field }

        # create pipeline and send command
        pipeline = [match_dict, group_dict]
        # print pipeline
        return list(collection.aggregate (pipeline))[0]


    def pluck_field(self, id=",Whole Program,", pluck_field="cumul-time", collection='metrics', match_field='ist_id'):

        pipeline = [
            {
                '$match': { match_field: id }
            },
            {
                '$group': {
                    '_id': '$ist_id',
                    'data': { '$push': "$" + pluck_field }
                }
            }
        ]
        # print 'db.metrics.aggregate({:s})'.format(pipeline)
        if collection == 'metrics':
            return self.metrics.aggregate(pipeline)
        if collection == 'cond':
            return self.cond.aggregate(pipeline)
        if collection == 'ist':
            return self.ist.aggregate(pipeline)
