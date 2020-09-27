#!/bin/bash

echo -e "\n------"
echo "Start docker-build.sh..." && \
echo "stop and remove container..."
docker stop exp_celery_workers
docker rm exp_celery_workers
echo "docker images:"
docker images -a|grep exp-analysis|grep -v none
cd `dirname $0`
pwd
tags=$(date +%Y%m%d-%H%M)
docker build ./ -t exp-analysis:${tags}
docker tag exp-analysis:${tags} exp-analysis:latest
docker images -a|grep exp-analysis|grep -v none|awk '{print $1":"$2}'|grep -v latest|grep -v ${tags}|xargs docker rmi
echo "docker images:"
docker images -a|grep exp-analysis|grep -v none
echo -e "------\n"
