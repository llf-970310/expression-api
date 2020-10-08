import json

from flask import current_app

from app.models.exam import *
from app.models.analysis import *
from app.exam.exam_config import ExamConfig
from client import analysis_thrift, analysis_client


class Analysis(object):

    def re_analysis(self, analysis_question):
        """对指定题目重新分析
        :param analysis_question: 要被分析的 question
        """
        print("analysis out", analysis_question['index'])
        total_key, total_detail, count = 0, 0, 0
        # 首先，将analysis表里所有这道题的答案都重新分析一遍
        old_analysis_list = AnalysisModel.objects(question_num=analysis_question['index'])
        for analysis in old_analysis_list:
            Analysis.compute_score_and_save(analysis, analysis['voice_features'], analysis_question,
                                            analysis['test_start_time'])
            total_key = analysis['score_key']
            total_detail = analysis['score_detail']
            count += 1

        # 然后，将current中未被分析的部分分析一遍
        histories = HistoryTestModel.objects(all_analysed=False)
        print(len(histories))
        for test in histories:
            questions = test['questions']
            all_analysed = True
            for question in questions.values():
                if question['q_id'] == analysis_question['id'].__str__() and question['status'] == 'finished' and \
                        not question['analysed']:
                    analysis = Analysis.init_analysis_item(analysis_question, question, test)
                    analysis = Analysis.compute_score_and_save(analysis, analysis['voice_features'], analysis_question,
                                                               test['test_start_time'])
                    if analysis is None:
                        continue
                    question['analysed'] = True
                    total_key = analysis['score_key']
                    total_detail = analysis['score_detail']
                    count += 1
                all_analysed = all_analysed and question['analysed']
            test['all_analysed'] = all_analysed
            test.save()

        # 更新难度
        if count != 0:
            mean = (total_key * ExamConfig.key_percent + total_detail * ExamConfig.detail_percent) / count
            difficulty = mean / ExamConfig.full_score
            analysis_question['level'] = round(10 - difficulty * 10)
            analysis_question.save()
        pass

    @staticmethod
    def init_analysis():
        """根据 current.questions 中的第二类问题初始化 analysis 表
        """
        # for question in QuestionModel.objects(q_type=2).order_by('q_id'):
        #     init_process(question)
        pass

    @staticmethod
    def init_analysis_item(analysis_question, question, test):
        """根据相关类（题目、测试）初始化一条 analysis 记录
        :param analysis_question: 要被分析的 question（对应 question 表）
        :param question: 一次测试中的某道题目的作答记录（对应 current/history 表中的 questions）
        :param test: 测试（对应 current/history 表）
        """
        print("analysis inner", analysis_question['index'], test['test_start_time'])
        analysis = AnalysisModel()
        analysis['exam_id'] = test['id'].__str__()
        analysis['user'] = test['user_id']
        analysis['question_id'] = question['q_id'].__str__()
        analysis['question_num'] = analysis_question['index']
        voice_features = {
            'rcg_text': question['feature']['rcg_text'],
            'last_time': question['feature']['last_time'],
            'interval_num': question['feature']['interval_num'],
            'interval_ratio': question['feature']['interval_ratio'],
            'volumes': question['feature']['volumes'],
            'speeds': question['feature']['speeds'],
        }
        analysis['voice_features'] = voice_features
        return analysis

    @staticmethod
    def init_process(analysis_question):
        """对指定问题进行 analysis 表的初始化工作

        :param analysis_question: 要被分析的 question
        """
        # 然后，将current中未被分析的部分分析一遍
        print('-----------------------')
        print('start to analyse question ', analysis_question['q_id'])
        histories = HistoryTestModel.objects()
        print(len(histories))
        for test in histories:
            questions = test['questions']
            all_analysed = True
            for question in questions.values():
                if question['q_id'] == analysis_question['id'].__str__() and question['status'] == 'finished':
                    analysis = Analysis.init_analysis_item(analysis_question, question, test)
                    Analysis.compute_score_and_save(analysis, analysis['voice_features'], analysis_question,
                                                    test['test_start_time'])
                    question['analysed'] = True
                all_analysed = all_analysed and question['analysed']
            test['all_analysed'] = all_analysed
            test.save()
        pass

    @staticmethod
    def compute_score_and_save(analysis, voice_features, question, test_start_time):
        try:
            resp = analysis_client.analyzeRetellingQuestion(
                analysis_thrift.AnalyzeRetellingQuestionRequest(
                    voiceFeatures=json.dumps(voice_features),
                    keywords=question['wordbase']['keywords'],
                    detailwords=question['wordbase']['detailwords'],
                    keyWeights=question['weights']['key'],
                    detailWeights=question['weights']['detail']
                )
            )
            if resp is None or resp.statusCode != 0:
                current_app.logger.error("[compute_score_and_save] "
                                         "analysis_client.analyzeRetellingQuestion failed. msg=%s" % resp.statusMsg)
                return None
            else:
                feature = json.loads(resp.feature)
                analysis['score_key'] = resp.keyScore
                analysis['score_detail'] = resp.detailScore
                analysis['key_hits'] = feature['key_hits']
                analysis['detail_hits'] = feature['detail_hits']
                analysis['test_start_time'] = test_start_time
                analysis.save()
                return analysis
        except Exception as e:
            current_app.logger.error("[compute_score_and_save] exception caught. exam_id: %s, question_id: %s" % (
                analysis['exam_id'], analysis['question_id']))
            current_app.logger.error(repr(e))

# if __name__ == '__main__':
#     print(sys.path)
#     print(analysis_util)
#     analysis = Analysis()
#     analysis.init_analysis()
