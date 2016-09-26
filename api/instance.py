from flask import Flask
from flask import jsonify
from flask import abort
from flask import make_response

from celery import Celery
from celery import platforms

import conf as CONF
from yardstick.cmd.cli import YardstickCLI

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = CONF.CELERY_BROKER_URL 
app.config['CELERY_RESULT_BACKEND'] = CONF.CELERY_RESULT_BACKEND 
celery = Celery(app.name, backend=app.config['CELERY_RESULT_BACKEND'], broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
platforms.C_FORCE_ROOT = True

# @app.errorhandler(404)
# def not_found(error):
#     return make_response(jsonify({'error':'not Found'}), 404)

@celery.task
def do_back_task(command_list, task_id, timestamp):
    YardstickCLI().main_api(command_list, task_id, timestamp)

def get_app():
    return app

def get_celery():
    return celery
