import pika, argparse, threading

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_address_broker', type=str, default='35.228.244.77')
    return parser.parse_args()
args = parse_args()

rabbitmq_credentials = pika.PlainCredentials('user', 'CzZETuZ1giTb')
rabbitmq_parameters = pika.ConnectionParameters(args.server_address_broker, '5672', '/', rabbitmq_credentials)

class consume_input_topic_and_publish_into_hdfs_topic(threading.Thread):
    def __init__(self, client_id):
        threading.Thread.__init__(self)
        self.client_id = client_id
    def run(self):
        def callback(_, __, ___, body):
            rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
            rabbitmq_channel = rabbitmq_connection.channel()
            rabbitmq_topic = 'hdfs_topic_'+self.client_id
            rabbitmq_channel.queue_declare(queue=rabbitmq_topic)
            rabbitmq_channel.basic_publish(exchange='', routing_key=rabbitmq_topic, body=body)
            rabbitmq_connection.close()
        rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_topic = 'input_topic_'+self.client_id
        rabbitmq_channel.queue_declare(queue=rabbitmq_topic)
        rabbitmq_channel.basic_consume(queue=rabbitmq_topic, on_message_callback=callback)
        rabbitmq_channel.start_consuming()

available_clients_id = ['client1']
for client_id in available_clients_id:
    print('Starting new input RabbitMQ topic for', client_id)
    consume_input_topic_and_publish_into_hdfs_topic(client_id).start()