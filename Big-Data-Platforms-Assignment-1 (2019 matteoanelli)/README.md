# BigDataPlatform Assignement 1 - Design of a Big Data Platform

---------------------------------------------------------------------------

This assignment is part of a collection of 3 assignment of the Big Data Platform course at Aalto University.
 * [Assignment 1](https://github.com/matteoanelli/BigDataPlatform) : Design of a big data platform (Main components). [Report](https://github.com/matteoanelli/BigDataPlatform/blob/master/assignment-1-801979-master/reports/Report.md)
 * [Assignment 2](https://github.com/matteoanelli/BigDataPlatform2) : Data Ingestion [Report](https://github.com/matteoanelli/BigDataPlatform2/blob/master/assignment-2-801979/reports/Report.md)
 * [Assignment 3](https://github.com/matteoanelli/BigDataPlatform3) : Analytics [Report](https://github.com/matteoanelli/BigDataPlatform3/blob/master/assignment-3/reports/Report.md)


The [Report](https://github.com/matteoanelli/BigDataPlatform/blob/master/assignment-1-801979-master/reports/Report.md) is a full explanation of the project.

---------------------------------------------------------------------------

Instruction for deployment
=====================
First of all I have used two **environment variable** so they have to be set as follow:
```
MONGO_URL = XXXXXXX
CLOUDAMQP_URL  = YYYYYYYYY
```
The **MONGO_URL** is the link to open a connection to MongoDB Atlas.

The **CLOUDAMQP_URL** is the link to connect with CloudAMQP (RabbitMQ as a service).

If you want to use your personal MongoDB and CloudAMQP account I followed the official tutorial to set up both.

The project have been developed in python. be sure to use version 3.6+.

As second step the all the requirement can be imported.
```
pip install -r requirements.txt
```

The first script that it can be executed is the source ingestion. I passed the csv file as argument of the command.
```
python ingestSource.py <csv source path>
```
Now that the database have been populated the Flask server can be launched as follow:
```
python server.py
```

After that the daemon (rabbit listener) should be launched as well.
```
python ingestPOST.py
```

A test of the uploading performance has been implemented. It calculate for all the iteration the response time.
You can reproduce the results as following:
```
./test_ingestion.sh <csv source path>
```
In order to reproduce all the trials you have to tune the upper limit of the for loop inside the file.
The result described in the report have been generated wit
```
for i in {1..10}; do
    time (python ingestSource.py "/home/matteo/Downloads/Indoor_Location_Detection_Dataset.csv") &
done

wait
```
# APIs

After that our microservices are running you can start doing POST/GET request to the APIs.
Two APIs have been implemented so far.

The first one is to do a GET request given the Part_id where it will retrieve all the entry with that Part_id.
```
GET http://127.0.0.1:5000/document/<Part_id>
```

The second API is to do a POST request. It require all the fields and it will push a new entry. No check are implemented so far.
```
GET http://127.0.0.1:5000/document
```
The API allow to insert a document (JSON). It has to be insert in the payload of the request. This request will
be forwarded to the queue RabbitMQ than to the daemon and eventually it will be written on the database.

```
{
    "part_id": 5555,
    "ts_date": 20183012,
    "ts_time": "10:05:38",
    "room": "1010"
    }
```

