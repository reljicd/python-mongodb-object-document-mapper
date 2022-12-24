#!/usr/bin/env bash

export CONTAINER_NAME=mongo_odm
echo -e "\nSet docker container name as ${CONTAINER_NAME}\n"

echo -e "\nStop running Docker containers with container name ${CONTAINER_NAME}...\n"
docker stop "$(docker ps -a | grep ${CONTAINER_NAME} | awk '{print $1}')"

stop_and_delete_containers() {
  echo -e "\nStop running Docker containers with container name ${CONTAINER_NAME}...\n"
  docker stop "$(docker ps -a | grep ${CONTAINER_NAME} | awk '{print $1}')"

  echo -e "\nStop and delete Mongo containers... \n"
  docker stop "$(docker ps -a | grep mongo | awk '{print $1}')"
  docker rm "$(docker ps -a | grep mongo | awk '{print $1}')"
}

stop_and_delete_containers

docker-compose -f docker/docker-compose.yml build

echo -e "\nStart Docker Compose...\n"
docker-compose -f docker/docker-compose.yml run --rm \
  --name ${CONTAINER_NAME} \
  ${CONTAINER_NAME} -m pytest /app/tests

stop_and_delete_containers
