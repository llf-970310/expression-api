#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 19-3-10

import config
import io
import logging
import time
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
from baidubce.services.bos.bos_client import BosClient
from subprocess import Popen, PIPE

# configurations
access_key_id = config.BD_BOS_AK
secret_access_key = config.BD_BOS_SK
bos_host = config.BD_BOS_HOST
bucket_name = config.BD_BOS_BUCKET


def bytes_io_m4a2wav(bytes_io_file):
    bytes_io_file.seek(0)
    content = bytes_io_file.getvalue()
    cmd = ['ffmpeg', '-i', 'pipe:', '-acodec', 'pcm_s16le', '-f', 'wav', '-ac', '1', '-ar', '8000', 'pipe:']
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=-1)
    out, _ = p.communicate(input=content)
    p.stdin.close()
    return io.BytesIO(out) if out.startswith(b'RIFF\xff\xff\xff') else None


def get_bos_file_bytes_io(path):
    logger = logging.getLogger("baidubce.http.bce_http_client")
    logger.setLevel(logging.DEBUG)
    logging.info('Getting file from Baidu BOS...')

    bos_config = BceClientConfiguration(credentials=BceCredentials(access_key_id, secret_access_key),
                                        endpoint=bos_host)
    bos_client = BosClient(bos_config)
    content = bos_client.get_object_as_string(bucket_name=bucket_name, key=path)
    audio = io.BytesIO(content)  # this would auto seek(0)
    return audio


def get_wav_file_bytes_io(file_key, location='bos', bos_retries=10, retry_interval=2):
    """
    :param file_key: BOS key 或 文件路径
    :param location: bos 或 local，不区分大小写
    :param bos_retries: 获取失败时重试次数(仅针对bos)
    :param retry_interval: 重试前等待时间
    :return:
    """
    file = None
    if location.lower() == 'bos':
        cnt = 0
        while cnt <= bos_retries:
            try:
                file = get_bos_file_bytes_io(file_key)
                if file:
                    break
                cnt += 1  # 保安全，万一不except
            except Exception as e:
                print('Exception on retry %s:%s' % (cnt, e))
                time.sleep(retry_interval)
                cnt += 1
    elif location.lower() == 'local':
        with open(file_key, 'rb') as f:
            file = io.BytesIO(f.read())
    if file is None:
        raise Exception('Failed to get file from BOS after retries %s' % bos_retries)
    if file_key.strip().endswith('.m4a'):  # 小程序的m4a转换为pcm
        file = bytes_io_m4a2wav(file)
    return file


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s:\t%(message)s')
    print(get_bos_file_bytes_io('audio/2019-05-21/5c939bb4cb08361b85b63be9/1558444193r688.wav'))  # BOS默认目录是根目录，最前有无/都可以
    # print(get_bos_file_bytes_io('/audio/batchtest/1.wav'))

# response = bos_client.list_buckets()
# for bucket in response.buckets:
#     print(bucket.name)

# ret = bos_client.put_object_from_string(bucket=bucket_name, key='/test.txt', data='hello world')
# print(ret)
# with open('net_test.wav', 'rb') as f:
#     data = f.read()
#
# wf = io.BytesIO(data)
# ret = bos_client.put_object_from_file(bucket=bucket_name, key='/test-BytesIO-file.wav', file_name=wf)
# print(ret)
# f2 = io.StringIO('hello world')
# ret = bos_client.put_object_from_file(bucket=bucket_name, key='/test.txt', file_name=f2)
# print(ret)
# logger = logging.getLogger("baidubce.http.bce_http_client")
# logger.setLevel(logging.DEBUG)
#
# bos_config = BceClientConfiguration(credentials=BceCredentials(access_key_id, secret_access_key),
#                                     endpoint=bos_host)
# bos_client = BosClient(bos_config)
# content = bos_client.get_object_as_string(bucket_name=bucket_name, key='/audio/batchtest/1.wav')
#
# print('cc' + str(type(content)))
# print(content)

# audio = io.BytesIO(content)  # this would auto seek(0)


# if __name__ == '__main__':
#     file = '8-1576685164r111.m4a'
#     with open(file, 'rb') as f:
#         data = BytesIO(f.read())
#     print(type(bytes_io_m4a2wav(data)))
