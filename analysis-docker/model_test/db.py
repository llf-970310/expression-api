#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 18-10-19
# Modify by tangdaye
# base on the memory, not the mongodb
import pymongo
from config import MongoConfig
from bson.objectid import ObjectId


class Mongo(object):
    def __init__(self):
        if MongoConfig.auth:
            client = pymongo.MongoClient(host=MongoConfig.host, port=MongoConfig.port, username=MongoConfig.user,
                                         password=MongoConfig.password, authSource=MongoConfig.db,
                                         authMechanism=MongoConfig.auth)  # 创建数据库连接
        else:
            client = pymongo.MongoClient(host=MongoConfig.host, port=MongoConfig.port)  # 创建数据库连接
        mdb = client[MongoConfig.db]  # db
        self.currents = list(mdb[MongoConfig.current].find({}))
        self.questions = list(mdb[MongoConfig.questions].find({}))
        self.api_accounts = list(mdb[MongoConfig.api_accounts].find({}))
        self.users = list(mdb[MongoConfig.users].find({}))
        self.analysis = mdb[MongoConfig.analysis]
        self.history = list(mdb[MongoConfig.history].find({}))

    def get_all_answer(self, type=1):
        temp_score = ['', 'quality', 'key', 'logic']
        result = []
        for t in self.history:
            questions = t.get('questions')
            for k, q in questions.items():
                if 'q_type' in q and 'score' in q and temp_score[type] in q.get('score'):
                    if q.get('q_type') == type and q.get('score').get(temp_score[type]) > 10:
                        result.append(q)

        return result

    def get_user(self, user_id):
        for user in self.users:
            if user.get('_id').__str__() == user_id:
                return {'name': user['name'], 'student_id': user['student_id']}
        return None

    def get_users(self):
        """
        :return: dict like {'_id':'xxx','name':'xxx','student_id':'xxx'}
        """
        users = self.users
        return [{'_id': user['_id'].__str__(), 'name': user['name'], 'student_id': user['student_id']} for user in
                users]

    def get_current(self, user_id):
        """
        :return: dict like {'student_id':'xxx','name':'xxx','score1':'xxx','score2':'xxx'}
        """
        result = None
        for current in self.currents:
            if current.get('user_id').__str__() == user_id:
                result = current
        return result

    def get_currents(self):
        """
        :return: dict like {'student_id':'xxx','name':'xxx','score1':'xxx','score2':'xxx'}
        """
        current = self.currents
        return current

    def get_question_wordbase(self, question_id):
        for question in self.questions:
            if question.get('_id').__str__() == question_id:
                return question.get('wordbase')
        return None

    # {'exam_id': '5bea5322dd626213f79b945c',
    # 'user': {'name': '孟磊', 'student_id': '000001'},
    # 'question_id': '5bea42c81bf6fb56a11a3253',
    # 'features': {'rcg_text': '高铁是现在最受欢迎的出行方式，他有三个优点，首先他速度快，提示他准点率高，最后他。我说是让他填好田地的投入非常多，对工艺和管理人员都有很高的要求，速度快的话能从。到贵阳以前用40个小时，现在只有60个小时，座椅非常的宽敞，而且很舒适，还有WiFi。', 'num': 111, 'last_time': 30.000125, 'interval_num': 0, 'interval_ratio': 0.0, 'n_ratio': 0.14285714285714285, 'v_ratio': 0.16883116883116883, 'vd_ratio': 0.0, 'vn_ratio': 0.025974025974025976, 'a_ratio': 0.1038961038961039, 'ad_ratio': 0.012987012987012988, 'an_ratio': 0.0, 'd_ratio': 0.07792207792207792, 'm_ratio': 0.012987012987012988, 'q_ratio': 0.0, 'r_ratio': 0.07792207792207792, 'p_ratio': 0.03896103896103896, 'c_ratio': 0.025974025974025976, 'u_ratio': 0.06493506493506493, 'xc_ratio': 0.0, 'w_ratio': 0.16883116883116883, 'ne_ratio': 0.06493506493506493, 'word_num': 77, 'noun_frequency_2': 1, 'noun_frequency_3': 0, 'noun_frequency_4': 0, 'keywords_num': [4, 4], 'keywords': ['高铁', '方式', '出行', '受欢迎'], 'mainwords_num': [3, 4], 'mainwords': ['速度', '舒适', '准点', ''], 'detailwords_nums': [[3, 3], [1, 3]], 'detailwords': [['40', '起飞', '电路'], ['', '', '管理']], 'keywords_num_main': [4, 4], 'speeds': 0, 'volumes': [2847.7988832167734, 2606.5623195149656, 2276.6604212572024], 'sentence_num': 14},
    # 'score_main': 94.0, 'score_detail': 80.0}
    def update_or_save_analysis(self, analysis_result):
        self.analysis.update_one({'exam_id': analysis_result.get('exam_id'),
                                  'question_id': analysis_result.get('question_id')},
                                 {'$set': {'features': analysis_result.get('features'),
                                           'score_main': analysis_result.get('score_main'),
                                           'score_detail': analysis_result.get('score_detail')}},
                                 True)

        pass


def clean_current():
    m = Mongo()
    # m.currents.remove({"current_q_num":2})
    # print(m.currents.count())
    # x = list(m.currents.find({}))
    # for current in x:
    #     if m.users.find({"_id":ObjectId(current.get("user_id"))}).count()>0:
    #         # pass
    #         # print("yes")
    #     else:
    #         print("no")


if __name__ == '__main__':
    pass
    # clean_current()
    # mongo = Mongo()
    # x = {'exam_id': '5bea5322dd626213f79b945c', 'user': {'name': '孟磊', 'student_id': '000001'},
    #      'question_id': '5bea42c81bf6fb56a11a3253', 'features': {
    #         'rcg_text': '高铁是现在最受欢迎的出行方式，他有三个优点，首先他速度快，提示他准点率高，最后他。我说是让他填好田地的投入非常多，对工艺和管理人员都有很高的要求，速度快的话能从。到贵阳以前用40个小时，现在只有60个小时，座椅非常的宽敞，而且很舒适，还有WiFi。',
    #         'num': 111, 'last_time': 30.000125, 'interval_num': 0, 'interval_ratio': 0.0,
    #         'n_ratio': 0.14285714285714285, 'v_ratio': 0.16883116883116883, 'vd_ratio': 0.0,
    #         'vn_ratio': 0.025974025974025976, 'a_ratio': 0.1038961038961039, 'ad_ratio': 0.012987012987012988,
    #         'an_ratio': 0.0, 'd_ratio': 0.07792207792207792, 'm_ratio': 0.012987012987012988, 'q_ratio': 0.0,
    #         'r_ratio': 0.07792207792207792, 'p_ratio': 0.03896103896103896, 'c_ratio': 0.025974025974025976,
    #         'u_ratio': 0.06493506493506493, 'xc_ratio': 0.0, 'w_ratio': 0.16883116883116883,
    #         'ne_ratio': 0.06493506493506493, 'word_num': 77, 'noun_frequency_2': 1, 'noun_frequency_3': 0,
    #         'noun_frequency_4': 0, 'keywords_num': [4, 4], 'keywords': ['高铁', '方式', '出行', '受欢迎'],
    #         'mainwords_num': [3, 4], 'mainwords': ['速度', '舒适', '准点', ''], 'detailwords_nums': [[3, 3], [1, 3]],
    #         'detailwords': [['40', '起飞', '电路'], ['', '', '管理']], 'keywords_num_main': [4, 4], 'speeds': 0,
    #         'volumes': [2847.7988832167734, 2606.5623195149656, 2276.6604212572024], 'sentence_num': 14},
    #      'score_main': 94.0, 'score_detail': 80.0}
    # mongo.update_or_save_analysis(x)
    # print(mongo.get_question_wordbase('5bea42c81bf6fb56a11a3253'))
    # pass
    # current_id = "5bcde8f30b9e037b1f67ba4e"
    # q_num = "2"
    #
    # db = Mongo()
    # q_info = db.get_question_info(current_id, q_num)
    # wf, q = db.get_wave_path_and_question(q_info)
    # feature = {}
    # score = {"main": 60, "detail": 80}
    # db.save_result(current_id, q_num, q_info, feature, score)

    # m = Mongo()
    # students = m.get_users()
    # result = []
    # for student in students:
    #     if student['student_id'][:3] == 'NJU' or student['student_id'][0] == 'M' or student['student_id'][0] == 'm':
    #         current = m.get_current(user_id=student['_id'])
    #         if current:
    #             questions = current['questions']
    #             questions_result = []
    #             for key, question in questions.items():
    #                 questions_result.append(question.get('feature').get('last_time'))
    #
    #             result.append({'student_id': student['student_id'],
    #                            'name': student['name'],
    #                            'result': questions_result})
    #         else:
    #             result.append({'student_id': student['student_id'],
    #                            'name': student['name'],
    #                            'result': '没有答题记录'})
    # with open('../测试情况12-03.json', 'w') as f:
    #     f.write(json.dumps(result, ensure_ascii=False))
    # normal, abnormal = [], []
    # for item in result:
    #     if item.get('result') == '没有答题记录':
    #         abnormal.append(item.get('name'))
    #         continue
    #     result = item.get('result')
    #     if result[0] and result[1] and result[2] and result[3] and result[4] and result[5]:
    #         normal.append(item.get('name'))
    #     else:
    #         abnormal.append(item.get('name'))
    # normal = set(normal)
    # should_delete = []
    # for item in abnormal:
    #     if item in normal:
    #         should_delete.append(item)
    # for item in should_delete:
    #     abnormal.remove(item)
    # abnormal = set(abnormal)
    # print(normal)
    # print(abnormal)

    # print(m.get_evl_account())
    # print(m.get_rcg_account())
    # print(m.get_baidu_account())
