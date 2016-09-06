#!/usr/bin/python 
import multiprocessing
import uuid
import os
import requests
import time

from flask import Flask
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request

from celery import Celery
from celery import platforms

from flasgger import Swagger
from flasgger.utils import swag_from

from utils.APIUtils import APIUtils
import conf as CONF
from instance import app
from instance import celery

platforms.C_FORCE_ROOT = True
Swagger(app)

query_url = CONF.query_url
write_url = CONF.write_url

utils = APIUtils()

@app.route('/api/v3/yardstick/tasks/<string:main_cmd>', methods = ['post']) 
@swag_from(os.path.abspath('.') + '/external/tasks.yaml')
def tasks(main_cmd):
    cmd = request.json.get('cmd', '')
    opts = request.json.get('opts', {})
    args = request.json.get('args', '')

    command_list = ['task', 'runner', 'scenario', 'testcase', 'plugin']
    if main_cmd in command_list:
        method = getattr(utils, 'dispatch_' + main_cmd)
        task_id = method(cmd, opts, args)
        return jsonify({'task_id': task_id})
    else:
        abort(404)

@app.route('/api/v3/yardstick/testresults', methods = ['get'])
@swag_from(os.path.abspath('.') + '/external/testresults.yaml')
def testresults():
    measurement = request.args.get('measurement')
    task_id = request.args.get('task_id')
    url = query_url  % (measurement, task_id)
    try:
        resposne = requests.get(url)
        result = resposne.json()
        return jsonify(result)
    except Exception:
        abort(404)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
