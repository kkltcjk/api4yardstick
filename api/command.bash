#!/bin/bash

# curl -i -H "Content-Type: application/json" -X POST -d '{"cmd": "start", "opts": {}, "args": "tc002"}' http://localhost:5000/api/v3/yardstick/tasks/task
# curl -i -H "Content-Type: application/json" -X POST -d '{"cmd": "start", "opts": {}, "args": ["tc002"]}' http://localhost:5000/api/v3/yardstick/tasks/task

# curl -i -H "Content-Type: application/json" -X POST -d '{"cmd": "list"}' http://localhost:5000/api/v3/yardstick/tasks/runner/

# curl -i -H "Content-Type: application/json" -X GET "http://localhost:5000/api/v3/yardstick/testresults?task_id=8ab0be0c-9dd3-4ce3-8b21-ea645b521842&measurement=tc002"

# curl -GET 'http://192.168.23.2:8086/query?pretty=true' --data-urlencode "db=yardstick" --data-urlencode "q=SELECT * FROM tasklist WHERE task_id='71ecca66-c59b-4f37-95b0-fce0373406e5'"
# curl -i -XPOST 'http://192.168.23.2:8086/write?db=yardstick' --data-binary 'tasklist,task_id=91e680a6-a81c-4bd6-bf37-b91a8b7a8ba9,error=noerror status=1 1472799230444195394'
curl -i -X POST --header "Content-Type: application/json"  -d '{"args": "tc100", "cmd": "start", "opts": {"task-args": {"tx_msg_size":"15536", "rx_msg_size":"17380", "tx_cache_size":"32768","rx_cache_size":"43690"}}}' http://localhost:5000/api/v3/yardstick/tasks/task
