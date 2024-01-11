# Part 1 - Design

### 1. Design and explain interactions between main components in your architecture of *mysimbdp*.

The following diagram shows the architecture of the design of my Big Data platform. This is the description and function of each main component:
    
  - *Client PC*: This component represents the external clients, consumers or users that want to connect to the database for storing or reading data from their own machine at any time. Then, the database has to be available and running on the cloud to maintain access for the users. In this assignment, as you can see in the code, I have simulated different clients or concurrent requests to the database by using multiple threads option in Python.
    
  - *REST APIs*: This component built-in Python represents the *mysimbdp-daas* which defines a set of APIs on a remote server and allows the clients to talk to it. Those can do requests (for sending data to store or reading it) via the corresponding endpoint or URL and get a response. Moreover, this component connects the requests to the following component *Data Processing* for accessing the database.

  - *Data Processing*: This component built with Python PyMongo contains tools for interacting with the MongoDB database from Python and is the interaction between the requests received from clients and the database. It works as the final ingestion component from *REST APIs* or directly from *Client PC*.
    
  - *Database MongoDB*: This is the component to store and manage data *mysimbdp-coredms* and it is basically a Mongo database available on the cloud. In more detail, I created a cluster in https://cloud.mongodb.com (more implementation details on file *reports/Deployment.md*) and used the corresponding URL to access to it.

<p align="center">
<img src="Figures/architecture.png" width="500">
<p>

The interactions between these components are developed in shell scripts in Python mainly using the modules *pymongo* and *flask* which is a micro web framework written in Python. Now I will explain the connections between the main components:

  - From *Client PC* to *REST APIs*: This connection is done via the Python file *code/client_to_mysimbdp-daas.py* and it is the client-side script that connects to the *REST APIs* (created with *code/mysimbdp-daas.py*) for storing data into *mysimbdp-coredms* MongoDB.
    
  - From *REST APIs* to *Data Processing*: This connection is done inside the shell script *code/mysimbdp-daas.py* using the request data sent from the client.
     
  - From *Client PC* to *Data Processing*: This connection enables the clients to read data from their external data sources (files/external databases) and then store the data by directly calling APIs of *mysimbdp-coredms* MongoDB instead of accessing it via *REST APIs*. The corresponding client-side script is *code/mysimbdp-dataingest.py*.
     
  - From *Data Processing* to *Database MongoDB*: This connection to the MongoDB cluster is provided by the Python module *pymongo*.
    
  - From *Database MongoDB* to *Client PC*: Apart from storing data requests, as you can see in the diagram I enable the clients to read data from the database. It is done via the *REST APIs* component which creates an API in the external IP of the remote server to filter data in the database by filtering the app name in the tables of my MongoDB cluster.

One note about the implementation is that for keeping the *REST APIs* available and running for clients I have used as the remote server a *Google Cloud Platform Kafka Certified by Bitnami* virtual machine to run the shell script *code/mysimbdp-daas.py*. Then, I can access it as a client from any other machine at any time.

### 2. Explain how many nodes are needed in the deployment of *mysimbdp-coredms* so that this component can work property (theoretically based on the selected technology).

The number of components needed for the deployment of my *mysimbdp-coredms* based on the selected technology Mongo database is 3 without considering the clients or customers as components. The first one is the *REST APIs*, the second one is the *Data Processing*, and the third is the *Database MongoDB* on itself.

### 3. Will you use VMs or containers for *mysimbdp* and explain the reasons for each component.

I use VMs for my *mysimbdp*. As explained before, I have used a *Google Cloud Platform Kafka Certified by Bitnami* Linux Debian virtual machine for keeping the *REST APIs* available and running for clients. Moreover, for setting up the database I have created a *Database MongoDB* cluster cloud service too. Then according to the components of my Big Data platform, as well as the fact that my local system is Windows and all the tools are easier to deploy on Linux, it is an appropiate, stable and easy way to set up my *mysimbdp*.

Since VMs are completely isolated from the host operating system, they are a safe place for experimenting and developing applications, and hence more secure. Moreover, since containers share the host's kernel, they cannot be as isolated as VMs. Consequently, containers are process-level isolated and one container can affect others by compromising the stability of the kernel, that is why they can do not offer the same security and stability that VMs.

### 4. Explain how would you scale *mysimbdp* to allow a lot of users using *mysimbdp-dataingest* to push data into *mysimbdp*.

My system is already scaled for several users to ingest data. To scale up my *mysimbdp* and allow authentication of several customers to ingest data into the database I use the *REST APIs* component in a remote server which connects the clients' requests to the database *Database MongoDB* component via the *Data Processing* component. Then the users will not have access to the database directly. This is developed in the shell script *code/mysimbdp-daas.py* which I run in a virtual machine to set up the corresponding APIs endpoints, then a lot of users can send requests for pushing data and the Python modules used on this implementation handle requests from several clients. This is tested by using multiple threads option in Python. Moreover, the *Database MongoDB* cloud-based service helps to handle the requests queue too.

### 5. Explain your choice of industrial cloud infrastructure and/or *mysimbdp-coredms* provider, when you do not have enough infrastructural resources for provisioning *mysimbdp*.

The choice of the industrial cloud infrastructure provider is based on the needs, duration and type of this project. On the one side, the *Google Cloud Platform*, as well as another cloud service, provides the highly-scalable cloud computing tools that we need in a cheap way, secure, and automatic maintenance. For example, for companies that need to use cloud service sporadically, it is very time-consuming and expensive to set up and maintain their own Big Data platform with local resources, comparing to rent cloud service. On the other side, MongoDB is easy to deploy and fully automated database cloud service with the operational and security best practices built-in. Then, these choices have been a good option due to the short term duration and the fact that my machine does not have enough resources for provisioning *mysimbdp* efficiently.

# Part 2 - Development and deployment

### 1. Design and explain the data schema/structure for *mysimbdp-coredms*.

My *mysimbdp-coredms* is MongoDB which is a cross-platform JSON document-oriented database that uses JSON data schema. MongoDB has been able to implement an automatic sharding solution with much better scaling and performance characteristics than you would normally be stuck with if you had to take relational joins and transactions into account.

JSON data schema is a standard that allows document data to be checked with a variety of tools before it is even imported into the database. The JSON documents stored in the database can have varying sets of fields with different types for each field, and you can define the data type of each property and how it should be validated to check for the range of values. For example, in our *Google Play Store* app information a possible requested JSON document could be:

    {
      "_id": {
        "$oid": "5d9c650e3ec2be0ffb733958"
      },
      "App": "Photo Editor & Candy Camera & Grid & ScrapBook",
      "Category": "ART_AND_DESIGN",
      "Rating": {
        "$numberDouble": "4.1"
      },
      "Reviews": "159",
      "Size": "19M",
      "Installs": "10,000+",
      "Type": "Free",
      "Price": "0",
      "Content Rating": "Everyone",
      "Genres": "Art & Design",
      "Last Updated": "January 7, 2018",
      "Current Ver": "1.0.0",
      "Android Ver": "4.0.3 and up"
    }

Then, we could infer the JSON schema from it. Moreover, as we can see in the following image, in my MongoDB cluster I have created 1 database containing 2 collections of documents or tables (for apps and reviews datasets respectively) with the implementation code via *Data Processing* component.

<p align="center">
<img src="Figures/mongodb_cluster.png">
<p>

### 2. Explain how would you partition the data in *mysimbdp-coredms* into different shards/partitions.

Database systems with large datasets or high throughput applications can challenge the capacity of a single server. For example, high query rates can exhaust the CPU capacity of the server. Working dataset sizes larger than the system's RAM stress the I/O capacity of disk drives. Then, there are two methods for addressing system growth:

- *Vertical scaling*: Involves increasing the capacity of a single server, such as using a more powerful CPU, adding more RAM, or increasing the amount of storage space.

- *Horizontal scaling*: Involves dividing the system dataset and load over multiple servers, adding additional servers to increase capacity as required. The trade-off is increased complexity in infrastructure and maintenance for the deployment.

MongoDB supports horizontal scaling through sharding. *Sharding* is a method for distributing data across multiple machines or the shards in the cluster, allowing each shard to contain a subset of the total cluster data documents. As the dataset grows, additional shards increase the storage capacity of the cluster. MongoDB uses sharding to support deployments with very large datasets and high throughput operations. MongoDB uses the shard key to distribute the collection's documents across shards. The shard key consists of a field or fields that exist in every document in the target collection and MongoDB uses it for the split data into chunks. Each chunk is then assigned a range based on the shard key values in a way that the shards should have a similar size.

For example, in our dataset of apps information we could use the feature about content rating to assign each document to a particular shard:

- In shard 1 categories: "Everyone", "Teen", "Everyone 10+".

- In shard 2 categories: "Mature 17+", "Adults only 18+", "Unrated".

### 3. Write a *mysimbdp-dataingest* that takes data from your selected sources and stores the data into *mysimbdp-coredms*.

As explained in the first question, in my architecture clients or customers can access the *mysimbdp-coredms* MongoDB in two ways: via connecting to the *REST APIs* component or directly to the *Data Processing* component using MongoDB API.

For this question, the corresponding client-side script is *code/mysimbdp-dataingest.py*. It connects the components *Client PC* to *Data Processing*, and this connection enables the clients to read data from their external data sources (files/external databases) and then store the data by directly calling APIs of *mysimbdp-coredms* MongoDB instead of accessing it via *REST APIs*. 

### 4. Given your deployment environment, show the uploading performance (response time and failure) of the tests for 1,5, 10, .., n of concurrent *mysimbdp-dataingest* pushing data into *mysimbdp-coredms*.

To study the request time performance given my deployment environment I will use multiple threads option in Python for simulating 1, 2, 4, 6, 8, 10, and 50 concurrent clients ingesting 1000 data requests. Then, I will study 3 scenarios for comparing the ingestion time between them by running the script *code/performance_multiple_requests.py* (instructions in the file *code/Deployment.md*):

  1. Using REST APIs with the server in a GCP virtual machine (set up by running shell script *code/mysimbdp-daas.py*).

  2. Using REST APIs with the server in my local machine (set up by running shell script *code/mysimbdp-daas.py*).
  
  3. Directly from client data using MongoDB API (same as the client-side script *code/mysimbdp-dataingest.py*).
  
In the following plots we have the results:

<p align="center">
<img src="Figures/performance_mean.png" width="600">
<img src="Figures/performance_std.png" width="600">
<p>

Under scenario 1, the following plot shows the mean and standard deviation of the request time response by concurrent threads simulating clients pushing data at the same time. As we can see there is a bottleneck since the mean increase linearly until 10 clients and then strongly for 50 clients, which make sense since the system needs to queue all this concurrent request, having minimum time response at 0.0938 seconds with 2 concurrent threads and maximum at 0.4742 seconds with 50 concurrent threads. Also, the plot shows the standard deviation of the data request by concurrent threads.

Under scenario 2, the following plot shows that in this case the mean of the request time response increases but with less slope by concurrent threads simulating clients pushing data, having minimum time response at 0.0648 seconds with 2 concurrent threads and maximum at 0.423 seconds with 50 concurrent threads. Moreover, we can appreciate that the request time response is lower for all number of threads compared to the previous case. It makes sense since in the previous case we are sending a request from the local machine to the VM and the connection latency increases the time needed.

Regarding the scenario 3, the following plot shows that in this case the mean of the request time response is very low around 0.05 seconds until 6 concurrent threads and then a bottleneck is produced increasing up to 0.4776 seconds with 50 concurrent threads. This result is reasonable since the time needed for doing the request to the *REST APIs* is deleted and we are connecting directly to the APIs of *mysimbdp-coredms* MongoDBthe. However, we can see that the standard deviation increases a lot by concurrent threads and in the previous scenarios was more constant. This can mean that the request queue is tackled in a different way between only *Data Processing* and with also *REST APIs*.

About the request failures, as you can see in the performance logs files, the system does not give any request error and it ingests correctly all data for the tried experiments. It means that the tools used (mainly Python modules *threading*, *flask*, *pymongo* and MongoDB itself) are queueing the concurrent requests.

### 5. Observing the performance and failure problems when you push a lot of data into *mysimbdp-coredms* (you do not need to worry about duplicated data in *mysimbdp*), propose the change of your deployment to avoid such problems (or explain why you do not have any problem with your deployment).

The conclusion of previous results shows that my system has a bottleneck problem when many clients or costumers send requests to the *mysimbdp-coredms*. Then, for avoiding this issue I propose to add a layer before the ingestion by using a queue system tool such as *Apache Kafka* and *MQTT*.

*Apache Kafka* is a real-time streaming platform that has been optimized to stream data between systems and applications as fast as possible in a scalable manner. It is a highly scalable distributed streaming platform which ingests, stores, processes, and forwards high volumes of data from thousands of IoT devices.

*MQTT* is a widely used ISO standard publish-subscribe-based messaging protocol which is mainly used for IoT scenarios (like connected cars or smart home devices). However, it is not built for high scalability, longer storage, or easy integration to legacy systems. 

Therefore, for example, in this project using both could be a good combination of end-to-end integration from the edge to the data center and back.

# Part 3 Extension with discovery

### 1. Assume that each of your tenants/users will need a dedicated *mysimbdp-coredms*. Design the data schema of service information for *mysimbdp-coredms* that can be published into an existing registry (like ZooKeeper, consul or etcd) so that you can find information about which *mysimbdp-coredms* for which tenants/users.

In this case, we would have a different *mysimbdp-coredms* for each client, and then we would have to store the client id and the corresponding MongoDB service information in a registry service such as ZooKeeper, which is useful to manage configuration information in a centralized and secure way providing distributed synchronization. In this case, the client user would be matched and connected with its corresponding database.

### 3. Explain how you would change the implementation of *mysimbdp-dataingest* (in Part 2) to integrate a service discovery feature (no implementation is required).

In a traditional application running on physical hardware, the network locations of service instances are relatively static. For example, my script *code/mysimbdp-dataingest.py* uses the API of MongoDB cluster that can be occasionally updated. But in a modern cloud-based application, this is a much more difficult problem to solve since the service instances have dynamically assigned network locations. Moreover, the set of service instances changes dynamically because of auto-scaling, failures, and upgrades. Consequently, the client code needs to use a more elaborate service discovery mechanism.

Service discovery functions by using a common network protocol, which allows agents to use each other's services. Protocols used include Dynamic Host Configuration Protocol (DHCP), DNS Service Discovery (DNS-SD) and Service Location Protocol (SLP). The database which contains service instances and network locations is called the service registry. The service registry is made up of server clusters containing databases of available service instances, which should be continually kept up to date.

In client-side service discovery, the client service is responsible for determining network locations of service instances. The client accomplishes this by querying a service registry. This service discovery option benefits from being straightforward and I would change the implementation of *mysimbdp-dataingest* by firstly adding a module to access the service registry (such as connecting to ZooKeper) to query it and finding the network location of the corresponding server service instance of *mysimbdp-coredms*.

### 4. Explain APIs you would design for *mysimbdp-daas* so that any other developer who wants to implement *mysimbdp-dataingest* can write his/her own ingestion program to write the data into *mysimbdp-coredms* by calling *mysimbdp-daas*.

This scenario does not differ from one of the ingestion options in my *mysimbdp* architecture since I have created the *REST APIs* component and clients or customers can access the database by using the client-side script *code/client_to_mysimbdp-daas.py*, which sends requests to the corresponding *REST APIs* via the corresponding server address or endpoint created.

Then, under my architecture, the APIs needed so that any other developer who wants to implement the data ingestion can write his/her own ingestion program by calling *mysimbdp-daas* are:

  - APIs for the external server *mysimbdp-daas* which enables ports for ingestion into each table of my MongoDB cluster. In my development: http://35.228.191.152/apps/ingestion and http://35.228.191.152/reviews/ingestion. It should be provided to the developer.
  
  - MongoDB APIs to access the *mysimbdp-coredms* after receiving the client requests via *mysimbdp-daas*. In my development it corresponds to "mongodb+srv://alvarorgaz:XLao4jEcoIz3kFXH@big-data-a1-j25ko.gcp.mongodb.net/admin?retryWrites=true&w=majority". But it should not be provided to the developer since it is used in *mysimbdp-daas* to connect to the MongoDB.

Here you can find the APIs options that I have created:

<img src="Figures/APIs.png">

### 5. Assume that now only *mysimbdp-daas* can read and write data into *mysimbdp-coredms*, how would you change your *mysimbdp-dataingest* (in Part 2) to work with *mysimbdp-daas*.

As in the previous question, this scenario does not differ from one of the ingestion options in my *mysimbdp* architecture, the one for connecting to the *mysimbdp-coredms* MongoDB via the *REST APIs* component by using the client-side script *code/client_to_mysimbdp-daas.py*. In this case, only *mysimbdp-daas* can read and write data into *mysimbdp-coredms* and clients do not have direct access to the MongoDB API. The client-side script *code/client_to_mysimbdp-daas.py* could be written in other programming languages once the server address is provided.

Basically, the difference between *code/mysimbdp-dataingest.py* and *code/client_to_mysimbdp-daas.py* is that in the second case, which is the corresponding to this question, the client only knows the server address for ingestion and sends a request to this server that will connect to the database itself and give an answer to the client.

# Bonus points

I have developed the bonus part since in the architecture of my *mysimbdp* clients can access the database in two ways. First one is via the script *code/mysimbdp-dataingest.py* which reads data from data sources (files/external databases) of the client/user and then store the data by directly calling APIs of *mysimbdp-coredms* MongoDB. The second one is the bonus part based on the component *REST APIs* developed in the shell script *code/mysimbdp-daas.py* that sets up the *REST APIs* which can be called by external data clients/consumers (using the client-side script *code/client_to_mysimbdp-daas.py*) to store/read data into/from *mysimbdp-coredms* MongoDB. Moreover, in section 2.4 I have tested its ingestion performance in scenarios 1 and 2 and compared them to the 3.