# celety config
CELERY_BROKER_URL = 'amqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'db+sqlite:///results.sqlite'

# url config
query_url = "http://192.168.23.2:8086/query?pretty=true&db=yardstick&q=SELECT * FROM %s WHERE task_id='%s'"
write_url = 'http://192.168.23.2:8086/write?db=yardstick'
