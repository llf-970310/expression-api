from flask import jsonify, current_app
from flask_login import current_user, login_required

from app import errors
from client import question_client, question_thrift
from . import questions


# TODO: 使用redis锁限制每天只能赞一次


@questions.route('/<question_id>/like', methods=['POST'])
@login_required
def new_like(question_id):
    resp = question_client.saveQuestionFeedback(question_thrift.SaveQuestionFeedbackRequest(
        questionId=question_id,
        userId=str(current_user.id),
        likeChange=1
    ))
    if resp is None:
        current_app.logger.error("[new_like] question_client.saveQuestionFeedback failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@questions.route('/<question_id>/like', methods=['DELETE'])
@login_required
def cancel_like(question_id):
    resp = question_client.saveQuestionFeedback(question_thrift.SaveQuestionFeedbackRequest(
        questionId=question_id,
        userId=str(current_user.id),
        likeChange=-1
    ))
    if resp is None:
        current_app.logger.error("[cancel_like] question_client.saveQuestionFeedback failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@questions.route('/<question_id>/up', methods=['POST'])
@login_required
def new_up(question_id):
    resp = question_client.saveQuestionFeedback(question_thrift.SaveQuestionFeedbackRequest(
        questionId=question_id,
        userId=str(current_user.id),
        upChange=1
    ))
    if resp is None:
        current_app.logger.error("[new_up] question_client.saveQuestionFeedback failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@questions.route('/<question_id>/up', methods=['DELETE'])
@login_required
def cancel_up(question_id):
    resp = question_client.saveQuestionFeedback(question_thrift.SaveQuestionFeedbackRequest(
        questionId=question_id,
        userId=str(current_user.id),
        upChange=-1
    ))
    if resp is None:
        current_app.logger.error("[cancel_up] question_client.saveQuestionFeedback failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@questions.route('/<question_id>/down', methods=['POST'])
@login_required
def new_down(question_id):
    resp = question_client.saveQuestionFeedback(question_thrift.SaveQuestionFeedbackRequest(
        questionId=question_id,
        userId=str(current_user.id),
        downChange=1
    ))
    if resp is None:
        current_app.logger.error("[new_down] question_client.saveQuestionFeedback failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@questions.route('/<question_id>/down', methods=['DELETE'])
@login_required
def cancel_down(question_id):
    resp = question_client.saveQuestionFeedback(question_thrift.SaveQuestionFeedbackRequest(
        questionId=question_id,
        userId=str(current_user.id),
        downChange=-1
    ))
    if resp is None:
        current_app.logger.error("[cancel_down] question_client.saveQuestionFeedback failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@questions.route('/<question_id>/up2down', methods=['POST'])
@login_required
def up2down(question_id):
    resp = question_client.saveQuestionFeedback(question_thrift.SaveQuestionFeedbackRequest(
        questionId=question_id,
        userId=str(current_user.id),
        upChange=-1,
        downChange=1
    ))
    if resp is None:
        current_app.logger.error("[up2down] question_client.saveQuestionFeedback failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@questions.route('/<question_id>/down2up', methods=['POST'])
@login_required
def down2up(question_id):
    resp = question_client.saveQuestionFeedback(question_thrift.SaveQuestionFeedbackRequest(
        questionId=question_id,
        userId=str(current_user.id),
        upChange=1,
        downChange=-1
    ))
    if resp is None:
        current_app.logger.error("[down2up] question_client.saveQuestionFeedback failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())
