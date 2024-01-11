# Global architecture
<p align="center">
<img src="architecture.png">
<p>

# Part 1 - Ingestion with batch

### 1. Define a set of constraints for files which should (or should not) be ingested and for the customer service profile w.r.t. ingestion constraints (e.g., number of files and data sizes).

The first defined ingestion constraint set for the clients are the maximum file size (1MB by default for each customer). The second constraint is the file type since the implementation can handle *.csv* and *.json*, I set by default that one client can only ingest *.csv* and other *.json*. The third constraint is the maximum number of files sent to the folder *client-input-directory* by each customer, which means that if at the moment of moving one file to the *client-stage-directory* there are more files of the corresponding client ID than its constraint the file will not be staged.

However, the restriction of the file size is not hard because although it is advised that the file size does not exceed the limit if it exceeds I implemented microbatching on the server site to split the file into microbatches to be staged in order to handle these large files. Moreover, the restriction for the file type is set according to the nature of the data, since in my implementation *client1* uses *googleplaystore.csv* which does not have any sparse values and contains several features, and *client2* uses reviews data which has many missings, is more sparse and the format of the data varies.

The file *config_ingestion_constraints.json* contains all these ingestion constraints of files by clients IDs. This constraints file is loaded by the component *mysimbdp-fetchdata.py*, which moves the files in folder *client-input-directory* into folder *client-stage-directory*, to check if each file passes the ingestion constraints and if the file size constraint is not handled then it applies microbatching.

    {
    "client1":{"file_type":"csv","max_file_size":1048576,"max_files_number":10},
    "client2":{"file_type":"json","max_file_size":1048576,"max_files_number":5}
    }

### 2. Each customer will put files to be ingested into a directory, client-input-directory. Implement a component mysimbdp-fetchdata that automatically detect which files should be ingested based on customer profiles and only move the files from client-input-directory inside mysimbdp (only staging data in; data has not been stored into mysimbdp-coredms yet).

The implementation of this question is done in *mysimbdp-fetchdata.py*. This component moves the files in folder *client-input-directory* into folder *client-stage-directory* by checking if they pass the ingestion constraints in *config_ingestion_constraints.json*. Apart from the requested task of stage files from input folder to stage folder, this program also handles the microbatching task if required.

### 3. Each customer provides a simple program, clientbatchingestapp, which will take the customer's files as input and ingest the files into the final sink mysimbdp-coredms. Design and develop a component mysimbdp-batchingestmanager that invokes customer's clientbatchingestapp to perform the ingestion when files are moved into mysimbdp. mysimbdp imposes the model that clientbatchingestapp (and the customer) has to follow.

The implementation of this question is done in files *mysimbdp-batchingestmanager.py* and *clientbatchingestapp--client#.py*. The first one is a component that invokes customer's clients' apps to perform the ingestion when files are moved into folder *client-stage-directory*. Moreover, it receives reporting and ingestion statistics from the customer app and MongoDB collections and accumulates it into the file *logs/batch_ingestion.log*. The second one is a program provided by the clients (coded by me as an example), which takes the staged customer's files as input and ingest the files into the final *mysimbdp-coredms* MongoDB. It is important to note that the client app implementation is independent of the coding language or system that the client has for the ingestion, it could be Python (as in my implementation), Java or simply a binary file and the manager can handle it easily.

### 4. Develop test programs (clientbatchingestapp), test data, and test profiles for customers. Show the performance of ingestion tests, including failures and exceptions, for at least 2 different customers in your test environment.

As explained before, *mysimbdp-batchingestmanager.py* receives reporting and ingestion statistics from the customer app *clientbatchingestapp--client#.py* and MongoDB collections and accumulates it into the file *logs/batch_ingestion.log*. In the log file provided you can find the information of the ingestion of the datafiles of each client (explained in *README.md*) into the database MongoDB using batch mode. As you can see these performance ingestion reports are separated by client ID and ingested files including the split in microbatches if required. 

In this log file with the testing of the performance of ingestion, we can see that there is a 100% successful ingestion rate with the two sent files (*googleplaystore.csv* and *googleplaystore_user_reviews.json*) to the server via the *REST APIs*. It is reasonable since in this test the file passed the constraints except the file size, and it was handled by the microbatching, then all information is ingested once staged. Moreover, you can check the ingestion time into MongoDB for each staged batch and microbatch and it is done quite efficiently.

### 5. Implement and provide logging features for capturing successful/failed ingestion as well as metrics about ingestion time, data size, etc., for files which have been ingested into mysimbdp. The log should be outputted in a separate file or database for analytics of ingestion.

As explained before, the implementation of this question is done in *mysimbdp-batchingestmanager.py* component which receives reporting and ingestion statistics from the customer app *clientbatchingestapp--client#.py* and MongoDB collections and accumulates it into the file *logs/batch_ingestion.log* (only for files that have been staged and then ingested into the database). My implementation includes several information:

- *ingestion_size_local*: Size in bytes of each batch file ingested in the original format set by the customer (*.csv* or *.json*).

- *successful_rows_rate*: Percentage of successful ingested rows or observations in the file.

- *successful_rows*: Number of successful ingested rows or observations in the file.

- *ingestion_time*: Time taken to ingest the batch into MongoDB.

- *collection_count*: Number of documents (ingested rows or observations) in the client MongoDB collection at this moment.

- *collection_size*: Size of the client MongoDB collection at this moment.

- *collection_avgObjSize*: Average size of documents (ingested rows or observations) in the client MongoDB collection at this moment.

# Part 2 - Near-realtime ingestion

### 1. For near-realtime ingestion, you introduce a simple message structure ingestmessagestructure that all consumers have to use. Design and implement ingestmessagestructure for your customers; explain your design.

For answering this question I have done my implementation according to the nature of the client data. In my implementation *client1* uses *googleplaystore.csv* which is dense, does not have any sparse values and contains several features, and *client2* uses reviews data which has many missings, is more sparse and the format of the data varies. That is why I have defined two different *ingestmessagestructure* for each data file type.

Then, *client1* which uses a comma-separated values format (*.csv*) and *client2* uses a key value pairs format (*.json*). You can find how my implementation handles these two *ingestmessagestructure* in the file *client_to_mysimbdp-databroker.py* which is the client-side script that connects to the message broker in a server (created with *mysimbdp-streamingestmanager.py* and *clientstreamingestapp.py*) for sending data files via messages to *RabbitMQ* topics.

### 2. Customers will put their data into messages following ingestmessagestructure to send the data to a message broker, mysimbdp-databroker (provisioned by mysimbdp) and customers will write a program, clientstreamingestapp, which read data from the broker and ingest data into mysimbdp. Provide a component mysimbdp-streamingestmanager, which invokes on-demand clientstreamingestapp (e.g., start, stop). mysimbdp imposes the model that clientstreamingestapp has to follow.

The implementation of this question is done in files *mysimbdp-streamingestmanager.py* and *clientstreamingestapp.py*. The first one is a component publishes into a *RabbitMQ* topic the available ingestion topics to be consumed by *client_to_mysimbdp-databroker.py* and also invokes customer's clients' apps to perform the ingestion when messages are received by the message broker. The second is a program provided by the clients (coded by me as an example), which will take the customer's message received by the message broker via *RabbitMQ* topics, ingest them into the final *mysimbdp-coredms* MongoDB, and reports the ingestion to *mysimbdp-streamingestmanager.py* via another *RabbitMQ* topic.

In more detail, *mysimbdp-streamingestmanager.py* uses the reported ingestion information from the client app to dynamically create parallel ingestion topics and apps for each client according to the ingestion load/time. It is also able to stop open topics and active apps if the ingestion load/time reduces. Moreover, it also sends to client (*client_to_mysimbdp-databroker.py*) the available ingestion *RabbitMQ* topics that are currently, available and active to ingest. It is a nice feature because it enables the customer to be synchronized with the server system.

Note that this is just my example client app and the customer would be able to access the message broker through for example other coding languages or systems. Moreover, the client app should be able to receive as input the server address and *RabbitMQ* topic to know where to subscribe and send the message. Currently, it is dependent on sys args to achieve this. The code provided by the client should be able to read the topic name from the command line argument.

Also note that due to the very dynamic nature of the problem and the scoop of the project, it is difficult to ensure perfect data security since it is possible that in unlikely cases, it is possible that the ingestion *RabbitMQ* topic that the customer is trying to access (chosen randomly out of the available ones in my implementation) has been closed and some data observations may be not ingested into MongoDB.

### 3. Develop test programs (clientstreamingestapp), test data, and test profiles for customers. Show the performance of ingestion tests, including failures and exceptions, for at least 2 different customers in your test environment.

To answer this question, the implementation is done in the components mysimbdp-streamingestmanager.py and clientstreamingestapp.py. The first one receives reporting and ingestion statistics from the customer app and MongoDB collections and accumulates it into the file *logs/near-realtime_ingestion.log*. In the log file provided you can find the information of the ingestion of the messages of each client (explained in *README.md*) into the database MongoDB using near-realtime mode. As you can see these performance ingestion reports are separated by client ID and message chunks or blocks.

In this log file with the testing of the performance of ingestion, we can see that the number of messages ingested by each client ID. By default, each app reports every 1000 messages sent via each active app and that is why I get the test performance reports every this number of messages. By ingesting the datafiles mentioned with *client_to_mysimbdp-databroker.py* you can see in the log file that the total number of document in each client ID collection increases until having a total number of document equal to the number of rows or observations in the files. Moreover, for each report you can find the average message ingestion time (from the message broker to the MongoDB) and it is pretty fast around 0.04 seconds in mean (faster than assignment 1, sending single rows via *REST APIs* and also direct ingestion from client to database, because now it does not wait for the message to be inserted to the database). Also, you can find the average message total time which is the difference between the message ingestion end and the time that the client sends it. Obviously, it increases at each report since once the client has sent the files to the server, *RabbitMQ* is queueing the messages ingestion.

### 4. clientstreamingestapp decides to report its processing rate, including average ingestion time, total ingestion data size, and number of messages to mysimbdpstreamingestmanager within a pre-defined period of time. Design the report format and the communication mechanism for reporting.

As explained before, the implementation of this question is done in *mysimbdp-batchingestmanager.py* component which receives reporting and ingestion statistics from the customer app *clientbatchingestapp--client#.py* and MongoDB collections and accumulates it into the file *logs/batch_ingestion.log* (only for files that has been staged and then ingested into the database).

Firstly, I use as the communication mechanism for reporting a *RabbitMQ* topic to sent the report between the active client apps and the manager. Basically, this way is useful because I only need to take care of local communication in the server without other internet protocols. Also, it is practical for the client-side since he only needs to push the report to the right reporting *RabbitMQ* topic from his app/program. Note that as you can see in my implementation code, every active app reports the ingestion report to the manager every 1000 messages but you can change as you prefer).

According to the design of the ingestion, my report implementation includes several information:

- *number_messages*: Number of messages ingested (rows or observations in the file).

- *avg_total_time*:  Average total time taken to ingest each message from the client sending time message broker into the MongoDB.

- *avg_ingestion_time*: Average time taken to ingest each message from the message broker into the MongoDB.

- *collection_count*: Number of documents (ingested rows or observations) in the client MongoDB collection at this moment.

- *collection_size*: Size of the client MongoDB collection at this moment.

- *collection_avgObjSize*: Average size of documents (ingested rows or observations) in the client MongoDB collection at this moment.

### 5. Implement the feature to receive the report from clientstreamingestapp. Based on the report from clientstreamingestapp, when the performance is below a threshold, e.g., average ingestion time is too low, or too many messages have to be processed, mysimbdp-streamingestmanager decides to create more instances of clientstreamingestapp. Define a model for specifying constraints for creating/removing instances for each customer.

As explained before, the implementation of this question is done in *mysimbdp-batchingestmanager.py* component which receives reporting and ingestion statistics from the customer app *clientbatchingestapp--client#.py* and MongoDB collections. Then, based on the report received from the client app, the manager app activates a new client app and the corresponding *RabbitMQ* topic for the client to be able to send a higher number of concurrent messages request to the broker. Moreover, it also able to stop the open topics and active apps if the ingestion load/time reduces. Concretely, I use the average total time in the report but you could modify it to another reported information.

# Part 3 - Integration and Extension

### 1. Produce an integrated architecture for both batch and near-realtime ingestion features in this assignment and explain the architecture.

Actually, the architecture of my Big Data platform developed is already integrated into both types of ingestion. Since both ingestion modes have the same ingestion destination/endpoint by client ID which is the MongoDB database and the respective client collection. In other words, it does not matter which type of ingestion method the client chooses to ingest, all go to the same table in the database.

### 2. Assume that if a file for batch ingestion is too big to ingest using the batch ingestion implementation in Part 1, design your solution to solve this problem by reusing your batch or near-realtime components in Parts 1 or 2.

I will explain my implemented solutions for both batch or near-realtime. Firstly, for batch mode you can find in *mysimbdp-fetchdata.py* the argument *micro_batching* which splits the batch file in the folder *client-input-directory* and stage all microbatches int *client-stage-directory* to be ingested. As explained before, it does it if the file size ingestion constraint in *config_ingestion_constraints.json* is not satisfied. Secondly, as mentioned before for near-realtime mode via a *RabbitMQ* as message broker you can find in my implementation that *mysimbdp-batchingestmanager.py* receives reporting and ingestion statistics from the customer app *clientbatchingestapp--client#.py* and MongoDB collections, and based on the report received it activates a new client app and the corresponding *RabbitMQ* topic for the client to be able to send a higher number of concurrent messages request to the broker. It means that if the messages queues get busy and it takes a lot of time to process them, the issue is detected and the server activates parallel topics/apps to handle a lot of messages or big files.

### 3. Regardless of programming languages used, explain why you as a platform provider should not see the code of the customer, like clientbatchingestapp and clientstreamingestapp. In which use cases, you can assume that you know the code?

Several cloud platforms are offering automatic services related to executing client code without knowing it. Nowadays, this is very useful since the data and code development of companies is getting more and more importance in terms of business assets, that is why many companies would not be interested in sharing the code but would be interested in a service like this. Also, the legal and privacy laws are changing and increasing, that is why it is not a good idea to ask/use/see the client code when you are providing a service. Then, the provider should guarantee security and confidentiality to the clients. About use cases where you can assume that you know the code, for example, when a company is deploying a Big Data platform not in the cloud but in "local" then can avoid this code confidentiality problems.

### 4. If you want to detect the quality of data and allow ingestion only for data with a pre-defined quality of data condition, how you, as a platform provider, and your customers can work together?

As mentioned, my database component is MongoDB. In this case, for example, I could add a data schema validation MongoDB level for each collection. Then, when ingesting data to a collection from the client app, this schema would be checked and if not satisfied by the data request an error information message is sent back to the client. Note that this schema should be discussed and agreed by both parties, client and platform provider.

### 5. If a consumer has multiple clientbatchingestapp and clientstreamingestapp, each is suitable for a type of messages or files, how would you extend your design and implementation in Parts 1 & 2 (only explain the concept/design) to support this requirement.

This situation is already implemented for both ingestion methods since in my default case *client1* uses *.csv* files and *client2* uses *.json* files. For batch mode, the client side script can send to server both data file types and the manager can open a different client app no matter the request file type is. For near-realtime mode, the client side script can also send to message broker both data file types through the corresponding *RabbitMQ* topic and then the manager can simply open a client app and the corresponding *RabbitMQ* topic as explained many times independently of the initial file/message type.

# Bonus points

### If you can design and implement the dynamic management of instances for Part 2 Question 5.

I have done this implementation. Related files: *mysimbdp-streamingestmanager.py* and *clientstreamingestapp.py*. More details in question 2.5 answer.

### If you can develop the solution that automatically switches from batch to microbatching based on a set of constraints (e.g., file size, time, bandwidth).

I have done this implementation. Related files: *mysimbdp-fetchdata.py*. More details explained during all this report.