import sys, pika, argparse, json, pandas, datetime, threading

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--client_id', type=str, help='Set the client ID.')
    parser.add_argument('--dataset_path', type=str, help='Set the path of the dataset to ingest including the extension.')
    parser.add_argument('--server_address_broker', type=str, default='35.228.244.77')
    parser.add_argument('--analytics_output_path', type=str, default='logs/analytics_output.log')
    return parser.parse_args()
args = parse_args()

def find_extension(filename):
    return filename.split('.')[-1]
args.file_extension = find_extension(args.dataset_path)

if args.file_extension=='csv':
    data = pandas.read_csv(args.dataset_path)
else:
    sys.exit('File extension not supported, ".csv" needed.')

rabbitmq_credentials = pika.PlainCredentials('user', 'CzZETuZ1giTb')
rabbitmq_parameters = pika.ConnectionParameters(args.server_address_broker, '5672', '/', rabbitmq_credentials)

class consume_output_analytics_topic(threading.Thread):
    def __init__(self, client_id):
        threading.Thread.__init__(self)
        self.client_id = client_id
    def run(self):
        def callback(_, __, ___, body):
            with open(args.analytics_output_path, 'a') as file:
                file.write('\n'+str(body)+'\n')  
        rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_topic = 'analytics_output_topic_'+self.client_id
        rabbitmq_channel.queue_declare(queue=rabbitmq_topic)
        rabbitmq_channel.basic_consume(queue=rabbitmq_topic, on_message_callback=callback)
        rabbitmq_channel.start_consuming()
thread_output_analytics = consume_output_analytics_topic(args.client_id)
thread_output_analytics.start()

rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
rabbitmq_channel = rabbitmq_connection.channel()
rabbitmq_topic = 'input_topic_'+args.client_id

start = datetime.datetime.now()
for row in data.index:
    row_to_ingest_json = data.loc[[row],].to_dict(orient='records')[0]
    sending_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_json = {'data':row_to_ingest_json,'sending_time':sending_time}
    rabbitmq_channel.queue_declare(queue=rabbitmq_topic)
    rabbitmq_channel.basic_publish(exchange='', routing_key=rabbitmq_topic, body=json.dumps(message_json))

print('All data sent to message broker in', (datetime.datetime.now()-start).total_seconds(), 'seconds.')
rabbitmq_connection.close()