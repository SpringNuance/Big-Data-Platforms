# Set up Cloud MongoDB

I have created a *MongoDB Atlas* cluster at https://cloud.mongodb.com as database and it is always running on the cloud. Then, in section "Network Access" I have added an IP Whitelist address "0.0.0.0/0" to allow access from anywhere. Finally, the corresponding API URL is used in the code.

In case you want to set up another database, create one at the provided link by configuring a username, password and IP address. Then the database is ready to use and you only need to change the respective URL in the code.

# Set up Google Cloud Platform Virtual Machine

Launch an image of a *Google Cloud Platform Kafka Certified by Bitnami* virtual machine at https://console.cloud.google.com/marketplace/details/bitnami-launchpad/kafka.

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

Connect into the VM by SSH and run the following commands in the root folder of the repository:

    1. source env/bin/activate
    2. nohup sudo env/bin/python code/mysimbdp-daas.py &

Now you are ready to ingest data by running the code (described in the *README.md* file) from the same VM instance or another machine (although in this case you may set up the same Python virtual environment). Note that you will have to specify the server address as the external IP of your VM. You can read the help of all the arguments for more information. For example yu can run:

    python code/performance_multiple_requests.py --n_threads 6 --n_requests_by_thread 1000 --ingestion_mode "daas" --server_address "http://35.228.191.152/" > logs/performance_daas_gcp_6threads.log

    python code/client_to_mysimbdp-daas.py --n_requests 1000 --ingest_all "No" --server_address "http://35.228.191.152/" --dataset "reviews"

    python code/mysimbdp-dataingest.py --dataset "apps"

For reading data from the database you can use the external IP address of the VM to filter by app name in the browser:

    http://35.228.191.152/