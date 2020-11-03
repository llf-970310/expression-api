#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-1-6

from celery import Celery
from collections import namedtuple

from kombu import Queue

pw = 'ise_expression'
celery_broker = 'amqp://admin:%s@106.13.160.74:5672/' % pw
celery_backend = 'redis://:%s@106.13.160.74:6379/7' % pw

app = Celery('tasks', broker=celery_broker, backend=celery_backend)
app.conf.task_queues = (
    Queue('q_type3', queue_arguments={'x-max-priority': 100}),
    Queue('q_type12', queue_arguments={'x-max-priority': 2}),
    Queue('q_pre_test', queue_arguments={'x-max-priority': 500}),
    Queue('default', queue_arguments={'x-max-priority': 1}),
)

__Queue = namedtuple('Queue', 'pretest type12 type3')
queues = __Queue('q_pre_test', 'q_type12', 'q_type3')


@app.task(name='analysis_12')
def analysis_main_12(current_id_str, q_num_str):
    pass


@app.task(name='analysis_3')
def analysis_main_3(current_id_str, q_num_str):
    pass


@app.task(name='analysis_pretest')
def analysis_wav_pretest(test_id_str):
    pass
