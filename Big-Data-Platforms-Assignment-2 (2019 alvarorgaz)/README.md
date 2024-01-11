# Big Data Platforms (Aalto CS-E4640)

## Assignment 2

**Author:**

I am Álvaro Orgaz Expósito, a data science student at Aalto (Helsinki, Finland) and a statistician from UPC-UB (Barcelona, Spain).

**Content:**

This repository contains the assignment 2 of the Big Data Platforms course in my master's degree in Data Science at Aalto (Helsinki, Finland). It consists of designing and building a multitenancy (multiple users/clients ingesting data) Big Data platform to store data files in batch mode (full data file at once) or in near-realtime mode via single messages using a message broker (e.g. *AMQP with RabbitMQ*, *MQTT with Mosquitto*, *Apache Kafka*, etc). In my designed database *mysimbdp*, the message broker used is *RabbitMQ* and the component to store and manage data *mysimbdp-coredms* is MongoDB (defining one collection of document for each client ID). Also, I use a *Google Cloud Platform RabbitMQ Certified by Bitnami* virtual machine for the *REST APIs* and the message broker. Finally, the data used is apps and reviews information of *Google Play Store Apps* which can be downloaded at https://www.kaggle.com/lava18/google-play-store-apps. Note that I have converted the reviews *.csv* format into *.json* using Python *pandas* module for having multiple file types in the project.
  
The repository mainly contains:

- file *cs-e4640-2019-assignment2.pdf*: Document with the assignment questions.

- file *requirements.txt*: Used to install necessary Python modules.

- folder *reports*:

    - file *Deployment.md*: Instructions for setting up the system and run the code.

    - file *Design.md* The answer to the assignment questions.
    
- folder *code*:
    
    - folder *client-input-directory*: Directory to save the sent files (.csv or .json) by clients through the REST API. It is part of batch mode ingestion.
    
    - folder *client-stage-directory*: Directory to move the sent files that pass the ingestion constraints before ingestion to MongoDB database. It is part of batch mode ingestion.
    
    - file *mysimbdp-daas.py*: Component for setting the *REST APIs* which can be called by external data clients/consumers (by using *client_file_to_mysimbdp-daas.py*) to store/read data files into folder *client-input-directory*. It is part of batch mode ingestion.
    
    - file *client_file_to_mysimbdp-daas.py*: Client-side script that connects to the *REST APIs* (created with *mysimbdp-daas.py*) for storing data files into server folder *client-input-directory*. It is part of batch mode ingestion.
    
    - file *config_ingestion_constraints.json*: Contains the ingestion constraints of files by clients IDs. Basically, the constraints are: file type (*.csv* or *.json*), max file size in bytes, and max number of files in the input directory by client ID. By default, I set client IDs *client1* with file type *.csv* and *client2* with file type *.json*.
    
    - file *mysimbdp-fetchdata.py*: Component for moving the files in folder *client-input-directory* into folder *client-stage-directory* by checking if they pass the ingestion constraints in *config_ingestion_constraints.json*. It is part of batch mode ingestion.
    
    - file *mysimbdp-batchingestmanager.py*: Component that invokes customer's clients' apps to perform the ingestion when files are moved into folder *client-stage-directory*. It is part of batch mode ingestion.
    
    - files *clientbatchingestapp--client#.py*: Simple program provided by the clients (coded by me as an example), which will take the customer's files as input and ingest the files into the final *mysimbdp-coredms* MongoDB. It is part of batch mode ingestion.
    
    - file *client_to_mysimbdp-databroker.py*: Client-side script that connects to the message broker in a server (created with *mysimbdp-streamingestmanager.py* and *clientstreamingestapp.py*) for sending data files via messages to *RabbitMQ* topics. It is part of near-realtime mode ingestion.
    
    - file *mysimbdp-streamingestmanager.py*: Component that publishes into a *RabbitMQ* topic the available ingestion topics to be consumed by *client_to_mysimbdp-databroker.py* and also invokes customer's clients' apps to perform the ingestion when messages are received by the message broker. It is part of batch mode ingestion. It is part of near-realtime mode ingestion.
    
    - file *clientstreamingestapp.py*: Program provided by the clients (coded by me as an example), which will take the customer's message received by the message broker via *RabbitMQ* topics, ingest them into the final *mysimbdp-coredms* MongoDB, and reports the ingestion to *mysimbdp-streamingestmanager.py* via another *RabbitMQ* topic. It is part of near-realtime mode ingestion.

- folder *data*: Apps and reviews information of *Google Play Store Apps* in files *googleplaystore.csv* and *googleplaystore_user_reviews.json*, and the respective licence. Note that I provide *googleplaystore_user_reviews.csv* converted into JSON since I set up default file type constraints for clients in both formats. Moreover, it is in the right format to be read in the code by Python module *pandas*.

- folder *logs*:
    
    - file *batch_ingestion.log*: Output information of ingested files into MongoDB by running *client_file_to_mysimbdp-daas.py* and created from *mysimbdp-batchingestmanager.py*. Basically, information about the client ID, file server reception time, file size, successful ingested rows, actual bytes size of client collection (or table in database), etc.
    
    - file *near-realtime_ingestion.log*: Output information of ingested files into MongoDB by running *client_to_mysimbdp-databroker.py* and created from *mysimbdp-streamingestmanager.py*. Basically, information about the client ID, average message ingestion time, average message total ingestion time from client sending to ingestion, number of messages ingested, actual number of documents and bytes size of client collection (or table in database), etc.

**Setup and how to run code:**

Follow instructions in *reports/Deployment.md* file.

**Code:**

The project has been developed in Python using several modules including *pika*, *pymongo*, and *flask* which is a micro web framework written in Python.