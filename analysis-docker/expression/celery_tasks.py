#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 18-8-18

import datetime
import logging
import traceback
from celery import Celery

from utils_file import get_wav_file_bytes_io
import celery_config
import config
import db
import analysis_features
import analysis_scores

app = Celery('tasks', broker=config.Celery_broker, backend=config.Celery_backend)
app.config_from_object(celery_config)

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s:\t%(message)s')


@app.task(name='analysis_12')
def analysis_main_12(current_id, q_num):
    return analysis_main(current_id, q_num)


@app.task(name='analysis_3')
def analysis_main_3(current_id, q_num):
    return analysis_main(current_id, q_num)


@app.task(name='analysis_pretest')
def analysis_wav_pretest(test_id):
    return analysis_test(test_id)


def analysis_test(test_id):
    logging.info("test_id: %s" % test_id)

    mongo = db.Mongo()
    wav_test_info = mongo.get_wav_test_info(test_id)

    result = {"status": "finished", "feature": {}}
    audio_key = ''
    file_location = ''
    try:
        file_location = wav_test_info.get('file_location', 'local')
        audio_key = wav_test_info['wav_upload_url']
        file = get_wav_file_bytes_io(audio_key, file_location)
        if file is not None:
            result['feature'] = analysis_features.analysis1(file, wav_test_info['text'], timeout=30,
                                                            rcg_interface='baidu', segments=1)
            result['analysis_end_time'] = datetime.datetime.utcnow()
        else:
            logging.error('pre-test: Finally failed to get audio file from %s after retries.' % file_location)
    except Exception as e:
        tr = traceback.format_exc() + "\naudio:" + audio_key + "\nfile_location:" + file_location
        print(tr)
        logging.error('error happened during process task: %s' % e)
        result["status"] = 'error'
    mongo.save_test_result(test_id, result)
    return result["status"]


def analysis_main(current_id, q_num):
    _start_time = datetime.datetime.utcnow()
    logging.info("current_id: %s, q_num: %s" % (current_id, q_num))
    feature = {}
    score = 0
    tr = None
    file_location = ''
    audio_key = ''

    mongo = db.Mongo()

    user_answer_info = mongo.get_user_answer_info(current_id, q_num)
    # 要使用传入的 q_num 而不使用 current表中的 current_q_num，因为 current_q_num 只是django维护的临时标记，随时会改变。

    q = mongo.get_problem(user_answer_info['q_id'])

    celery_result = 'no exception or been caught'
    try:
        file_location = user_answer_info.get('file_location', 'local')
        audio_key = user_answer_info['wav_upload_url']
        Q_type = q['q_type']
        file = get_wav_file_bytes_io(audio_key, file_location)
        if file is not None:
            if Q_type == 1:
                # 默认用百度识别
                feature = analysis_features.analysis1(file, q['text'], timeout=30, rcg_interface='baidu')
                score = analysis_scores.score1(feature, rcg_interface='baidu')
                # feature = analysis_features.analysis1(file, q['text'], timeout=30, rcg_interface='xunfei')
                # score = analysis_scores.score1(feature,rcg_interface='xunfei')
            elif Q_type in [2, 5, 6, 7]:
                key_weights = q['weights']['key']
                detail_weights = q['weights']['detail']
                feature = analysis_features.analysis2(file, q['wordbase'], timeout=30)
                score = analysis_scores.score2(feature['key_hits'], feature['detail_hits'], key_weights, detail_weights)
            elif Q_type == 3:
                feature = analysis_features.analysis3(file, q['wordbase'], timeout=30)
                score = analysis_scores.score3(feature)
            else:
                logging.error('Invalid question type: %s' % Q_type)
            status = 'finished'
            tr = None
        else:
            logging.error('analysis_main: Finally failed to get audio file from %s after retries.' % file_location)
            status = 'error'

    except Exception as e:
        tr = traceback.format_exc() + "\naudio:" + audio_key + "\nfile_location:" + file_location
        print(tr)
        logging.error('error happened during process task: %s' % e)
        status = 'error'
        celery_result = str(e)

    user_answer_info['analysis_start_time'] = _start_time
    logging.info('Score: %s' % score)
    tries = 1
    while tries <= 3:
        try:
            mongo.save_result(current_id, q_num, user_answer_info, feature, score, status=status, stack=tr)
            break
        except Exception as e:
            logging.exception('Exception(tries:%d/3) saving (%s) result to mongodb: %s' % (tries, current_id, str(e)))
            tries += 1
    return celery_result

# if __name__ == '__main__':
#     status1 = analysis_main("5d6735dd15b52d6910d22c14", "3")
#     print(status1)
