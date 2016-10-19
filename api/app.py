#!/usr/bin/python
import os
import requests

from flask import jsonify
from flask import abort
from flask import request

from flask_restful import fields
from flask_restful_swagger import swagger
from flasgger import Swagger
from flasgger.utils import swag_from

import conf as CONF
from utils.APIUtils import APIUtils
from instance import get_app

app = get_app()
Swagger(app)

query_url = CONF.query_url
write_url = CONF.write_url


@swagger.model
class TaskArgModel:
    resource_fields = {
    }


@swagger.model
class OptsModel:
    resource_fields = {
            'task-args': TaskArgModel,
            'keep-deploy': fields.String,
            'suite': fields.String
    }


@swagger.model
class StartModel:
    resource_fields = {
            'cmd': fields.String,
            'opts': OptsModel,
            'args': fields.String
    }

utils = APIUtils()


@app.route('/api/v3/yardstick/tasks/<string:main_cmd>', methods=['post'])
@swag_from(os.path.abspath('.') + '/external/tasks.yaml')
def tasks(main_cmd):
    cmd = utils.translate_to_str(request.json.get('cmd', ''))
    opts = utils.translate_to_str(request.json.get('opts', {}))
    args = utils.translate_to_str(request.json.get('args', ''))

    command_list = ['task', 'runner', 'scenario', 'testcase', 'plugin']
    if main_cmd in command_list:
        method = getattr(utils, 'dispatch_' + main_cmd)
        return method(cmd, opts, args)
    else:
        abort(404)


@app.route('/api/v3/yardstick/testresults', methods=['get'])
@swag_from(os.path.abspath('.') + '/external/testresults.yaml')
def testresults():
    measurement = request.args.get('measurement')
    measurement = 'opnfv_yardstick_' + measurement
    task_id = request.args.get('task_id')

    url = query_url % ('tasklist', task_id)
    try:
        resposne = requests.get(url)
        result = resposne.json()
        result = utils.translate_influxdb_result(result)
        status = result['values'][0]['status']

        if status == 0:
            return jsonify({'status': status})
        elif status == 2:
            return jsonify({'status': status, 'error': result['values'][0]['error']})
    except Exception, e:
        raise e

    url = query_url % (measurement, task_id)
    try:
        resposne = requests.get(url)
        result = resposne.json()
        result = utils.translate_influxdb_result(result)
        return jsonify({'status': 1, 'results': result})
    except Exception, e:
        raise e


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
