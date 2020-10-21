#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-17

import json
from flask import request, current_app, jsonify
from flask_login import current_user
from app.auth.util import admin_login_required
from app import errors
from app.utils.dto_converter import invitation_code_convert_to_json
from client import user_client, user_thrift
from . import admin


@admin.route('/accounts/invite', methods=['POST'])  # url will be .../admin/accounts/test
@admin_login_required
def accounts_invite():
    """批量创建邀请码

    Form-data Args:
        vipStartTime: 评测权限开始时间（时间戳）
        vipEndTime: 评测权限结束时间（时间戳）
        remainingExamNum: 邀请码包含的评测考试权限
        remainingExerciseNum: 邀请码包含的评测练习权限（暂未使用）
        availableTimes: 邀请码可用人数
        codeNum: 创建邀请码个数

    Returns:
        jsonify(errors.success({'msg': '生成邀请码成功', 'invitationCode': [...]}))

    """
    current_app.logger.info('create invitation request: %s' % request.form.__str__())
    # 检验是否有权限申请邀请码
    form = request.form
    try:
        vip_start_time = form.get('vipStartTime').strip()
        vip_end_time = form.get('vipEndTime').strip()
        remaining_exam_num = int(form.get('remainingExamNum').strip())
        remaining_exercise_num = int(form.get('remainingExerciseNum').strip())
        available_times = int(form.get('availableTimes').strip())
        code_num = int(form.get('codeNum').strip())
    except Exception as e:
        current_app.logger.error('Params_error:POST admin/accounts/invite: %s' % e)
        return jsonify(errors.Params_error)

    resp = user_client.createInvitationCode(user_thrift.CreateInvitationCodeRequest(
        creator=current_user.name,
        availableTimes=available_times,
        vipStartTime=vip_start_time,
        vipEndTime=vip_end_time,
        remainingExamNum=remaining_exam_num,
        remainingExerciseNum=remaining_exercise_num,
        codeNum=code_num,
    ))
    if resp is None:
        current_app.logger.error("[accounts_invite] user_client.createInvitationCode failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success({'msg': '生成邀请码成功', 'invitationCode': resp.codeList}))


@admin.route('/accounts/invite', methods=['GET'])
@admin_login_required
def get_invitations():
    """批量查询邀请码

    Request.args URL Args:
        "currentPage": int,  默认 1
        "pageSize": int,     默认 10
        "conditions": {      可选
            "code": str,
            "createTimeFrom": "2019-11-20 00:00:00",  // utc
            "createTimeTo": "2019-11-22 00:00:00",  // utc
            "availableTimes": int
        }

    Returns:
        {
          "code": xx,
          "msg": xx,
          "data": {
            "totalCount": int,
            "invitationCodes": [
                {}, {}, {}
            ]
          }
        }
    """
    conditions = json.loads(request.args.get('conditions'))
    create_time_from = conditions.get('createTimeFrom')
    create_time_to = conditions.get('createTimeTo')
    available_times = conditions.get('availableTimes')
    specify_code = conditions.get('code')
    cp = int(request.args.get('currentPage', 1))
    ps = int(request.args.get('pageSize', 10))

    resp = user_client.getInvitationCode(user_thrift.GetInvitationCodeRequest(
        invitationCode=specify_code,
        createTimeFrom=create_time_from,
        createTimeTo=create_time_to,
        availableTimes=available_times,
        page=cp,
        pageSize=ps,
    ))
    if resp is None:
        current_app.logger.error("[get_invitations] user_client.getInvitationCode failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    result = []
    for invitation in resp.invitationCodeList:
        result.append(invitation_code_convert_to_json(invitation))

    return jsonify(errors.success({
        'totalCount': resp.total,
        'invitationCodes': result
    }))
