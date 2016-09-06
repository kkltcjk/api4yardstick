import multiprocessing
import uuid

from yardstick.cmd.cli import YardstickCLI

task_id = str(uuid.uuid4())
argv = ['task', 'start', '../samples/ping.yaml']

process = multiprocessing.Process(
        target=YardstickCLI().main,
        args=(argv, task_id))
process.start()
print task_id
