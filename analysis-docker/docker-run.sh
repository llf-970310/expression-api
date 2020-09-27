#!/bin/bash

echo -e "\n------"
echo "Now run exp_celery_workers..." && \
# docker run --restart=always -d -v /expression/temp_audio:/expression/temp_audio --name exp_celery_workers exp-analysis --loglevel=info --concurrency=20 && \
docker run --restart=always -d -v /expression/audio:/expression/audio --net=host --name exp_celery_workers exp-analysis && \
echo "Now waiting for 3 seconds..." && \
sleep 3s && \
echo "Now this is the result of docker ps:" && \
docker ps
echo -e "------\n"
