#!/bin/bash

docker-compose up -d mongo  && docker-compose up -d mongo1 && docker-compose up -d mongo2

sleep 5

docker-compose exec mongo /scripts/rs-init.sh

sleep 5

docker-compose up -d