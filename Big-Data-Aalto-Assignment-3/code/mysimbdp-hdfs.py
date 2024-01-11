import pika, json, argparse, threading, importlib, datetime, sys, warnings, time
warnings.filterwarnings('ignore')

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_address_broker', type=str, default='35.228.244.77')
    parser.add_argument('--spark_executor_cores', type=int, default=4)
    return parser.parse_args()
args = parse_args()

rabbitmq_credentials = pika.PlainCredentials('user', 'CzZETuZ1giTb')
rabbitmq_parameters = pika.ConnectionParameters(args.server_address_broker, '5672', '/', rabbitmq_credentials)

class consume_hdfs_topic(threading.Thread):
    def __init__(self, client_id):
        threading.Thread.__init__(self)
        self.client_id = client_id
        self.customer_app = importlib.import_module('customerstreamapp')
        self.customer_app.init_spark(args.spark_executor_cores)
        self.customer_app.init_analytics_output_RabbitMQ_topic(client_id, rabbitmq_parameters)
    def run(self):
        def callback(_, __, ___, body):
            message_json = json.loads(body.decode())
            data, sending_time = message_json['data'], message_json['sending_time']
            reception_time = time.time()
            self.customer_app.ingest_and_run_analytics(data, sending_time, reception_time)
        rabbitmq_topic = 'hdfs_topic_'+self.client_id
        rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.queue_declare(queue=rabbitmq_topic)
        rabbitmq_channel.basic_consume(queue=rabbitmq_topic, on_message_callback=callback)
        rabbitmq_channel.start_consuming()

available_clients_id = ['client1']
for client_id in available_clients_id:
    print('Starting new HDFS RabbitMQ topic for '+client_id)
    thread = consume_hdfs_topic(client_id)
    thread.start()