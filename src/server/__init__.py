# encoding: utf-8
# author:   Jan Hybs

from flask import Flask
from mongodb.mongo_exec import MongoExec

app = Flask(__name__)
mongo = MongoExec()

from server.views import index