import pandas as pd
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegressionModel, GBTRegressionModel
import pyspark, json, time, warnings, threading, pika
warnings.filterwarnings('ignore')

hdfs_database_path = 'hdfs://cluster-ebb0-m/hadoop/2018_Yellow_Taxi_Trip_Data.csv'
database_features_ordered = ['VendorID','tpep_pickup_datetime','tpep_dropoff_datetime','passenger_count','trip_distance','RatecodeID','store_and_fwd_flag','PULocationID','DOLocationID','payment_type','fare_amount','extra','mta_tax','tip_amount','tolls_amount','improvement_surcharge','total_amount']
model_features = ['VendorID','passenger_count','trip_distance','extra','mta_tax','tip_amount','tolls_amount','improvement_surcharge','fare_amount','RatecodeID','payment_type']
target = 'total_amount'

def init_spark(spark_executor_cores=4):
    global spark, assembler, model_lr, model_gbt
    spark = pyspark.sql.SparkSession.builder.appName('Spark '+time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time()))).getOrCreate()
    spark.sparkContext._conf.set('spark.executor.cores', spark_executor_cores)
    assembler = VectorAssembler(inputCols=model_features, outputCol='features')
    model_lr = LinearRegressionModel.load('hdfs://cluster-ebb0-m/hadoop/model_lr.model')
    model_gbt = GBTRegressionModel.load('hdfs://cluster-ebb0-m/hadoop/model_gbt.model')

def init_analytics_output_RabbitMQ_topic(client_id_, rabbitmq_parameters):
    global client_id, rabbitmq_connection, rabbitmq_channel
    client_id = client_id_
    rabbitmq_connection = pika.BlockingConnection(rabbitmq_parameters)
    rabbitmq_channel = rabbitmq_connection.channel()
    rabbitmq_topic = 'analytics_output_topic_'+client_id
    rabbitmq_channel.queue_declare(queue=rabbitmq_topic)

with open('code/config_constraints.json', 'r') as file:
    ingestion_constraints = json.load(file)

def check_ingestion_constraints(data):
    for feature in database_features_ordered:
        for feature_constraint in ingestion_constraints[client_id][feature].keys():
            if feature_constraint=='type':
                if type(data[feature]).__name__ not in ingestion_constraints[client_id][feature]['type']:
                    return 'Error! feature '+feature+' should be '+ingestion_constraints[client_id][feature]['type']
            if feature_constraint=='min':
                if data[feature]<ingestion_constraints[client_id][feature]['min']:
                    return 'Error! feature '+feature+' should be > '+str(ingestion_constraints[client_id][feature]['min'])
            if feature_constraint=='max':
                if data[feature]>ingestion_constraints[client_id][feature]['max']:
                    return 'Error! feature '+feature+' should be < '+str(ingestion_constraints[client_id][feature]['max'])
    return 'OK'
    
def ingest_and_run_analytics(data, sending_time, reception_time):
    format_check = check_ingestion_constraints(data)
    if format_check!='OK':
        report = {'Format check': format_check}
    else:
        df_message = pd.DataFrame.from_dict([data])
        df_message = df_message[database_features_ordered]
        df_message_pyspark = spark.createDataFrame(df_message)
        df_message_pyspark.write.csv(hdfs_database_path, header=True, mode='append')
        end_ingestion = time.time()
        ingestion_time = end_ingestion-reception_time
        df_message_pyspark_assembler = assembler.transform(df_message_pyspark).select(['features',target])
        prediction_lr = model_lr.transform(df_message_pyspark_assembler).toPandas()['prediction'][0]
        prediction_gbt = model_gbt.transform(df_message_pyspark_assembler).toPandas()['prediction'][0]
        analytics_time = time.time()-end_ingestion
        report = {'Format check': format_check+' Message ingested to database in '+str(ingestion_time)+' seconds','Analytics time':analytics_time,'Prediction LR':prediction_lr,'Prediction GBT:':prediction_gbt,'Target':df_message[target][0]}
    analytics_output = 'For the message of '+client_id+' sent at '+sending_time+' the report is: '+str(report)    
    rabbitmq_topic = 'analytics_output_topic_'+client_id
    rabbitmq_channel.basic_publish(exchange='', routing_key=rabbitmq_topic, body=analytics_output)