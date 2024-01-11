# Big Data Platforms (Aalto CS-E4640)

## Assignment 1

**Author:**

I am Álvaro Orgaz Expósito, a data science student at Aalto (Helsinki, Finland) and a statistician from UPC-UB (Barcelona, Spain).

**Content:**

This repository contains the assignment 1 of the Big Data Platforms course in my master's degree in Data Science at Aalto (Helsinki, Finland). It consists of designing and building a Big Data platform. In my designed database *mysimbdp*, the component to store and manage data *mysimbdp-coredms* is MongoDB. Also, I use a *Google Cloud Platform Kafka Certified by Bitnami* virtual machine for the *REST APIs*. Finally, the data used is apps and reviews information of *Google Play Store Apps* which can be downloaded at https://www.kaggle.com/lava18/google-play-store-apps. 
  
The repository mainly contains:

- file *cs-e4640-2019-assignment1.pdf*: Document with the assignment questions.

- file *requirements.txt*: Used to install necessary Python modules.

- file *demolink.txt*: Contains the YouTube link of the project demo.

- folder *reports*:

    - file *Deployment.md*: Instructions for setting up the system and run the code.

    - file *Design.md* The answer to the assignment questions.
    
- folder *code*:
    
    - file *mysimbdp-daas.py*: Component for setting the *REST APIs* which can be called by external data clients/consumers (by using *client_to_mysimbdp-daas.py*) to store/read data into/from *mysimbdp-coredms* MongoDB.
    
    - file *client_to_mysimbdp-daas.py*: Client-side script that connects to the *REST APIs* (created with *mysimbdp-daas.py*) for storing data into *mysimbdp-coredms* MongoDB.
    
    - file *mysimbdp-dataingest.py*: Component to read data from data sources (files/external databases) of the client/user and then store the data by directly calling APIs of *mysimbdp-coredms* MongoDB.
    
    - file *performance_multiple_requests.py*: Script to test request time performance.

- folder *data*: Apps and reviews information of *Google Play Store Apps* in files *googleplaystore.csv* and *googleplaystore_user_reviews.csv*, and the respective licence.

- folder *logs*: Outputs of running the script *code/performance_multiple_requests.py* to study ingestion performance. Basically, for several Python multi threads (simulating different clients ingesting data to MongoDB at the same time) I try to ingest some data requests for comparing the ingestion time between using *REST APIs* in a GCP virtual machine (created with *code/mysimbdp-daas.py*), the same in local, and directly from client data using MongoDB API (with *code/mysimbdp-dataingest.py*).

**Setup and how to run code:**

Follow instructions in *reports/Deployment.md* file.

**Code:**

The project has been developed in Python using several modules including *pymongo* and *flask* which is a micro web framework written in Python.