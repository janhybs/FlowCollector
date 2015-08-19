# encoding: utf-8
# author:   Jan Hybs

from unittest import TestCase
from mongodb.mongo_exec import MongoExec
from flow_collector import Runner
from utils.timer import Timer


class TestMongo(TestCase):
    def __init__(self, methodName='runTest'):
        super(TestMongo, self).__init__(methodName)

        self.mongo = MongoExec()
        self.runner = Runner(self.mongo)
        self.timer = Timer()

    def test_search_1_simple(self):
        with self.timer.measured('simple 1 - find and find'):

            result = []
            for item in self.mongo.metrics.find({ 'ist_id': ',Whole Program,' }):
                # with self.timer.measured('test_search_1_simple find'):
                if self.mongo.cond.find({ '_id': item['cond_id'], "run-process-count": 3 }).count():
                    result.append(item)
            print "Total result found {:d}".format(len(result))

    def test_search_2_simple(self):
        with self.timer.measured('simple 2 - find and find_one'):

            result = []
            for item in self.mongo.metrics.find({ 'ist_id': ',Whole Program,' }):
                # with self.timer.measured('test_search_2_simple find'):
                if self.mongo.cond.find_one({ '_id': item['cond_id'], "run-process-count": 3 }):
                    result.append(item)
            print "Total result found {:d}".format(len(result))

    def test_search_3_simple(self):
        with self.timer.measured('simple 3 - pluck_fields'):
            result = []
            conditions_ids = self.mongo.pluck_fields (
                collection=self.mongo.metrics,
                fields=["cond_id"],
                match={'ist_id': ',Whole Program,'},
                group='$ist_id'
            )['cond_id']

            metrics_id = self.mongo.pluck_fields (
                collection=self.mongo.cond,
                fields=['_id'],
                match={
                    '_id': { '$in': conditions_ids },
                    "run-process-count": 3
                    },
                group=''
            )['data']
            for item in self.mongo.metrics.find({ 'cond_id': { '$in': metrics_id }, 'ist_id': ',Whole Program,' }):
                result.append(item)

            print "Total result found {:d}".format(len(result))

