# -*- coding: utf-8 -*-

"""
    Speech
"""

from .base import AipBase
from .base import base64
from .base import hashlib
from .base import json


class AipSpeech(AipBase):
    """
        Aip Speech
    """

    __asrProUrl = 'https://vop.baidubce.com/pro_api'
    __asrUrl = 'http://vop.baidubce.com/server_api'

    def _isPermission(self, authObj):
        """
            check whether permission
        """

        return True    

    def _proccessRequest(self, url, params, data, headers):
        """
            参数处理
        """

        token = params.get('access_token', '')

        if not data.get('cuid', ''):
            data['cuid'] = hashlib.md5(token.encode()).hexdigest()

        data['token'] = token
        data = json.dumps(data)

        if 'access_token' in params:
            del params['access_token']

        return data

    def _proccessResult(self, content):
        """
            formate result
        """

        try:
            return super(AipSpeech, self)._proccessResult(content)
        except Exception as e:
            return {
                '__json_decode_error': content,
            }

    def asr_pro(self, speech=None, format='pcm', rate=16000, options=None):
        """
            语音识别
        """

        data = {}

        if speech:
            data['speech'] = base64.b64encode(speech).decode()
            data['len'] = len(speech)

        data['channel'] = 1
        data['format'] = format
        data['rate'] = rate

        data = dict(data, **(options or {}))

        return self._request(self.__asrProUrl, data)

    def asr(self, speech=None, format='pcm', rate=16000, options=None):
        """
            语音识别
        """

        data = {}

        if speech:
            data['speech'] = base64.b64encode(speech).decode()
            data['len'] = len(speech)

        data['channel'] = 1
        data['format'] = format
        data['rate'] = rate

        data = dict(data, **(options or {}))

        return self._request(self.__asrUrl, data)



