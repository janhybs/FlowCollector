# encoding: utf-8
# author:   Jan Hybs

import json, mysql.connector
from config import credentials

from utils.decoder import ProfilerJSONDecoder
from utils.dotdict import DotDict
from utils.sql import insert_condition_query, insert_condition_fields, insert_structure_query, insert_measurement_query

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
        print e

    if 'children' in json_data:
        for child in json_data['children']:
            create_structure(child, json_data['tag'])


def create_measurement(json_data, field, condition_id):
    return {
        'type': field,
        'value': json_data[field],
        'structure': json_data['tag'],
        'cond': condition_id
    }


def add_measurements(json_data, condition_id):
    fields = ['call-count-sum', 'cumul-time-sum']
    for field in fields:
        data = create_measurement(json_data, field, condition_id)
        cursor.execute(insert_measurement_query, data)

    if 'children' in json_data:
        for child in json_data['children']:
            add_measurements(child, condition_id)


if __name__ == '__main__':

    raw_data = open('../data/example.json').read()
    json_data = json.loads(raw_data, encoding="utf-8", cls=ProfilerJSONDecoder)

    condition_id = create_conditions(json_data)
    whole_program = json_data['children'][0]
    create_structure(whole_program, parent=None)
    add_measurements(whole_program, condition_id)

    connector.commit()

cursor.close()
connector.close()
