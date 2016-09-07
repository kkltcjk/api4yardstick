import threading

class DaemonThread(threading.Thread):

    def __init__(self, method, args):
        threading.Thread.__init__(self)
        self.method = method
        self.args = args

    def run(self):
        self.method(self.args[0], self.args[1], self.args[2])
