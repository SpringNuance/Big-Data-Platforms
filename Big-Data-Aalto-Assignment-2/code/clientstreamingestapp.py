import threading, pika, sys, pymongo, json, time, datetime

args = json.loads(sys.argv[1])
rabbitmq_topic, client_id, server_address = args['rabbitmq_topic'], args['client_id'], args['server_address']

mongo_client = pymongo.MongoClient('mongodb+srv://alvarorgaz:XLao4jEcoIz3kFXH@big-data-a1-j25ko.gcp.mongodb.net/admin?retryWrites=true&w=majority')
database = mongo_client['google_play_store']
table = database[client_id]
    
rabbitmq_credentials = pika.PlainCredentials('user', 'CzZETuZ1giTb')
rabbitmq_parameters = pika.ConnectionParameters(args['server_address'], '5672', '/', rabbitmq_credentials)

class publish_report_ingestion(threading.Thread):
    def __init__(self, report_id, number_messages, avg_ingestion_time, avg_total_time):
        threading.Thread.__init__(self)
        self.report_id, self.number_messages, self.avg_ingestion_time, self.avg_total_time = report_id, number_messages, avg_ingestion_time, avg_total_time
    def run(self):
        collection_stats = database.command('collstats', client_id)
        report = {
            'report_id':self.report_id,
            'client_id': client_id,
            'number_messages':self.number_messages,
            'avg_ingestion_time':self.avg_ingestion_time,
            'avg_total_time':self.avg_total_time,
            'collection_size':collection_stats['size'],
            'collection_count':collection_stats['count'],
            'collection_avgObjSize':collection_stats['avgObjSize']
        }
        rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.basic_publish(exchange='', routing_key='reporting', body=json.dumps(report))
        rabbitmq_connection.close()

report_id, report_frequency, messages_ingested, ingestion_time, total_time = 0, 1000, 0, [], []
def callback(_, __, ___, body):
    global report_id, report_frequency, messages_ingested, ingestion_time, total_time
    message_json = json.loads(body.decode())
    sending_time, data = message_json['sending_time'], message_json['data']
    start_ingestion = datetime.datetime.now()
    table.insert(data)
    end_ingestion = datetime.datetime.now()
    ingestion_time.append((end_ingestion-start_ingestion).total_seconds())
    total_time.append((end_ingestion-datetime.datetime.strptime(sending_time, '%Y-%m-%d %H:%M:%S')).total_seconds())
    messages_ingested += 1
    if messages_ingested%report_frequency==0:
        avg_ingestion_time, avg_total_time = sum(ingestion_time)/report_frequency, sum(total_time)/report_frequency
        publish_report_ingestion(report_id, report_frequency, avg_ingestion_time, avg_total_time).start()
        report_id, ingestion_time, total_time = report_id+1, [], []

rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
rabbitmq_channel = rabbitmq_connection.channel()
rabbitmq_channel.queue_declare(queue=rabbitmq_topic)
rabbitmq_channel.basic_consume(queue=rabbitmq_topic, on_message_callback=callback)
rabbitmq_channel.start_consuming()