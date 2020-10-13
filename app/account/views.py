#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

# 该文件存放面向用户的accounts相关views,与view无关的具体功能的实现请写在utils.py中,在此尽量只作引用

from flask import request, current_app, jsonify
from flask_login import current_user, login_required

from app import errors
from app.exam.manager.exam import get_exam_by_id, get_score_and_feature
from app.exam.manager.report import generate_report
from client import exam_client, exam_thrift
from . import account

from app.models.exam import HistoryTestModel, CurrentTestModel
from app.admin.admin_config import ScoreConfig
from app.utils.date_and_time import datetime_to_str
from app.paper import compute_exam_score
from app.models.invitation import InvitationModel


@account.route('/update', methods=['POST'])
@login_required
def update():
    password = request.form.get('password')
    name = request.form.get('name').strip()
    if len(name) > 20:
        return jsonify(errors.Params_error)
    if not password:
        current_user.name = name
    elif password.strip() == "":
        return jsonify(errors.Params_error)
    else:
        current_user.set_password(password)
        current_user.name = name
    current_user.save()
    return jsonify(errors.success({
        'msg': '修改成功',
        'uuid': str(current_user.id),
        'name': str(current_user.name),
        'password': '********'
    }))


@account.route('/update-privilege/<code>', methods=['POST'])
@login_required
def update_privilege(code):
    # todo 从这开始需要同步
    existing_invitation = InvitationModel.objects(code=code).first()
    if existing_invitation is None or existing_invitation.available_times <= 0:
        return jsonify(errors.Illegal_invitation_code)
    # 修改这个邀请码
    existing_invitation.activate_users.append(current_user.email if current_user.email else current_user.phone)
    if existing_invitation.available_times <= 0:
        return jsonify(errors.Invitation_code_invalid)
    existing_invitation.available_times -= 1
    current_app.logger.debug('invitation info: %s' % existing_invitation.__str__())
    existing_invitation.save()
    # todo 同步结束
    current_app.logger.info('[UpdatePrivilege][update_privilege]email:%s, phone:%s' %
                            (current_user.email, current_user.phone))
    current_user.vip_start_time = existing_invitation.vip_start_time
    current_user.vip_end_time = existing_invitation.vip_end_time
    current_user.remaining_exam_num = existing_invitation.remaining_exam_num
    # 这里需要添加一个邀请码信息
    current_user.invitation_code = existing_invitation.code
    current_app.logger.info('[UserInfo][update_privilege]%s' % current_user.__str__())
    current_user.save()
    current_app.logger.debug('user(id = %s) has been saved' % current_user.id)
    return jsonify(errors.success())


@account.route('/unbind-wx', methods=['POST'])
@login_required
def unbind_wx():
    if not current_user.wx_id:
        return jsonify(errors.Wechat_not_bind)
    current_user.update(set__wx_id='')
    return jsonify(errors.success(
        {
            'msg': '解绑成功'
        }
    ))


@account.route('/info', methods=['GET'])
@login_required
def get_info():
    current_app.logger.debug('[GetAccountInfo][get_info]%s' % current_user)
    return jsonify(errors.success({
        'role': str(current_user.role.value),
        'name': current_user.name,
        'email': current_user.email if current_user.email is not None else current_user.phone,
        'password': '********',
        'register_time': datetime_to_str(current_user.register_time),
        'last_login_time': datetime_to_str(current_user.last_login_time),
        # 'questions_history': current_user.questions_history,
        'wx_id': current_user.wx_id,
        'vip_start_time': datetime_to_str(current_user.vip_start_time),
        'vip_end_time': datetime_to_str(current_user.vip_end_time),
        'remaining_exam_num': current_user.remaining_exam_num
    }))


@account.route('/history-scores/<tpl_id>', methods=['GET'])
@account.route('/history-scores', methods=['GET'])
@login_required
def get_history_scores(tpl_id="0"):
    resp = exam_client.getExamRecord(exam_thrift.GetExamRecordRequest(
        userId=str(current_user.id),
        templateId=tpl_id if tpl_id != "0" else ""
    ))
    if resp is None:
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    history_scores = []
    for exam_item in resp.examList:
        history_scores.append({
            "test_start_time": exam_item.examStartTime,
            "paper_tpl_id": exam_item.templateId,
            "test_id": exam_item.examId,
            "score_info": exam_score_convert_to_json(exam_item.scoreInfo)
        })

    if len(history_scores) == 0:
        return jsonify(errors.No_history)
    return jsonify(errors.success({"history": history_scores}))


@account.route('/history-report/<test_id>', methods=['GET'])
@login_required
def get_history_report(test_id):
    resp = exam_client.getExamReport(exam_thrift.GetExamReportRequest(examId=test_id))
    if resp is None:
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    report = resp.report
    score = resp.score
    result = {
        "report": {
            "主旨": report.key, "细节": report.detail, "结构": report.structure,
            "逻辑": report.logic, "音质": {
                "无效表达率": report.ftlRatio,
                "清晰度": report.clearRatio,
                "语速": report.speed,
                "间隔": report.interval
            }
        },
        "data": exam_score_convert_to_json(score)
    }
    return jsonify(errors.success(result))


def exam_score_convert_to_json(score) -> dict:
    return {
        "total": format(score.total, ScoreConfig.DEFAULT_NUM_FORMAT),
        "主旨": format(score.key, ScoreConfig.DEFAULT_NUM_FORMAT),
        "细节": format(score.detail, ScoreConfig.DEFAULT_NUM_FORMAT),
        "结构": format(score.structure, ScoreConfig.DEFAULT_NUM_FORMAT),
        "逻辑": format(score.logic, ScoreConfig.DEFAULT_NUM_FORMAT),
        "音质": format(score.quality, ScoreConfig.DEFAULT_NUM_FORMAT)
    }
