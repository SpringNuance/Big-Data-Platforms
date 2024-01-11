# Big Data Platforms (Aalto CS-E4640)

## Assignment 3

**Author:**

I am Álvaro Orgaz Expósito, a data science student at Aalto (Helsinki, Finland) and a statistician from UPC-UB (Barcelona, Spain).

**Content:**

This repository contains the assignment 3 of the Big Data Platforms course in my master's degree in Data Science at Aalto (Helsinki, Finland). It consists of designing and building a stream processing service for big data platforms to store in near-realtime mode via single messages using a message broker (e.g. *AMQP with RabbitMQ*, *MQTT with Mosquitto*, *Apache Kafka*, etc) into a big data database by doing stream analytics on the fly (e.g. *Spark*). In my designed database *mysimbdp*, the message broker used is *RabbitMQ* and the component to store and manage data *mysimbdp-coredms* is *Hadoop HDFS*. Also, I use a *Google Cloud Platform RabbitMQ Certified by Bitnami* virtual machine for the message broker and a *GCP Dataproc Cluster* for *Hadoop* and *Spark*. Finally, the data used is apps and reviews information of *NYC taxis* which can be downloaded at https://data.cityofnewyork.us/Transportation/2018-Yellow-Taxi-Trip-Data/t29m-gskq. Note that I have used *.csv* as source format during all assignment implementation.

The repository mainly contains:

- file *cs-e4640-2019-assignment3.pdf*: Document with the assignment questions.

- file *requirements.txt*: Used to install necessary Python modules.

- folder *reports*:

    - file *Deployment.md*: Instructions for setting up the system and run the code.

    - file *Design.md* The answer to the assignment questions.
    
- folder *code*:
    
    - file *client_to_mysimbdp-databroker.py*: Client-side script that connects to the message broker in a server (created with *mysimbdp-broker.py*) for sending data files via messages by publishing to *RabbitMQ* topics.
    
    - file *mysimbdp-broker.py*: Component running in *GCP VM with RabbitMQ* that consumes the messages from *client_to_mysimbdp-databroker.py* and publishes them into another *RabbitMQ* topic for the *GCP Dataproc Cluster*.
    
    - file *mysimbdp-hdfs.py*: Component running in the master machine of *GCP Dataproc Cluster* that consumes the messages from *client_to_mysimbdp-broker.py* and also invokes customer's apps (*customerstreamapp.py*) with the consumed messages.
    
    - file *customerstreamapp.py*: Program running in the master machine of *GCP Dataproc Cluster* and provided by the clients (coded by me as an example), which will take the customer's message received from the message broker, check if the format is correct, perform the stream analytics (prediction of *total_amount* with *PySpark* Machine Learning models), ingest to *Hadoop HDFS* database, and report the ingestion and prediction time as well as the predictions.
    
    - file *training-PySpark-ML-models.ipynb*: *Jupyter PySpark* notebook which contains the batch analysis of *NYC taxis* dataset and the training of a Linear Regression and Gradient Boosted Trees Regressor models to predict the *total amount* feature which is saved into *Hadoop HDFS*.

    - file *config_constraints.json*: Contains the *HDFS* database constraints of features for the messages. Basically, the constraints are the type, maximum and minimum of features values.
    
- folder *data*: the metadata of NYC taxis data in *data_dictionary_trip_records_yellow.pdf*, a sample of the dataset in file *2018_Yellow_Taxi_Trip_Data_sample.csv* and the Python code used to subsample the 10GB original file in *create_2018_Yellow_Taxi_Trip_Data_sample.py*.

- folder *logs*:
    
    - file analytics_output.log*: Output information of ingested messages into *Hadoop HDFS* database by running *code/client_to_mysimbdp-databroker.py* with a subsample of the original *NYC taxis* dataset. Basically, information about the analytics outputs and the time consumed for the ingestion to database and analytics.

**Setup and how to run code:**

Follow instructions in *reports/Deployment.md* file.

**Code:**

The project has been developed in Python using several modules including *pyspark* and *pika*.