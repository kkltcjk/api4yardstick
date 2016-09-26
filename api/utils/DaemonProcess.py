import os
import multiprocessing
from InfluxUtils import write_data_influx

class DaemonProcess(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)

    def __init__(self, method, args):
        print "in"
        multiprocessing.Process.__init__(self, target=method, args=args)

    def task():
        try:
            self.run()
        except Exception, e:
            write_data_influx(task_id, timestamp, 2,error=str(e))
        finally:
            if os.path.exists('../tests/opnfv/test_suites/' + task_id + '.yaml'):
                os.remove('../tests/opnfv/test_suites/' + task_id + '.yaml')
