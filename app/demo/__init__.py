#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-2-24

from flask import Blueprint

demo = Blueprint('demo', __name__)

from . import views
