#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

from flask import request, current_app, jsonify
from flask_login import current_user, login_required

from app import errors
from app.utils.dto_converter import exam_score_convert_to_json, exam_report_convert_to_json, user_info_convert_to_json
from client import exam_client, exam_thrift, user_thrift, user_client
from . import account


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
    resp = user_client.updateUserInfo(user_thrift.UpdateUserInfoRequest(
        userId=str(current_user.id),
        invitationCode=code
    ))
    if resp is None:
        current_app.logger.error("[update_privilege] user_client.updateUserInfo failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

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
    resp = user_client.getUserInfo(user_thrift.GetUserInfoRequest(
        userId=str(current_user.id)
    ))
    if resp is None:
        current_app.logger.error("[get_info] user_client.getUserInfo failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success(user_info_convert_to_json(resp.userInfo)))


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
        "report": exam_report_convert_to_json(report),
        "data": exam_score_convert_to_json(score)
    }
    return jsonify(errors.success(result))
