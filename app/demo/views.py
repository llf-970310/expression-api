import json

from flask import request, current_app, jsonify

from app import errors
from app.demo import demo
from app.errors import Internal_error
from client import analysis_client, analysis_thrift


@demo.route('/analysis', methods=['POST'])
def demo():
    resp = analysis_client.analyzeSentence(
        analysis_thrift.AnalyzeSentenceRequest(
            base64Str=request.json["audio"],
            segmentNum=2,
            wordbase={
                "sum-aspects": [
                    "分为几点",
                    "分情况",
                    "看情况",
                    "有几点"
                ],
                "aspects": [
                    "第一",
                    "第1",
                    "第二",
                    "第2",
                    "第三",
                    "第3",
                    "第四",
                    "第4",
                    "首先",
                    "其次",
                    "还有"
                ],
                "example": [
                    "举个例子",
                    "比如",
                    "例如",
                    "比方说",
                    "我的工作",
                    "我的职业"
                ],
                "opinion": [
                    "我同意",
                    "我不同意",
                    "我觉得",
                    "我认为",
                    "我的观点",
                    "应该",
                    "不应该"
                ],
                "sum": [
                    "总之",
                    "最后",
                    "总的来说"
                ],
                "cause-affect": [
                    "因为",
                    "所以",
                    "因此"
                ],
                "transition": [
                    "虽然",
                    "但",
                    "但是"
                ],
                "if": [
                    "假如",
                    "如果"
                ],
                "parallel": [
                    "而且",
                    "也"
                ],
                "progressive": [
                    "不但"
                ]
            }
        )
    )
    if resp is None or resp.statusCode != 0:
        current_app.logger.error("analysis_client.analyzeSentence failed. msg=%s" % resp.statusMsg)
        return jsonify(errors.error(Internal_error))

    feature = json.loads(resp.feature)
    return jsonify(errors.success({"feature": feature}))
