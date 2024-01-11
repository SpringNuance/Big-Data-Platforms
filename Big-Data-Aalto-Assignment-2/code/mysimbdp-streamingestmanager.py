import pika, json, time, subprocess, threading, os, signal, argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server_address', type=str, default='35.228.211.137')
    parser.add_argument('--total_time_threshold', type=float, default=20, help='Set the threshold of total time (from sending message to end ingestion) reported to open new app.')
    return parser.parse_args()
args = parse_args()

rabbitmq_credentials = pika.PlainCredentials('user', 'CzZETuZ1giTb')
rabbitmq_parameters = pika.ConnectionParameters(args.server_address, '5672', '/', rabbitmq_credentials)

available_rabbitmq_topics = {'client1':[],'client2':[]}
active_apps = {'client1':[],'client2':[]}

class publish_available_rabbitmq_topics_client_id(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while True:
            rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
            rabbitmq_channel = rabbitmq_connection.channel()
            for client_id in available_rabbitmq_topics.keys():
                rabbitmq_channel.queue_declare(queue='rabbitmq_topics_'+client_id)
                rabbitmq_channel.basic_publish(exchange='', routing_key='rabbitmq_topics_'+client_id, body=','.join(available_rabbitmq_topics[client_id]))
            rabbitmq_connection.close()
            time.sleep(20)

publish_available_rabbitmq_topics_client_id().start()

class get_report_ingestion(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        def callback(_, __, ___, body):
            global active_apps, available_rabbitmq_topics
            report = json.loads(body.decode())
            client_id, report_id = report.pop('client_id'), report.pop('report_id')
            print('For '+client_id+' the ingestion report '+str(report_id)+' is:\n', report, '\n', file=open('logs/nearrealtime_ingestion.log', 'a'))
            if report['avg_total_time']>args.total_time_threshold:
                rabbitmq_topic = client_id+'_app'+str(len(available_rabbitmq_topics[client_id]))
                print('Starting new app and RabbitMQ topic', rabbitmq_topic)                
                arguments = {'rabbitmq_topic':rabbitmq_topic,'client_id':client_id,'server_address':args.server_address}
                app = subprocess.Popen(['python', 'code/clientstreamingestapp.py', json.dumps(arguments)])
                available_rabbitmq_topics[client_id].append(rabbitmq_topic)
                active_apps[client_id].append(app)
            if report['avg_total_time']<=args.total_time_threshold and len(available_rabbitmq_topics[client_id])>1:
                for app_index in range(len(active_apps[client_id])):
                    if app_index==0:
                        continue
                    os.killpg(os.getpgid(active_apps[client_id][app_index].pid), signal.SIGTERM)
                active_apps[client_id] = [active_apps[client_id][0]]
                available_rabbitmq_topics[client_id] = [available_rabbitmq_topics[client_id][0]]
        rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.queue_declare(queue='reporting')
        rabbitmq_channel.basic_consume(queue='reporting', on_message_callback=callback, auto_ack=True)
        rabbitmq_channel.start_consuming()

get_report_ingestion().start()

for client_id in available_rabbitmq_topics.keys(): 
    rabbitmq_topic = client_id+'_app'+str(len(available_rabbitmq_topics[client_id]))
    print('Starting new app and RabbitMQ topic', rabbitmq_topic)                            
    arguments = {'rabbitmq_topic':rabbitmq_topic,'client_id':client_id,'server_address':args.server_address}
    app = subprocess.Popen(['python', 'code/clientstreamingestapp.py', json.dumps(arguments)])
    available_rabbitmq_topics[client_id].append(rabbitmq_topic)
    active_apps[client_id].append(app)