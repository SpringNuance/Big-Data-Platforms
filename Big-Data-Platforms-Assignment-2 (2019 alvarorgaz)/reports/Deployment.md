# Set up Cloud MongoDB

I have created a *MongoDB Atlas* cluster at https://cloud.mongodb.com as database and it is always running on the cloud. Then, in section "Network Access" I have added an IP Whitelist address "0.0.0.0/0" to allow access from anywhere. Finally, the corresponding API URL is used in the code.

In case you want to set up another database, create one at the provided link by configuring a username, password and IP address. Then the database is ready to use and you only need to change the respective URL in the code.

# Set up Google Cloud Platform Virtual Machine with RabbitMQ

Launch an image of a *Google Cloud Platform RabbitMQ Certified by Bitnami* virtual machine at https://console.cloud.google.com/marketplace/details/bitnami-launchpad/rabbitmq?project=fresh-office-232310. You will need to obtain the user name and password of *RabbitMQ* provided.

**Add firewall rules:**

Go to the "View network details" section of your VM instance, then go to "Firewall rules" section and create 2 firewall rules. One to allow traffic from all IP addresses (*ingress*) and one to send traffic to all IP addresses (*egress*).

- Set the direction of traffic as "Egrees", the destination IP ranges as "0.0.0.0/0", and the protocols and ports as "Allow all".

- Set the direction of traffic as "Ingrees", the destination IP ranges as "0.0.0.0/0", and the protocols and ports as "Allow all".

# Set up a Python virtual environment

Connect into the VM by SSH and run the following commands in the root folder of the repository:

    1. sudo apt-get install python3-pip
    2. sudo pip3 install virtualenv
    3. virtualenv env
    4. source env/bin/activate
    5. pip3 install -r requirements.txt

# Run code

The folders *code/client-input-directory* and *code/client-stage-directory* which are needed to run the code. Connect into the VM by SSH and run the following commands in the root folder of the repository to enable the both ingestion modes in your VM as server:

    1. source env/bin/activate
    2. mkdir code/client-input-directory
    3. mkdir code/client-stage-directory
    4. nohup sudo env/bin/python code/mysimbdp-daas.py &
    5. nohup sudo env/bin/python code/mysimbdp-fetchdata.py --micro_batching "Yes" &
    6. nohup sudo env/bin/python code/mysimbdp-batchingestmanager.py > logs/batch_ingestion.log &
    7. nohup sudo env/bin/python code/mysimbdp-streamingestmanager.py --server_address "35.228.167.103" &
    
Now you are ready to ingest data (in batch or near-realtime modes) by running the code (described in the *README.md* file) from the same VM instance or another machine (although in this case, you may set up the same Python virtual environment). Note that you will have to specify the server address as the external IP of your VM. You can read the help of all the arguments for more information. 

For example, for ingesting data files in batch mode, you can run:

    python code/client_file_to_mysimbdp-daas.py --client_id "client1" --server_address "http://35.228.167.103/" --dataset_path "data/googleplaystore.csv"
    
    python code/client_file_to_mysimbdp-daas.py --client_id "client2" --server_address "http://35.228.167.103/" --dataset_path "data/googleplaystore_user_reviews.json"
    
For example, for ingesting data in near-realtime mode, you can run:

    python code/client_to_mysimbdp-databroker.py --client_id "client1" --server_address "35.228.167.103" --dataset_path "data/googleplaystore.csv"
    
    python code/client_to_mysimbdp-databroker.py --client_id "client2" --server_address "35.228.167.103" --dataset_path "data/googleplaystore_user_reviews.json"

*Note*: For the near-realtime mode, in *clientstreamingestapp.py* you can modify the report message frequency and in *mysimbdp-streamingestmanager.py* the ingestion time threshold for creating new client app instances and their corresponding *RabbitMQ* topics. For the batch mode, you can modify the client IDs and ingestion constraints for them in the configuration JSON file (described in the *README.md* file). By default, the constraints are:

- *client1*: file type "csv", max file size 1MB (1048576 bytes), max files number 10.

- *client2*: file type "json", max file size 1MB (1048576 bytes), max files number 5.