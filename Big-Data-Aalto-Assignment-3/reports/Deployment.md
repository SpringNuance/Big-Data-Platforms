# Set up Google Cloud Platform Virtual Machine with RabbitMQ

Launch an image of a *Google Cloud Platform RabbitMQ Certified by Bitnami* virtual machine at https://console.cloud.google.com/marketplace/details/bitnami-launchpad/rabbitmq?project=fresh-office-232310. You will need to obtain the user name and password of *RabbitMQ* provided and change them in the code.

**Add firewall rules:**

Go to the "View network details" section of your VM instance, then go to "Firewall rules" section and create 2 firewall rules. One to allow traffic from all IP addresses (*ingress*) and one to send traffic to all IP addresses (*egress*).

- Set the direction of traffic as "Egrees", the destination IP ranges as "0.0.0.0/0", and the protocols and ports as "Allow all".

- Set the direction of traffic as "Ingrees", the destination IP ranges as "0.0.0.0/0", and the protocols and ports as "Allow all".

# Set up Google Cloud Platform Dataproc Cluster (with Hadoop and Spark)

Create a cluster of *Google Cloud Platform Dataproc* which has Hadoop and Spark at https://console.cloud.google.com/marketplace/details/google-cloud-platform/cloud-dataproc?project=fresh-office-232310. You will need to specify the configuration (number of cores and memory for master node and worker nodes which will define the YARN cores and memory for Spark). Moreover, when creating the cluster I select the optional components *Jupyter Notebook* and *ZooKeeper*.

# Set up a Python virtual environment for GCP VM with Rabbit MQ

Connect into the GCP VM with RabbitMQ by SSH and run the following commands in the root folder of the repository:

    1. sudo apt-get install python3-pip
    2. sudo pip3 install virtualenv
    3. virtualenv env
    4. source env/bin/activate
    5. pip3 install -r requirements.txt

Repeat the same process in the client-side, the machine where you want to send messages from. Note that the *GCP Dataproc Cluster* has already the necessary Python modules, such as *pyspark* or *pandas* or *pip*, however, you need to install *pika*:

    6. pip install pika --user

# Initialize the HDFS database

Firstly, you need to have the database initialized as a HDFS *.csv* file in the VM of *GCP Dataproc Cluster*. Download the NYC taxi data (described in the *README.md* file) or a subsample of it just to initialize the database and use these Hadoop commands 
'hdfs://cluster-ebb0-m/hadoop/2018_Yellow_Taxi_Trip_Data.csv'
    
    7. hdfs dfs -put your_path/2018_Yellow_Taxi_Trip_Data.csv /hadoop/2018_Yellow_Taxi_Trip_Data_TMP.csv

However, by running the command *hdfs dfs -ls /hadoop* you will see that the permission is *-rw-r--r--* and asociated to your user. We need to have *drwxr-xr-x* permission and root user to avoid problems ingesting data to it. Then, I run from the Jupyter Notebook (with root privileges) at *ExternalIP:8123* the code:

    import pyspark
    spark = pyspark.sql.SparkSession.builder.appName('tmp').getOrCreate()
    df = spark.read.csv('hdfs://cluster-ebb0-m/hadoop/2018_Yellow_Taxi_Trip_Data_TMP.csv', header=True, inferSchema=True)
    df = spark.write.csv('hdfs://cluster-ebb0-m/hadoop/2018_Yellow_Taxi_Trip_Data.csv', header=True)
    spark.stop()

And now we can simply delete the wrong HDFS *.csv* with the Hadoop command: 

    8. hdfs dfs -rm -r /hadoop/2018_Yellow_Taxi_Trip_Data_TMP.csv

Additionally, you can get Hadoop information about the database (data nodes, replication factor, blocksize, etc.) by using the Hadoop commands:

    hdfs fsck /hadoop/2018_Yellow_Taxi_Trip_Data.csv -files -blocks -locations
    hdfs dfsadmin -report
    hdfs getconf -confKey dfs.blocksize

Finally, we need to train the *PySpark* Machine Learning models used in the streaming analytics platform. Basically, you only have to run the notebook *code/training-PySpark-ML-models.ipynb* in the VM of *GCP Dataproc Cluster*.

# Run code

Connect into the VM with RabbitMQ by SSH and run the following commands in the root folder of the repository:

    9. source env/bin/activate
    10. nohup sudo env/bin/python code/mysimbdp-broker.py --server_address_broker "35.228.56.40" &

Connect into the master VM of *GCP Dataproc Cluster* by SSH and run the following commands in the root folder of the repository:

    11. nohup python code/mysimbdp-hdfs.py --server_address_broker "35.228.56.40" --spark_executor_cores 4 &

Now you are ready to ingest data by running the code (described in the *README.md* file) from the client-side machine. You can read the help of all the arguments for more information. For example, you can run under the created virtual environment:

    python code/client_to_mysimbdp-databroker.py --client_id client1 --dataset_path data/2018_Yellow_Taxi_Trip_Data_sample.csv --server_address_broker "35.228.56.40"
    
*Note*: You can modify the report log file destination and the number of YARN cores for Spark in step 11, as well as the ingestion constraints of the database, features in the configuration JSON file (described in the *README.md* file).