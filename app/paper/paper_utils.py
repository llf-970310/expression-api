#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 2020-05-10

from app.exam.exam_config import ExamConfig, QuestionConfig, DefaultValue
from flask import current_app

from app.models.cached.questions import get_cached_questions
from app.models.exam import *
from app.models.question import QuestionModel
from app.models.user import UserModel
from app.models.paper_template import PaperTemplate


class PaperUtils:
    @staticmethod
    def get_templates():
        all_templates = PaperTemplate.objects(deprecated=False)  # TODO: cache in redis
        tpl_lst = []
        for tpl in all_templates:
            d = {
                'tpl_id': str(tpl.id),
                'name': tpl.name,
                'desc': tpl.desc,
            }
            tpl_lst.append(d)
        return tpl_lst
