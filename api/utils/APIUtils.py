import multiprocessing
import uuid
import os
import requests
import time
import json

from flask import Flask
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request

from yardstick.cmd.cli import YardstickCLI
from utils.InfluxUtils import write_data_influx
from utils.DaemonThread import DaemonThread
from api.instance import celery

@celery.task
def do_back_task(command_list, task_id, timestamp):
    YardstickCLI().main_api(command_list, task_id, timestamp)

class APIUtils(object):
    def _get_cmd(self, command_list, cmd):
        if cmd not in command_list:
            abort(404)
        return ' ' + cmd

    def _get_opts(self, opts):
        options = ''
        for key in opts.keys():
            options += ' --' + key + ' ' + opts[key]
        return options

    def _get_args(self, args):
        if len(args) == 0:
            return ''
        return ' ' + args

    def _get_command(self, command_list, cmd, opts, args):
        command = ''
        command += self._get_cmd(command_list, cmd)
        command += self._get_opts(opts)
        command += self._get_args(args)
        return command

    def _exec_command_nooutput(self, command):
        try:
            os.system(command)
            return jsonify({'state': 'OK'})
        except Exception, e:
            print e
            abort(404)

    def _get_command_list_influx(self, command_list, cmd, opts, args):

        command_list.append(cmd)
        for key in opts.keys():
            command_list.append('--' + key)
            command_list.append(opts[key])
        
        command_list.append(args)
        return command_list

    def _exec_command_influx(self, command_list):

        task_id = str(uuid.uuid4())
        timestamp = str(int(float(time.time()) * 1000000000))
        write_data_influx(task_id, timestamp, 0)

        try:
            # process = multiprocessing.Process(
            #         target=YardstickCLI().main_api,
            #         args=(command_list, task_id, timestamp))
            # process.daemon = True
            # process.start()
            daemonthread = DaemonThread(YardstickCLI().main_api, (command_list, task_id, timestamp))
            daemonthread.start()
            # do_back_task.delay(command_list, task_id, timestamp)
        except Exception, e:
            print e
        return task_id

    def dispatch_task(self, cmd, opts, args):

        command_list = ['task']
        command_list = self._get_command_list_influx(command_list, cmd, opts, args)

        task_id = self._exec_command_influx(command_list)
        return task_id 

    def dispatch_runner(self, cmd, opts, args):
        command = 'yardstick runner'
        command_list = ['list', 'show']
        command += self._get_command(command_list, cmd, opts, args)
        return self._exec_command_nooutput(command)

    def dispatch_scenario(self, cmd, opts, args):
        command = 'yardstick scenario'
        command_list = ['list', 'show']
        command += self._get_command(command_list, cmd, opts, args)
        return self._exec_command_nooutput(command)

    def dispatch_testcase(self, cmd, opts, args):
        command = 'yardstick testcase'
        command_list = ['list', 'show']
        command += self._get_command(command_list, cmd, opts, args)
        return self._exec_command_nooutput(command)

    def dispatch_plugin(self, cmd, opts, args):
        command = 'yardstick plugin'
        command_list = ['install', 'remove']
        command += self._get_command(command_list, cmd, opts, args)
        return self._exec_command(command)
