#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-24

import datetime

import jwt
from flask import current_app, jsonify, request, session
from flask_login import login_user, logout_user, current_user, login_required

from app import errors
from app.auth.util import wx_get_user_info, validate_email, validate_phone
from app.models.invitation import InvitationModel
from app.models.user import UserModel
from client import exam_thrift, exam_client, user_client, user_thrift
from . import auth


# from app.account.views import get_info as get_account_info


@auth.route('/register', methods=['POST'])
def register():
    current_app.logger.info('register request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    if not current_app.config.get('ALLOW_REGISTER'):
        return jsonify(errors.Register_not_allowed)

    username = request.form.get('username').strip().lower()
    password = request.form.get('password').strip()
    name = request.form.get('name').strip()
    code = request.form.get('code').strip()
    """
        校验form，规则
        1. email符合规范
        2. 各项不为空
    """
    if not (username and password and name):
        return jsonify(errors.Params_error)
    if current_app.config.get('NEED_INVITATION') and not code:
        return jsonify(errors.Params_error)

    invitation_code = None
    if current_app.config.get('NEED_INVITATION'):
        invitation_code = code

    resp = user_client.createUser(user_thrift.CreateUserRequest(
        username=username,
        password=password,
        name=name,
        invitationCode=invitation_code
    ))
    if resp is None:
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success({
        'msg': '注册成功',
        'username': username,
        'nickname': name
    }))


@auth.route('/login', methods=['POST'])
def login():
    authorization = request.headers.get("Authorization", None)
    token = ""
    is_login = False

    # already login
    if authorization:
        try:
            token = authorization.split(' ')[1]
            payload = jwt.decode(token, "secret", algorithms="HS256")
            if payload:
                current_app.logger.info("re-login")
                is_login = True
                # current_app.logger.info('re-login user: %s, id: %s' % (check_user.name, check_user.id))
        except Exception as e:
            current_app.logger.error(e)

    if not is_login:
        username = request.form.get('username')
        password = request.form.get('password')
        if not (username and password):
            return jsonify(errors.Params_error)

        resp = user_client.authenticate(user_thrift.AuthenticateRequest(
            username=username,
            password=password
        ))
        if resp is None:
            return jsonify(errors.Internal_error)
        if resp.statusCode != 0:
            return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

        token = resp.token

    payload = jwt.decode(token, "secret", algorithms="HS256")
    return jsonify(errors.success({
        'msg': '登录成功',
        "token": token,
        # 'uuid': payload["uuid"],
        'name': payload["nick_name"],
        'role': payload["role"]
    }))


@auth.route('/logout', methods=['POST'])
def logout():
    _time1 = datetime.datetime.utcnow()
    # current_app.logger.debug('logout request: %s' % request.form.__str__())
    if current_user.is_authenticated:
        current_app.logger.info('user(id:%s) logout' % current_user.id)
        logout_user()
    _time2 = datetime.datetime.utcnow()
    current_app.logger.info('[TimeDebug][logout total]%s' % (_time2 - _time1))
    return jsonify(errors.success())


@auth.route('/wechat-login')  # callback预留接口，已在微信开放平台登记
def wechat_callback():
    return ''


# web 端微信扫码登录
@auth.route('/wechat/login', methods=['POST'])
def wechat_login():
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)
    code = request.form.get('code')
    if not code:
        return jsonify(errors.Params_error)
    err_code, user_info = wx_get_user_info(code, current_app.config['WX_APPID'], current_app.config['WX_SECRET'])
    if err_code:
        return jsonify(errors.error({'code': int(err_code), 'msg': 'invalid wechat code'}))
    wx_union_id = user_info.get('unionid')
    check_user = UserModel.objects(wx_id=wx_union_id).first()
    if not check_user:
        session['wx_union_id'] = wx_union_id
        # data = {'msg': '用户尚未绑定微信，前端请指引用户补充填写信息，进行绑定'}
        # data.update({'userInfo': user_info})
        # return jsonify(errors.error(data))
        headimgurl = user_info.get('headimgurl')
        nickname = user_info.get('nickname').encode('ISO-8859-1').decode('utf-8')  # 要转码
        return jsonify(errors.success({
            'msg': '未绑定用户',
            'headimgurl': headimgurl,
            'nickname': nickname,
        }))
    session['wx_nickname'] = user_info.get('nickname')
    login_user(check_user)
    check_user.last_login_time = datetime.datetime.utcnow()
    check_user.save()
    current_app.logger.info('login from wechat: %s, id: %s' % (check_user.name, check_user.id))
    return jsonify(errors.success({
        'msg': '已绑定用户，自动登录',
        'uuid': str(check_user.id),
        'name': str(check_user.name),
    }))


"""
微信登录返回示例
oauth2 ret:
{"access_token":"19_IJE6MpX1MyK9VVXQlppGJk762p_n80ePdS0oWHVhyx7vCUwdWWkolumWFnaYOp3QBlJD5k9x-vNaejZAoSlsZg",
 "expires_in":7200,
 "refresh_token":"19_IlD6dnGYZKUchv-G92SZvxkqRjAs_JdLuow2FTduYc9wVtO6esEb_LzkbQBdmApuKnuAEY-1V8zUkETeZxWxeg",
 "openid":"oSeg251hPU-NlMesh7KrT7Izp-Bc",
 "scope":"snsapi_login",
 "unionid":"om7mj00CPmlmh27SaLSFu3Nd_RQA"}
user_info: 
{'openid': 'oSeg251hPU-NlMesh7KrT7Izp-Bc',
 'nickname': 'BetweenAugust&December', 'sex': 1, 'language': 'zh_CN',
 'city': 'Nanjing', 'province': 'Jiangsu', 'country': 'CN',
 'headimgurl': 'http://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTLST3pS1ya049yK1vpfF7O8NV96S2GKrrvopiaRR5DQvuK9G4Jmk6iceDjTcYwF62yx1H9vKSI89qxg/132',
 'privilege': [], 'unionid': 'om7mj00CPmlmh27SaLSFu3Nd_RQA'}
"""


@auth.route('/wechat/bind', methods=['POST'])
def wechat_bind():
    """
    前端展示用户的微信头像和名称，引导用户填写账号和密码进行绑定，将来可能直接绑定手机号
    :return:
    """
    wx_union_id = session.get('wx_union_id')
    if not wx_union_id:
        return jsonify(errors.error())
    username = request.form.get('username')
    password = request.form.get('password')

    resp = user_client.authenticate(user_thrift.AuthenticateRequest(
        username=username,
        password=password
    ))
    if resp is None:
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    token = resp.token
    payload = jwt.decode(token, "secret", algorithms="HS256")
    check_user = UserModel.objects(pk=payload["uuid"]).first()

    if check_user.wx_id:
        return jsonify(errors.Wechat_already_bind)

    current_app.logger.info('Bind wechat union id -\n  user: %s, union id: %s' % (check_user.email, wx_union_id))
    check_user.wx_id = wx_union_id
    check_user.last_login_time = datetime.datetime.utcnow()
    check_user.save()

    return jsonify(errors.success({
        'msg': '绑定成功',
        'token': token,
        'name': payload["nick_name"],
    }))


# 微信小程序登录
@auth.route('/wxapp/login', methods=['POST'])
def wxapp_login():
    if current_user.is_authenticated:
        return jsonify(errors.Already_logged_in)

    code = request.form.get('code')
    nick_name = request.form.get('nick_name')
    if not code:
        return jsonify(errors.Params_error)

    resp = user_client.authenticateWechatUser(user_thrift.AuthenticateWechatUserRequest(
        code=code,
        nickName=nick_name
    ))
    if resp is None:
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    token = resp.token
    payload = jwt.decode(token, "secret", algorithms="HS256")

    return jsonify(errors.success({
        'msg': '登录成功',
        "token": token,
        'name': payload["nick_name"],
    }))
