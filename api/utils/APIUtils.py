import uuid
import time

from flask import jsonify

from yardstick.cmd.cli import YardstickCLI
from utils.InfluxUtils import write_data_influx
from utils.DaemonThread import DaemonThread


class APIUtils(object):
    def _get_cmd(self, cmd):

        cmd_list = []
        cmd_list.append(cmd)
        return cmd_list

    def _get_opts(self, opts):

        opts_list = []
        for key in opts.keys():
            opts_list.append('--' + key)
            if len(opts[key]) > 0:
                opts_list.append(str(opts[key]))
        return opts_list

    def _get_args(self, args):

        args_list = []
        if len(args) == 0:
            return args_list
        args_list.append(args)
        return args_list

    def _get_command_list(self, cmd, opts, args):

        command_list = []
        command_list += self._get_cmd(cmd)
        command_list += self._get_opts(opts)
        command_list += self._get_args(args)
        return command_list

    def _exec_command_notask(self, command_list):

        try:
            result_list = YardstickCLI().main(command_list)
            return jsonify({'status': 'SUCCESS', 'result_list': result_list})
        except Exception, e:
            print e
            return jsonify({'status': 'FAILED', 'result_list': ''})

    def translate_to_str(self, object):
        if isinstance(object, dict):
            dic = {str(k): self.translate_to_str(v) for k, v in object.items()}
            return dic
        elif isinstance(object, list):
            return [self.translate_to_str(ele) for ele in object]
        elif isinstance(object, unicode):
            return str(object)
        return object

    def _get_command_list_influx(self, command_list, cmd, opts, args):

        command_list.append(cmd)
        for key in opts.keys():
            if 'task-args' != key:
                command_list.append('--' + key)

        command_list.append(args)
        if 'task-args' in opts.keys():
            command_list.append('--' + 'task-args')
            command_list.append(str(opts['task-args']))

        return command_list

    def _do_task(self, command_list, task_id, timestamp):
        daemonthread = DaemonThread(YardstickCLI().main_api,
                                    (command_list, task_id, timestamp))
        daemonthread.start()

    def _exec_command_influx(self, command_list, task_id):

        timestamp = str(int(float(time.time()) * 1000000000))
        write_data_influx(task_id, timestamp, 0)

        self._do_task(command_list, task_id, timestamp)

    def _create_test_suites_file(self, args, task_id):
        with open('../tests/opnfv/test_suites/' + task_id + '.yaml', 'a') as f:
            f.write("schema: 'yardstick:suite:0.1'\n")
            f.write("name: " + task_id + "\n")
            f.write("test_cases_dir: '../tests/opnfv/test_cases/'\n")
            f.write("test_cases:\n")
            for test_case in args:
                f.write("-\n")

    def dispatch_task(self, cmd, opts, args):

        command_list = ['-d', 'task']
        # command_list = ['task']

        task_id = str(uuid.uuid4())

        if isinstance(args, list):
            self._create_test_suites_file(args, task_id)
            opts['suite'] = ''
            args = '../tests/opnfv/test_suites/' + task_id + '.yaml'
        else:
            args = '../tests/opnfv/test_cases/opnfv_yardstick_' + \
                args + '.yaml'

        command_list = self._get_command_list_influx(command_list, cmd,
                                                     opts, args)
        print command_list

        self._exec_command_influx(command_list, task_id)
        return jsonify({'task_id': task_id})

    def dispatch_runner(self, cmd, opts, args):
        command_list = ['runner']
        command_list += self._get_command_list(cmd, opts, args)
        return self._exec_command_notask(command_list)

    def dispatch_scenario(self, cmd, opts, args):
        command_list = ['scenario']
        command_list += self._get_command_list(cmd, opts, args)
        return self._exec_command_notask(command_list)

    def dispatch_testcase(self, cmd, opts, args):
        command_list = ['testcase']
        command_list += self._get_command_list(cmd, opts, args)
        return self._exec_command_notask(command_list)

    def dispatch_plugin(self, cmd, opts, args):
        command_list = ['plugin']
        args = '../plugin/' + args + '.yaml'
        command_list += self._get_command_list(cmd, opts, args)

        daemonthread = DaemonThread(YardstickCLI().main, (command_list,))
        daemonthread.start()
        # return self._exec_command_notask(command_list)
        return jsonify({'status': 'SUCCESS'})

    def translate_influxdb_result(self, influxdb_result):
        if 'series' not in influxdb_result['results'][0].keys():
            results = {
                'name': '',
                'values': []
            }
            return results

        data = influxdb_result['results'][0]['series'][0]
        results = {}

        columns = data['columns']
        values = data['values']

        result_list = []
        for value in values:
            r = {}
            for i in range(len(columns)):
                r[columns[i]] = value[i]
            result_list.append(r)

        results['name'] = data['name']
        results['values'] = result_list
        return results
