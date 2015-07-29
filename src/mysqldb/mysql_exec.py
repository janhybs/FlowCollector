# encoding: utf-8
# author:   Jan Hybs

import mysql.connector
from config import credentials
from mysqldb.mysql_query import insert_condition_fields, insert_condition_query, insert_measurement_query, \
    insert_structure_query


class MySQLExec(object):
    def __init__(self):
        self.connector = mysql.connector.connect(**credentials)
        self.cursor = self.connector.cursor()


    def process_file(self, json_data):
        whole_program = json_data['children'][0]
        condition_id = self.create_conditions(json_data)
        self.create_structure(whole_program, parent=None)
        self.add_measurements(whole_program, condition_id)

    def close(self):
        self.cursor.close()
        self.connector.close()

    def commit(self):
        self.connector.commit()

    # ------------------------------


    def create_conditions(self, json_data):
        data = { key: json_data[key] for key in insert_condition_fields }
        self.cursor.execute(insert_condition_query, data)

        return self.cursor.lastrowid


    def create_structure(self, json_data, parent=None):
        try:
            self.cursor.execute(insert_structure_query, { 'name': json_data['tag'], 'parent': parent })
        except mysql.connector.errors.IntegrityError as e:
            # print e
            pass

        if 'children' in json_data:
            for child in json_data['children']:
                self.create_structure(child, json_data['tag'])


    def create_measurement(self, json_data, metric, condition_id):
        return {
            'metric': metric,
            'value': json_data[metric],
            'structure': json_data['tag'],
            'cond': condition_id
        }


    def add_measurements(self, json_data, condition_id):
        # store all keys
        fields = set(json_data.keys())
        fields = fields - set(['function', 'tag', 'file-path'])

        # except children
        if 'children' in fields:
            fields.remove('children')

        for metric in fields:
            try:
                data = self.create_measurement(json_data, metric, condition_id)
                self.cursor.execute(insert_measurement_query, data)
            except mysql.connector.errors.DatabaseError as e:
                print "{:s} {:s}".format(data, e)

        if 'children' in json_data:
            for child in json_data['children']:
                self.add_measurements(child, condition_id)
