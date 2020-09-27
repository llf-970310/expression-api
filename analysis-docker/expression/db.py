#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 18-10-19

import datetime
import logging
import pymongo
from config import MongoConfig
from bson.objectid import ObjectId
import json


class Mongo(object):
    def __init__(self):
        if MongoConfig.auth:
            client = pymongo.MongoClient(host=MongoConfig.host, port=MongoConfig.port, username=MongoConfig.user,
                                         password=MongoConfig.password, authSource=MongoConfig.db,
                                         authMechanism=MongoConfig.auth)  # 创建数据库连接
        else:
            client = pymongo.MongoClient(host=MongoConfig.host, port=MongoConfig.port)  # 创建数据库连接
        mdb = client[MongoConfig.db]  # db
        self.current = mdb[MongoConfig.current]  # collection
        self.questions = mdb[MongoConfig.questions]
        self.api_accounts = mdb[MongoConfig.api_accounts]
        self.users = mdb[MongoConfig.users]
        self.current = mdb[MongoConfig.current]
        self.wav_test = mdb[MongoConfig.wav_test]

    def get_wav_test_info(self, test_id):
        return self.wav_test.find_one({"_id": ObjectId(test_id)})

    def get_user_answer_info(self, current_id, q_num):
        return self.current.find_one({"_id": ObjectId(current_id)})['questions'][q_num]

    def get_problem(self, problem_id):
        """ 获取： 要分析问题的原题 """
        q = self.questions.find_one({"_id": ObjectId(problem_id)})
        logging.debug('question: %s' % q)
        return q

    def save_result(self, current_id, q_num, question_info, feature=None, score=None, status='finished', stack=None):
        """ 根据给定的current_id和q_num，
        设置当前题目status为finished，保存分析结果feature{}，保存该题score，保存分析结束时间analysis_end_time
        若当前题目处理出错，保存堆栈信息
        """
        if status == 'finished':
            question_info['feature'] = feature
            question_info['score'] = score
        else:
            question_info['stack'] = stack
        question_info['status'] = status
        question_info['analysis_end_time'] = datetime.datetime.utcnow()
        self.current.update_one({'_id': ObjectId(current_id)}, {'$set': {'questions.%s' % q_num: dict(question_info)}},
                                True)  # 参数分别是：条件，更新内容，不存在时是否插入

    def save_test_result(self, test_id, result):
        """ 
        保存音频测试的结果
        """
        print('id: %s' % test_id)
        print('result %s' % str(result))
        self.wav_test.update_one({'_id': ObjectId(test_id)}, {'$set': {'result': dict(result)}}, True)

    # def test_insert_data(self):
    #     with open('/tmp/current.json', 'r') as f:
    #         data = json.loads(f.read())
    #     self.current.insert_one(data)

    # def test_find(self):
    #     current_item = self.current.find_one({"_id": ObjectId("5bcdc98e0b9e0365ce135a68")})  # format right! found!
    #     current_item = self.current.find_one({"_id": "5bcdc98e0b9e0365ce135a68"})  # format wrong! not found!
    #     logging.info(current_item)

    def get_evl_account(self):
        """
        :return: dict like {'appid': 'xxx', 'key': 'xxx', 'used_times': 6}
        """
        evl_accounts = self.api_accounts.find_one({"type": "xf_evl"})
        all_accounts = evl_accounts['accounts']
        all_accounts = sorted(all_accounts, key=lambda a: a['used_times'], reverse=False)
        all_accounts[0]['used_times'] += 1
        self.api_accounts.update_one({'_id': evl_accounts['_id']}, {'$set': {'accounts': list(all_accounts)}}, False)
        return all_accounts[0]

    def get_rcg_account(self):
        """
        :return: dict like {'appid': 'xxx', 'key': 'xxx', 'used_times': 6}
        """
        rcg_accounts = self.api_accounts.find_one({"type": "xf_rcg"})
        all_accounts = rcg_accounts['accounts']
        all_accounts = sorted(all_accounts, key=lambda a: a['used_times'], reverse=False)
        all_accounts[0]['used_times'] += 1
        self.api_accounts.update_one({'_id': rcg_accounts['_id']}, {'$set': {'accounts': list(all_accounts)}}, False)
        return all_accounts[0]

    def get_baidu_account(self):
        """
        :return: dict like {'appid': 'xxx', 'api_key': 'xxx', 'secret_key': 'xxx', 'used_times': 6}
        """
        baidu_accounts = self.api_accounts.find_one({"type": "baidu"})
        all_accounts = baidu_accounts['accounts']
        all_accounts = sorted(all_accounts, key=lambda a: a['used_times'], reverse=False)
        all_accounts[0]['used_times'] += 1
        self.api_accounts.update_one({'_id': baidu_accounts['_id']}, {'$set': {'accounts': list(all_accounts)}}, False)
        return all_accounts[0]

    def get_users(self):
        """
        :return: dict like {'_id':'xxx','name':'xxx','student_id':'xxx'}
        """
        users = self.users.find({})
        return [{'_id': user['_id'].__str__(), 'name': user['name'], 'student_id': user['student_id']} for user in
                users]

    def get_current(self, user_id):
        """
        :return: dict like {'student_id':'xxx','name':'xxx','score1':'xxx','score2':'xxx'}
        """
        current = self.current.find({'user_id': user_id})
        if current.count() == 0:
            return None
        return list(current)[-1]


if __name__ == '__main__':
    # current_id = "5bcde8f30b9e037b1f67ba4e"
    # q_num = "2"
    #
    # db = Mongo()
    # q_info = db.get_question_info(current_id, q_num)
    # wf, q = db.get_wave_path_and_question(q_info)
    # feature = {}
    # score = {"main": 60, "detail": 80}
    # db.save_result(current_id, q_num, q_info, feature, score)

    m = Mongo()
    students = m.get_users()
    result = []
    for student in students:
        if student['student_id'][:3] == 'NJU' or student['student_id'][0] == 'M' or student['student_id'][0] == 'm':
            current = m.get_current(user_id=student['_id'])
            if current:
                questions = current['questions']
                questions_result = []
                for key, question in questions.items():
                    questions_result.append(question.get('feature').get('last_time'))

                result.append({'student_id': student['student_id'],
                               'name': student['name'],
                               'result': questions_result})
            else:
                result.append({'student_id': student['student_id'],
                               'name': student['name'],
                               'result': '没有答题记录'})
    with open('../测试情况12-03.json', 'w') as f:
        f.write(json.dumps(result, ensure_ascii=False))
    normal, abnormal = [], []
    for item in result:
        if item.get('result') == '没有答题记录':
            abnormal.append(item.get('name'))
            continue
        result = item.get('result')
        if result[0] and result[1] and result[2] and result[3] and result[4] and result[5]:
            normal.append(item.get('name'))
        else:
            abnormal.append(item.get('name'))
    normal = set(normal)
    should_delete = []
    for item in abnormal:
        if item in normal:
            should_delete.append(item)
    for item in should_delete:
        abnormal.remove(item)
    abnormal = set(abnormal)
    print(normal)
    print(abnormal)

    # print(m.get_evl_account())
    # print(m.get_rcg_account())
    # print(m.get_baidu_account())
