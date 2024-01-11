import pika, argparse, threading, time, random, json, ctypes, pandas, datetime

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client_id', type=str, help='Set the client ID.')
    parser.add_argument('--dataset_path', type=str, help='Set the path of the dataset to ingest including the extension.')
    parser.add_argument('--server_address', type=str, default='35.228.211.137')
    return parser.parse_args()
args = parse_args()

def find_extension(filename):
    return filename.split('.')[-1]
args.file_extension = find_extension(args.dataset_path)

rabbitmq_topics_client_id = []
rabbitmq_credentials = pika.PlainCredentials('user', 'CzZETuZ1giTb')
rabbitmq_parameters = pika.ConnectionParameters(args.server_address, '5672', '/', rabbitmq_credentials)

class get_available_rabbitmq_topics_client_id(threading.Thread):
    def __init__(self, client_id):
        threading.Thread.__init__(self)
        self.client_id = client_id
    def run(self):
        def callback(_, __, ___, body):
            global rabbitmq_topics_client_id
            rabbitmq_topics_client_id = body.decode().split(',')
        rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.basic_consume(queue='rabbitmq_topics_'+self.client_id, on_message_callback=callback, auto_ack=True)
        rabbitmq_channel.start_consuming()
    def get_id_thread(self):
       if hasattr(self, '_thread_id'):
           return self._thread_id
       for id_thread, active_thread in threading._active.items():
           if active_thread is self:
               return id_thread
    def raise_exception(self):
        id_thread = self.get_id_thread()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(id_thread, ctypes.py_object(SystemExit))

available_rabbitmq_topics_client_id = get_available_rabbitmq_topics_client_id(args.client_id)
available_rabbitmq_topics_client_id.start()
while not len(rabbitmq_topics_client_id)>0:
    time.sleep(1)

if args.file_extension=='csv':
    data = pandas.read_csv(args.dataset_path)
elif args.file_extension=='json':
    data = pandas.read_json(args.dataset_path)

rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
rabbitmq_channel = rabbitmq_connection.channel()
start = datetime.datetime.now()
for row in data.index:
    row_to_ingest_json = data.loc[[row],].to_dict(orient='records')[0]
    message_json = {'data':row_to_ingest_json,'sending_time':datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    rabbitmq_channel.basic_publish(exchange='', routing_key=random.choice(rabbitmq_topics_client_id), body=json.dumps(message_json))
print('All data sent to message broker in', (datetime.datetime.now()-start).total_seconds(), 'seconds.')
rabbitmq_connection.close()
available_rabbitmq_topics_client_id.raise_exception()