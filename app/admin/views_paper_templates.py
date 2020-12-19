import json

from flask import current_app, jsonify, request

from app import errors
from app.admin import admin
from app.auth.util import admin_login_required
from client import exam_client, exam_thrift


@admin.route('/all-paper-templates', methods=['GET'])
@admin_login_required
def get_all_paper_templates():
    resp = exam_client.getPaperTemplate(exam_thrift.GetPaperTemplateRequest())
    if resp is None:
        current_app.logger.error("[get_all_paper_templates] exam_client.getPaperTemplate failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    tpl_lst = []
    for item in resp.templateList:
        tpl_lst.append({
            'tpl_id': item.id,
            'name': item.name,
            'is_deprecated': item.isDeprecated,
            "duration": item.duration,
            "questions": json.loads(item.description)
        })
    return jsonify(errors.success({'paperTemplates': tpl_lst}))


@admin.route('/paper-template', methods=['POST'])
@admin_login_required
def save_paper_template():
    template_id = request.form.get('id')
    name = request.form.get('name')
    duration = request.form.get('duration')
    question_list = request.form.get('questions')

    # modify
    if template_id:
        resp = exam_client.savePaperTemplate(exam_thrift.SavePaperTemplateRequest(
            newTemplate=exam_thrift.ExamTemplate(
                id=template_id,
                name=name,
                duration=int(duration),
                description=question_list
            )
        ))
    # add
    else:
        resp = exam_client.savePaperTemplate(exam_thrift.SavePaperTemplateRequest(
            newTemplate=exam_thrift.ExamTemplate(
                id="",
                name=name,
                duration=int(duration),
                description=question_list
            )
        ))

    if resp is None:
        current_app.logger.error("[save_paper_template] exam_client.savePaperTemplate failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@admin.route('/paper-template/enable', methods=['POST'])
@admin_login_required
def enable_paper_template():
    template_id = request.form.get('id')

    resp = exam_client.savePaperTemplate(exam_thrift.SavePaperTemplateRequest(
        newTemplate=exam_thrift.ExamTemplate(
            id=template_id,
            isDeprecated=False,
        )
    ))
    if resp is None:
        current_app.logger.error("[enable_paper_template] exam_client.savePaperTemplate failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())


@admin.route('/paper-template/disable', methods=['POST'])
@admin_login_required
def disable_paper_template():
    template_id = request.form.get('id')

    resp = exam_client.savePaperTemplate(exam_thrift.SavePaperTemplateRequest(
        newTemplate=exam_thrift.ExamTemplate(
            id=template_id,
            isDeprecated=True,
        )
    ))
    if resp is None:
        current_app.logger.error("[disable_paper_template] exam_client.savePaperTemplate failed")
        return jsonify(errors.Internal_error)
    if resp.statusCode != 0:
        return jsonify(errors.error({'code': resp.statusCode, 'msg': resp.statusMsg}))

    return jsonify(errors.success())
