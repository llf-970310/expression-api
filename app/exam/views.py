#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-25

import random
import time

from flask import request, current_app, jsonify
from flask_login import current_user, login_required

from app import errors
from app.admin.admin_config import ScoreConfig
from app.async_tasks.celery_ops import app
from app.models.exam import *
from app.async_tasks import MyCelery
from app.models.user import UserModel
from app.utils.dto_converter import question_info_convert_to_json, exam_score_convert_to_json, \
    exam_report_convert_to_json
from client import exam_client, exam_thrift, user_client, user_thrift
from . import exam
from .exam_config import PathConfig, ExamConfig, DefaultValue, Setting
from .utils.session import ExamSession
from .utils.misc import get_server_date_str

# TODO: 保存put_task接口返回的ret.id到redis，于查询考试结果时查验，减少读库次数
# TODO: 接口改为标准REST风格
# TODO: get-upload-url时后端发放STS凭证供前端访问BOS，避免直接在前端存BOS凭证

"""
正式评测中考试状态的控制：
1. 使用Redis存放，调用ExamSession.set/get/delete控制；
2. 初始化考试时，设置test_id（数据库current.id）和testing（字符串"True"，因Redis不支持bool类型）；
3. 最后一题上传成功后，清空test_id和testing，同时设置last_test_id，供获取结果时使用；
4. 获取结果时使用last_test_id查询，（原有的test_id已被清除）；
5. 再次考试时检查test_id和testing判断有无未完成考试。
"""


@exam.route('/pretest-wav-info', methods=['GET'])
@login_required
def get_test_wav_info():
    resp = exam_client.initNewAudioTest(exam_thrift.InitNewAudioTestRequest(
        userId=str(current_user.id)
    ))
    if resp is None:
        current_app.logger.error("[get_test_wav_info] exam_client.initNewAudioTest failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success({
        "questionLimitTime": resp.question.answerLimitTime,
        "readLimitTime": resp.question.readLimitTime,
        "questionContent": resp.question.content,
        "questionInfo": resp.question.questionTip,
    }))


@exam.route('/pretest-wav-url', methods=['GET'])
@login_required
def get_test_wav_url():
    resp = exam_client.getFileUploadPath(exam_thrift.GetFileUploadPathRequest(
        userId=str(current_user.id),
        type=exam_thrift.ExamType.AudioTest
    ))
    if resp is None:
        current_app.logger.error("[get_test_wav_url] exam_client.getFileUploadPath failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success({
        "fileLocation": "BOS",
        "url": resp.path,
    }))


@exam.route('/pretest-analysis', methods=['POST'])
@login_required
def upload_test_wav_success():
    file_path = request.form.get('filePath')
    std_text = request.form.get('stdText')
    result_id, err = MyCelery.put_task('pretest', std_text=std_text, file_path=file_path)
    ExamSession.set(current_user.id, 'pretest_result_id', result_id, ex=300)
    current_app.logger.info("[upload_test_wav_success] put task into celery successful. "
                            "AsyncResult id: %s, user name: %s" % (result_id, current_user.name))
    return jsonify(errors.success())


@exam.route('/pretest-result', methods=['GET'])
@login_required
def get_pretest_result():
    async_result_id = ExamSession.get(current_user.id, "pretest_result_id", default=None)
    if not async_result_id:
        return jsonify(errors.Internal_error)

    async_result = app.AsyncResult(async_result_id)
    if async_result.ready():
        result = async_result.get()
        if result['status'] != 'error':
            return jsonify(errors.success({
                "qualityIsOk": result['lev_ratio'] >= 0.6,
                "canRcg": True,
                "levRatio": result['lev_ratio']
            }))
        else:
            return jsonify(errors.success({"canRcg": False, "qualityIsOk": False}))
    else:
        return jsonify(errors.WIP)


@exam.route('/<question_num>/upload-url', methods=['GET'])
@login_required
def get_upload_url_v2(question_num):
    test_id = ExamSession.get(current_user.id, "test_id", default=DefaultValue.test_id)  # for production

    resp = exam_client.getFileUploadPath(exam_thrift.GetFileUploadPathRequest(
        examId=test_id,
        userId=str(current_user.id),
        type=exam_thrift.ExamType.RealExam,
        questionNum=int(question_num)
    ))
    if resp is None:
        current_app.logger.error("[get_upload_url_v2] exam_client.getFileUploadPath failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    context = {"fileLocation": "BOS", "url": resp.path}
    return jsonify(errors.success(context))


@exam.route('/<question_num>/upload-success', methods=['POST'])
@login_required
def upload_success_v2(question_num):
    # get test
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error("[TestNotFound][upload_success_v2]test_id: %s" % test_id)
        return jsonify(errors.Exam_not_exist)
    try:
        question = current_test.questions[question_num]
    except Exception as e:
        current_app.logger.error("[GetEmbeddedQuestionException][get_upload_url_v2]question_num: "
                                 "%s, user_name: %s. exception:\n%s"
                                 % (question_num, current_user.name, e))
        return jsonify(errors.Get_question_failed)
    q_type = question['q_type']  # EmbeddedDocument不是dict，没有get方法.  --  已手动支持...

    # todo: 任务队列应放更多信息，让评分节点直接取用，避免让评分节点查url
    task_id, err = MyCelery.put_task(q_type, current_test.id, question_num)
    if err:
        current_app.logger.error('[PutTaskException][upload_success]q_type:%s, test_id:%s,'
                                 'exception:\n%s' % (q_type, current_test.id, err))
        return jsonify(errors.exception({'Exception': str(err)}))
    current_app.logger.info("[PutTaskSuccess][upload_success]dataID: %s" % str(current_test.id))

    # 设置状态为handling
    d = {'set__questions__%s__status' % question_num: 'handling'}
    current_test.update(**d)

    # 最后一题上传完成，去除正在测试状态，设置last_test_id
    if int(question_num) >= len(current_test.questions):
        try:
            ExamSession.delete(current_user.id, 'testing')
            ExamSession.rename(current_user.id, 'test_id', 'last_test_id')
            ExamSession.expire(current_user.id, 'last_test_id', 3600)
        except Exception as e:
            current_app.logger.error('[ExamSessionRenameError]%s' % e)
            return jsonify(errors.exception({'Exception': str(e)}))

    resp = {
        "status": "Success",
        "desc": "添加任务成功，等待服务器处理",
        "dataID": str(current_test.id),
        "taskID": task_id
    }
    return jsonify(errors.success(resp))


# @exam.route('/get-result', methods=['POST'])
@exam.route('/result', methods=['GET'])
@login_required
def get_result():
    last_test_id = ExamSession.get(current_user.id, "last_test_id", DefaultValue.test_id)
    if not last_test_id:
        return jsonify(errors.Check_history_results)

    resp = exam_client.getExamResult(exam_thrift.GetExamResultRequest(
        examId=last_test_id
    ))
    if resp is None:
        current_app.logger.error("[get_result] exam_client.getExamResult failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        # 正在处理
        if resp.statusCode == errors.WIP['code']:
            try_times = int(ExamSession.get(current_user.id, "tryTimes", 0)) + 1
            ExamSession.set(current_user.id, 'tryTimes', str(try_times))
            current_app.logger.info("[get_result] handling!!! try times: %s, test_id: %s, user name: %s" %
                                    (str(try_times), last_test_id, current_user.name))
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success({
        "status": "Success",
        "totalScore": format(resp.score.total, ScoreConfig.DEFAULT_NUM_FORMAT),
        "data": exam_score_convert_to_json(resp.score),  # 这个表示成绩信息，为兼容旧系统就不改了...
        "report": exam_report_convert_to_json(resp.report)
    }))


@exam.route('/paper-templates', methods=['GET'])
@login_required
def get_paper_templates():
    resp = exam_client.getPaperTemplate(exam_thrift.GetPaperTemplateRequest())
    if resp is None:
        current_app.logger.error("[get_paper_templates] exam_client.getPaperTemplate failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    tpl_lst = []
    for item in resp.templateList:
        tpl_lst.append({
            'tpl_id': item.id,
            'name': item.name,
            'desc': item.description,
        })
    return jsonify(errors.success({'paperTemplates': tpl_lst}))


@exam.route('/paper-templates/<paper_tpl_id>/total', methods=['GET'])
@login_required
def get_question_num_of_tpl(paper_tpl_id):
    resp = exam_client.getPaperTemplate(exam_thrift.GetPaperTemplateRequest(
        templateId=paper_tpl_id
    ))
    if resp is None:
        current_app.logger.error("[get_question_num_of_tpl] exam_client.getPaperTemplate failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success({'total': resp.templateList[0].questionCount}))


# init exam
@exam.route('/new/<paper_tpl_id>', methods=['POST'])
@login_required
def init_exam_v2(paper_tpl_id):
    """
    创建试卷
    TODO: 使用redis锁避免短时重复创建(如网络原因导致请求重复到达)
    :param paper_tpl_id: 模板在数据库的 _id
    :return: json格式状态
    """
    # 判断是否有剩余考试次数
    if Setting.LIMIT_EXAM_TIMES:
        resp = user_client.checkExamPermission(user_thrift.CheckExamPermissionRequest(
            userId=str(current_user.id)
        ))
        if resp is None:
            current_app.logger.error("[init_exam_v2] user_client.checkExamPermission failed")
            return jsonify(errors.Internal_error)
        if resp.statusCode != 0:
            return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    # 生成当前题目
    resp = exam_client.initNewExam(exam_thrift.InitNewExamRequest(
        userId=str(current_user.id),
        templateId=paper_tpl_id
    ))
    if resp is None:
        current_app.logger.error("[init_exam_v2] exam_client.initNewExam failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    # todo: change to rpc
    if Setting.LIMIT_EXAM_TIMES:
        current_user.remaining_exam_num -= 1
        current_user.save()

    ExamSession.set(current_user.id, 'test_id', resp.examId)
    ExamSession.set(current_user.id, 'testing', 'True')  # for find-left-exam
    return jsonify(errors.success())


@exam.route('/<question_num>/next-question', methods=['GET'])
@login_required
def next_question_v2(question_num):
    """
    获取下一题
    :param question_num: 完成的题号(原nowQuestionNum),获取第1题时为0
    :return: json格式包装的question，如：
    {
        "code": 0,
        "data": {
            "examLeftTime": 1752.312776,
            "examTime": 1800,
            "lastQuestion": false,
            "questionContent": "表达能力是一种非常有用的技能",
            "questionDbId": "5bcdea7df9438b6e56a32999",
            "questionInfo": {
                "detail": "声音质量测试。点击 “显示题目” 按钮后请先熟悉屏幕上的文字，然后按下 “开始回答” 按钮朗读该段文字。",
                "tip": "为了保证测试准确性，请选择安静环境，并对准麦克风。"
            },
            "questionLimitTime": 60,
            "questionNumber": 1,
            "questionType": 1,
            "readLimitTime": 5
        },
        "msg": "success"
    }
    """
    # 验证参数
    next_question_num = int(question_num) + 1
    if next_question_num <= 0:  # db中题号从1开始
        return jsonify(errors.Params_error)

    # todo: nowQuestionNum: 限制只能获取当前题目
    ExamSession.set(current_user.id, 'question_num', next_question_num)
    test_id = ExamSession.get(current_user.id, "test_id", default=DefaultValue.test_id)  # for production

    resp = exam_client.getQuestionInfo(exam_thrift.GetQuestionInfoRequest(
        examId=test_id,
        questionNum=next_question_num
    ))
    if resp is None:
        current_app.logger.error("[next_question_v2] exam_client.getQuestionInfo failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        if resp.statusCode == errors.Exam_finished["code"]:
            ExamSession.set(current_user.id, 'question_num', 0)
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    if not resp.question:
        return jsonify(errors.Get_question_failed)

    # log question id to user's historical questions  todo: change to rpc
    user = UserModel.objects(id=str(current_user.id)).first()
    user.questions_history.update({resp.question.id: datetime.datetime.utcnow()})
    user.save()

    # 判断考试是否超时，若超时则返回错误
    if resp.question.examLeftTime <= 0:
        return jsonify(errors.Test_time_out)

    return jsonify(errors.success(question_info_convert_to_json(resp.question)))


# @exam.route('/find-left-exam', methods=['POST'])
@exam.route('/left', methods=['GET'])
@login_required
def find_left_exam():
    """
    获取未完成考试,(断网续测),返回题号
    """
    # _time1 = datetime.datetime.utcnow()
    # 判断断电续做功能是否开启
    if ExamConfig.detect_left_exam:
        # 首先判断是否有未做完的考试
        test_id = ExamSession.get(current_user.id, 'test_id')
        is_testing = ExamSession.get(current_user.id, 'testing')
        if test_id is not None and is_testing == 'True':
            # _time2 = datetime.datetime.utcnow()
            left_exam = CurrentTestModel.objects(id=test_id).first()
            # _time3 = datetime.datetime.utcnow()
            # current_app.logger.info('[TimeDebug][find_left_exam query-db]%s' % (_time3 - _time2))
            if left_exam and left_exam['test_expire_time'] > datetime.datetime.utcnow():
                # 查找到第一个未做的题目
                for key, value in left_exam['questions'].items():
                    status = value['status']
                    if status in ['none', 'question_fetched', 'url_fetched']:
                        current_app.logger.info("[LeftExamFound][find_left_exam]user name: %s, test_id: %s" %
                                                (current_user.name, left_exam.id))
                        return jsonify(errors.info("有未完成的考试", {"next_q_num": key}))  # info是什么鬼??
    current_app.logger.debug("[NoLeftExamFound][find_left_exam]user name: %s" % current_user.name)
    # _time4 = datetime.datetime.utcnow()
    # current_app.logger.info('[TimeDebug][find_left_exam total]%s' % (_time4 - _time1))
    return jsonify(errors.success({"info": "没有未完成的考试"}))


# 压测专用
@exam.route('/<question_num>/upload-url-bt', methods=['GET'])
@login_required
def get_upload_url_v2_bt(question_num):
    specified_path = request.args.get('givenUrl')
    test_id = ExamSession.get(current_user.id, "test_id",
                              default=DefaultValue.test_id)  # for production
    # get test
    current_test = CurrentTestModel.objects(id=test_id).first()
    if current_test is None:
        current_app.logger.error(
            "[TestNotFound][get_upload_url_v2]username: %s, test_id: %s" % (current_user.name, test_id))
        return jsonify(errors.Exam_not_exist)

    # get question
    user_id = str(current_user.id)
    current_app.logger.debug("[DEBUG][get_upload_url_v2]question_num: %s, user_name: %s"
                             % (question_num, current_user.name))
    try:
        question = current_test.questions[question_num]
    except Exception as e:
        current_app.logger.error("[GetEmbeddedQuestionException][get_upload_url_v2]question_num: "
                                 "%s, user_name: %s. exception:\n%s"
                                 % (question_num, current_user.name, e))
        return jsonify(errors.Get_question_failed)

    # sts = auth.get_sts_from_redis()  # a to--do

    """generate file path
    upload file path: 相对目录(audio)/日期/用户id/时间戳+后缀(.wav)
    temp path for copy: 相对目录(temp_audio)/用户id/文件名(同上)
    """

    # 如果数据库没有该题的url，创建url，存数据库 ，然后返回
    # 如果数据库里已经有这题的url，说明是重复请求，不用再创建
    if not question.wav_upload_url:
        file_dir = '/'.join((PathConfig.audio_save_basedir, get_server_date_str('-'), user_id))
        _temp_str = "%sr%s" % (int(time.time()), random.randint(100, 1000))
        file_name = "%s%s" % (_temp_str, PathConfig.audio_extension)
        # question.wav_upload_url = file_dir + '/' + file_name
        question.wav_upload_url = specified_path

        # -------- 压测: 使用指定路径进行覆盖,只供压测使用,否则将导致灾难性后果!
        # question.wav_upload_url = request.args.get('givenUrl')
        # -----------------------------------------------------------

        question.file_location = 'BOS'
        question.status = 'url_fetched'
        current_test.save()
        current_app.logger.info("[NewUploadUrl][get_upload_url]user_id:%s, url:%s"
                                % (current_user.id, question.wav_upload_url))
        current_app.logger.info("[INFO][get_upload_url_v2]new url: " + question.wav_upload_url)

    context = {"fileLocation": "BOS", "url": question.wav_upload_url}
    return jsonify(errors.success(context))
