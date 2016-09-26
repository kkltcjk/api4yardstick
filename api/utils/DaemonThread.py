import threading
import os
from InfluxUtils import write_data_influx

class DaemonThread(threading.Thread):

    def __init__(self, method, args):
        threading.Thread.__init__(self, target=method, args=args)
        self.method = method
        self.args = args

    def _do_task(self):
        command_list = self.args[0]
        task_id = self.args[1]
        timestamp = self.args[2]

        try:
            self.method(command_list, task_id, timestamp)
        except Exception, e:
            write_data_influx(task_id, timestamp, 2,error=str(e))
            raise e
        finally:
            if os.path.exists('../tests/opnfv/test_suites/' + task_id + '.yaml'):
                os.remove('../tests/opnfv/test_suites/' + task_id + '.yaml')

    def _do_notask(self):
        command_list = self.args[0]
        self.method(command_list)

    def run(self):
        if len(self.args) == 3:
            self._do_task()
        else:
            self._do_notask()
