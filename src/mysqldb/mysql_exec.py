# encoding: utf-8
# author:   Jan Hybs

import mysql.connector
from config import credentials
from mysqldb.mysql_query import insert_condition_fields, insert_condition_query, insert_measurement_query, \
    insert_structure_query

connector = mysql.connector.connect(**credentials)
cursor = connector.cursor()



def create_conditions(json_data):
    data = { key: json_data[key] for key in insert_condition_fields }
    cursor.execute(insert_condition_query, data)

    return cursor.lastrowid


def create_structure(json_data, parent=None):
    try:
        cursor.execute(insert_structure_query, { 'name': json_data['tag'], 'parent': parent })
    except mysql.connector.errors.IntegrityError as e:
        # print e
        pass

    if 'children' in json_data:
        for child in json_data['children']:
            create_structure(child, json_data['tag'])


def create_measurement(json_data, metric, condition_id):
    return {
        'metric': metric,
        'value': json_data[metric],
        'structure': json_data['tag'],
        'cond': condition_id
    }


def add_measurements(json_data, condition_id):
    # store all keys
    fields = set(json_data.keys())
    fields = fields - set(['function', 'tag', 'file-path'])

    # except children
    if 'children' in fields:
        fields.remove ('children')

    for metric in fields:
        try:
            data = create_measurement(json_data, metric, condition_id)
            cursor.execute(insert_measurement_query, data)
        except mysql.connector.errors.DatabaseError as e:
            print "{:s} {:s}".format(data, e)


    if 'children' in json_data:
        for child in json_data['children']:
            add_measurements(child, condition_id)


def mysql_close ():
    cursor.close()
    connector.close()

def mysql_commit ():
    connector.commit()