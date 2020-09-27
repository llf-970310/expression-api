#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 18-7-13
import logging
import os
import threading
import urllib.parse
import urllib.request
import time
import json
import hashlib
import base64
import wave
from math import ceil

import config
import io

import utils


class RcgCore(object):  # 不再使用线程
    def __init__(self, wav_file, timeout=600, x_appid=None, api_key=None):
        self.wav_file = wav_file
        self.timeout = timeout
        self.x_appid = x_appid
        self.api_key = api_key
        self.result = None

    def run(self):
        file_content = utils.read(self.wav_file, 'rb')
        base64_audio = base64.b64encode(file_content)  # 参数是bytes类型，返回也是bytes类型
        body = urllib.parse.urlencode({'audio': base64_audio})
        url = config.XF_RCG_URL
        if self.x_appid is None:
            self.x_appid = config.XF_RCG_APP_ID
        if self.api_key is None:
            self.api_key = config.XF_RCG_API_KEY
        param = {"engine_type": config.XF_RCG_ENGINE_TYPE, "aue": "raw"}
        x_param = base64.b64encode(json.dumps(param).replace(' ', '').encode('utf-8'))
        x_time = int(int(round(time.time() * 1000)) / 1000)

        # print(x_param)  # bytes
        x_checksum_content = self.api_key + str(x_time) + str(x_param, 'utf-8')
        x_checksum = hashlib.md5(x_checksum_content.encode('utf-8')).hexdigest()

        # 讯飞api说明：
        # 授权认证，调用接口需要将Appid，CurTime, Param和CheckSum信息放在HTTP请求头中；
        # 接口统一为UTF-8编码；
        # 接口支持http和https；
        # 请求方式为POST。
        x_header = {'X-Appid': self.x_appid,
                    'X-CurTime': x_time,
                    'X-Param': x_param,
                    'X-CheckSum': x_checksum}
        req = urllib.request.Request(url=url, data=body.encode('utf-8'), headers=x_header, method='POST')
        max_retry = config.RCG_MAX_RETRY
        for retry in range(max_retry + 1):
            try:
                rst = urllib.request.urlopen(req, timeout=self.timeout)
                self.result = rst.read().decode('utf-8')
                break
            except Exception as e:
                logging.warning('RcgCore: on retry %d:' % retry)
                logging.warning(e)

    def get_result(self):
        return self.result


def _rcg(wav_file, timeout=600, segments=0, x_appid=None, api_key=None) -> dict:
    # 音频切段：
    segment_files = {}
    if isinstance(wav_file, io.BytesIO):
        wav_file.seek(0)  # seek(0) before read
    with wave.open(wav_file, 'rb') as wf:
        params = wf.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        duration = nframes / framerate
        if segments == 0:  # if segments is not assigned manually, calculate segments count
            segments = ceil(duration / 60)
        if segments == 1:
            segment_files[0] = wav_file
        if segments >= 2:  # cut wav into segments (average length)
            logging.debug("Cutting %s by into %d segments..." % (wav_file, segments))
            seg_length = ceil(duration / segments * framerate)  # how many frames per segment
            for i in range(segments):
                segment_files[i] = io.BytesIO()
                seg_data = wf.readframes(seg_length)
                with wave.open(segment_files[i], 'wb') as seg:
                    seg.setnchannels(nchannels)
                    seg.setsampwidth(sampwidth)
                    seg.setframerate(framerate)
                    seg.writeframes(seg_data)
    # 识别：
    results = {}
    for i in range(segments):
        job = RcgCore(segment_files[i], timeout, x_appid, api_key)
        job.run()
        results[i] = job.get_result()
        rcg_dict = json.loads(results[i])
        if rcg_dict.get('code') == '10105':
            print('IP错误, 请把下面的IP添加至讯飞云IP白名单并等待两分钟再试!!')
            print(rcg_dict.get('desc').strip('illegal access|illegal client_ip: '))  # no need to use replace here
            print()
            raise Exception('RCG IP Error')
    logging.debug('summarized rcg results: %s' % results)
    return results


def rcg_and_save(wave_file, rcg_fp, segments=0, timeout=600, x_appid=None, api_key=None, stop_on_failure=True):
    rcg_result = _rcg(wave_file, segments=segments, timeout=timeout, x_appid=x_appid, api_key=api_key)
    if rcg_result:
        rcgs_dict = {}
        rcgs_status = {}
        data_lst = []
        for i in range(len(rcg_result)):
            if rcg_result[i] is not None:
                rcgs_dict[i] = json.loads(rcg_result[i])
                rcgs_status[i] = rcgs_dict[i]['desc']
                if rcgs_dict[i].get('code') == '0':
                    data_lst.append(rcgs_dict[i].get('data'))
                else:
                    if stop_on_failure:
                        raise Exception('rcg failure: %s SEG %d - %s' % (wave_file, i, rcgs_dict[i].get('code')))
                    else:
                        logging.info('rcg failure: %s SEG %d - %s' % (wave_file, i, rcgs_dict[i].get('code')))
            else:
                data_lst.append('')
        logging.info('Multi segments rcg result: %s' % rcgs_status)

        if rcg_result[0] is None:
            rcgs_dict[0] = {'code': '0', 'data': '', 'desc': 'None'}

        rcgs_dict[0]['data'] = data_lst  # 结果一直是列表，如果只有一段就是长度为1的列表 tangdaye 11-21
        utils.write(rcg_fp, json.dumps(rcgs_dict[0], ensure_ascii=False), 'w')  # dump as utf-8
    if isinstance(rcg_fp, str):
        if not os.path.exists(rcg_fp):
            rcgs_dict = {'code': '0', 'data': '', 'desc': 'None'}
            utils.write(rcg_fp, json.dumps(rcgs_dict, ensure_ascii=False), 'w')  # dump as utf-8


if __name__ == '__main__':
    import time
    time1 = time.time()
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s:\t%(message)s')

    # result = rcg(config.WAV_FILE_PATH, segments=1, timeout=100)
    # rcg(config.WAV_FILE_PATH, timeout=10, segments=3)
    # print(isinstance(result, str))
    # print(isinstance(result, dict))

    wave_file_processed = io.BytesIO()
    interval_list = utils.find_and_remove_intervals('net_test.wav', wave_file_processed)

    rcg_fp = io.StringIO()
    rcg_and_save(wave_file_processed, rcg_fp, segments=3, timeout=1, stop_on_failure=True)

    print(utils.read(rcg_fp))
    print(time.time() - time1)
