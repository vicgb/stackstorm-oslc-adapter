#!/bin/bash
# Change paths into your own folders. 
# You should have installed st2-docker repo modified with the MongoDB RS and Kafka instance as explained on the README.md

cd st2-docker
echo "Starting the Stackstorm and Kafka environment..."
sleep 2
sh start-st2.sh
echo "Stackstorm and Kafka deployment completed"
sleep 2

#Stackstorm auth
echo "Obtaining authentication token..."
sleep 3
#Default password: Ch@ngeMe 
token=$(curl -X POST -k -u st2admin:$ST2_PASSWORD http://localhost/auth/v1/tokens | jq -r .token) 

cd $PWD/st2-oslc-adapter
sed -i "5d" .env
echo "TOKEN=$token" >> .env


sleep 2 
echo "Login succeded"


# MongoDB Monitoring
cd $PWD/st2-oslc-adapter/st2api
python3 monitoring.py &
sleep 2
echo "Monitoring module deployment completed"

# Stackstorm-OSLC Adapter
sleep 2
echo "Starting Stackstorm-OSLC Adapter Graph Manager"
sleep 4
cd $PWD/st2-oslc-adapter
flask run 






