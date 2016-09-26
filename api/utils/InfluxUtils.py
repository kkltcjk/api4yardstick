import requests

from yardstick.dispatcher.influxdb_line_protocol import make_lines

write_url = 'http://192.168.23.2:8086/write?db=yardstick'

def write_data_influx(task_id, timestamp, status, error=''):
    msg = {}
    point = {}
    point['measurement'] = 'tasklist'
    point['fields'] = {'status': status, 'error': error}
    point['time'] = timestamp 
    point['tags'] = {'task_id': task_id} 
    msg['points'] = [point]
    msg['tags'] = {}
    line = make_lines(msg).encode('utf-8')
    resposne = requests.post(write_url, data=line)
