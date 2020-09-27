#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 18-7-14
import io
import json
import logging
import re
from math import ceil

import Levenshtein
import numpy as np
import wave

import config


def fetch_file_content(filename):
    with open(filename, 'rb') as f:
        json_str = f.read()
    json_dict = json.loads(json_str)
    return json_dict


def rm_pctt(s):
    """去除字符串中的标点符号"""
    punctuation = '''\n\t ,.?!<'">！？；，。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠《》｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."'''
    return re.sub(r"[%s]+" % punctuation, "", s)


def simplify_result(evl_file_content, **kwargs):
    """简化评测结果，保留各句子内容和句子中汉字起止时间(单位为10ms)
    返回内容格式 (符号含义参考讯飞文档https://doc.xfyun.cn/ise_protocol/)
    [{'content': '主要判断第二题', 'words_pos': [['fil', 0, 1], ['判', 1, 30], ... , ['题', 94, 146]]},
     {'content': '以是否答对主旨', 'words_pos': [['sil', 146, 149], ['以', 149, 180], ... , ['旨', 308, 322]]}]
    """
    if kwargs.get('category') != 'read_chapter':
        raise Exception('Please make sure you are simplifying the result of "read_chapter"')
    # sentences - words - syllables - rec_node_type - sil|fil|paper
    simp_result = list()
    if isinstance(evl_file_content, str):
        evl_file_content = json.loads(evl_file_content)
    result = evl_file_content['data']['read_chapter']['rec_paper']['read_chapter']
    sentences = list()
    if isinstance(result['sentence'], dict):  # dict or list
        sentences.append(result['sentence'])
    elif isinstance(result['sentence'], list):
        sentences = result['sentence']
    for sentence in sentences:
        words_pos = list()  # list of [word, start, end]
        words = list()
        if isinstance(sentence['word'], dict):
            words.append(sentence['word'])
        elif isinstance(sentence['word'], list):
            words = sentence['word']
        for word in words:
            # 获取识别内容的字符串要用syll而非word的content
            syllables = list()
            if isinstance(word['syll'], dict):  # word['syll'] might be a dict, see L112 in evl_有不得见者，三十六年.json
                syllables.append(word['syll'])
            elif isinstance(word['syll'], list):
                syllables = word['syll']

            for syllable in syllables:
                if syllable['beg_pos'] != syllable['end_pos']:
                    if syllable['rec_node_type'] == 'paper':
                        words_pos.append([syllable['content'], int(syllable['beg_pos']), int(syllable['end_pos'])])
                    else:
                        sil_fil_obj = [syllable['content'], int(syllable['beg_pos']), int(syllable['end_pos'])]
                        # if len(wtl_arr):
                        #     print(wtl_arr)
                        # print(sil_fil_obj)
                        if len(words_pos) == 0:
                            words_pos.append(sil_fil_obj)
                        elif sil_fil_obj[1] == words_pos[-1][1]:  # sil_fil is in and before the last word
                            words_pos.insert(len(words_pos) - 1, sil_fil_obj)
                            words_pos[-1][1] = sil_fil_obj[2]
                        elif sil_fil_obj[2] == words_pos[-1][2]:  # sil_fil is in and after the last word
                            words_pos[-1][2] = sil_fil_obj[1]
                            words_pos.append(sil_fil_obj)
                        elif sil_fil_obj[1] == words_pos[-1][2]:  # sil_fil is after the last word
                            words_pos.append(sil_fil_obj)
        simp_result.append({'content': sentence['content'], 'phone_score': sentence['phone_score'],
                            'tone_score': sentence['tone_score'], 'fluency_score': sentence['fluency_score'],
                            'total_score': sentence['total_score'], 'words_pos': words_pos})
    chapter_scores = {'integrity_score': result['integrity_score'], 'phone_score': result['phone_score'],
                      'tone_score': result['tone_score'], 'fluency_score': result['fluency_score'],
                      'total_score': result['total_score']}
    return chapter_scores, simp_result


def get_sentence_durations(simp_result):
    sd = list()
    for sentence in simp_result:
        words_pos = sentence['words_pos']
        duration = 0
        word_count = 0
        for wp in words_pos:
            if wp[0] != 'sil' and wp[0] != 'silv' and wp[0] != 'fil':
                word_count += 1
            duration += (wp[2] - wp[1])
            if wp == words_pos[-1]:
                if words_pos[0] == 'sil' or words_pos[0] == 'silv':
                    word_count -= 1
                    duration -= (words_pos[0][2] - words_pos[0][1])
                if words_pos[-1] == 'sil' or words_pos[-1] == 'silv':
                    word_count -= 1
                    duration -= (words_pos[-1][2] - words_pos[-1][1])
                if word_count > 0 and duration > 0:
                    sd.append({'wc': word_count, 'duration': duration / 100})
                duration = 0
                word_count = 0
    return sd


def join_words_pos(simp_result):
    """获取评测中所有识别的汉字及其起止时间"""
    # sentences - words - syllables - content - sil
    joined_words_pos = list()  # list of [word, start, end]
    for sentence in simp_result:
        if sentence['words_pos']:
            joined_words_pos.extend(sentence['words_pos'])
    return joined_words_pos


def get_intervals(simp_result):
    # 1-3.间隔
    intervals = list()
    words_pos = join_words_pos(simp_result)
    for i in range(len(words_pos)):
        if words_pos[i][0] == 'sil' or words_pos[i][0] == 'silv':
            intervals.append(words_pos[i])
    if len(intervals):
        if intervals[0][1] == 0:  # silence at beginning is not interval
            intervals.pop(0)
    if len(intervals):
        if intervals[-1][2] == words_pos[-1][2]:  # silence at end is not interval
            intervals.pop(-1)
    return intervals


def get_cfc(str_rcg, str_std):
    """@:returns 清晰度，无效表达次数，完成度
    出入文本可以带标点，会自动去标点。

    计算cfc(清晰度，无效表达，完成度)应使用识别结果(rcg_xxx.json)而非评测结果(evl_xxx.json)，使用评测结果可能过于宽松

    清晰度几种比较方式：
    1. 按汉字识别个数，不管顺序，优点是简单，缺点也较明显；
    2. 按顺序比较汉字，需完成相关diff算法，将待比较的两向量以0值扩充至等维度，
        然后以difflib.SequenceMatcher()比较；
    3. 比较 Levenshtein 距离(编辑距离)
    此处采用3
    """
    str_rcg = rm_pctt(str_rcg)
    str_std = rm_pctt(str_std)

    total_word_count = len(str_std)
    if total_word_count == 0:
        return
    _L_ops = Levenshtein.opcodes(str_rcg, str_std)

    ftl_count = 0
    for op in _L_ops:
        if op[0] == 'delete':  # 错误发音('replace')不计算在内
            ftl_count += (op[2] - op[1])
    ftl_ratio = ftl_count / total_word_count

    lack_count = 0
    for op in _L_ops:
        if op[0] == 'insert':  # 'replace'也视为完成
            lack_count += (op[4] - op[3])
    cpl_ratio = 1 - lack_count / total_word_count

    eql_count = 0
    for op in _L_ops:
        if op[0] == 'equal':
            eql_count += (op[4] - op[3])
    if cpl_ratio != 0:
        clr_ratio = eql_count / total_word_count / cpl_ratio  # 只需看完成部分
    else:
        clr_ratio = 0
    return {'clr_ratio': clr_ratio, 'ftl_ratio': ftl_ratio, 'cpl_ratio': cpl_ratio}


def read_wave_data(wav_file):
    if isinstance(wav_file, io.BytesIO):
        wav_file.seek(0)  # seek(0) before read
    with wave.open(wav_file, 'rb') as f:
        params = f.getparams()  # file header, return tuple
        # print("Wave file header:\n\t", params, '\n')
        nchannels, sampwidth, framerate, nframes = params[:4]
        data_str = f.readframes(nframes)
    # save wav data as numpy array
    wave_data = np.fromstring(data_str, dtype=np.short)

    if nchannels == 2:  # stereo
        wave_data.shape = -1, 2  # shape the array to n*2 (format is LRLRLR...)
        wave_data = wave_data.T[0]  # use Left channel only
        logging.warn("THE WAV FILE IS STEREO, MAYBE NOT SUPPORTED BY RECOGNITION API!")

    # calculate the time
    time = np.arange(0, nframes) * (1.0 / framerate)
    return wave_data, time


def get_ampl(simp_result, wf, **kwargs):
    wave_data, time = read_wave_data(wf)
    ampl_lst = list()
    for sentence in simp_result:
        words_pos = sentence['words_pos']
        for wp in words_pos:
            if wp[0] != 'sil' and wp[0] != 'silv' and wp[0] != 'fil':
                index_low = np.where(time >= wp[1] / 100)[0][0]
                index_high = np.where(time <= wp[2] / 100)[0][-1]
                avg_amp = np.average(np.abs(wave_data[index_low:index_high]))
                ampl_lst.append({'word': wp[0], 'ampl': avg_amp})
    return ampl_lst


def get_volume(wav_file, segments=1):
    volume_lst = []
    if isinstance(wav_file, io.BytesIO):
        wav_file.seek(0)  # seek(0) before read
    with wave.open(wav_file, 'rb') as wf:
        params = wf.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        seg_frames = ceil(nframes / segments)
        chunk = wf.readframes(seg_frames)
        while chunk != b'':
            volume_lst.append(np.average(np.abs(np.frombuffer(chunk, dtype=np.int16))))
            chunk = wf.readframes(seg_frames)
    while len(volume_lst) < segments:
        volume_lst.append(0)

    return volume_lst


if __name__ == "__main__":

    n = 33
    config.WAV_FILE_PATH = "audio/Samples2/%d/1.wav" % n
    config.RCG_JSON_FILE_PATH = "text_files/Samples2/rcg_%d_1.json" % n
    config.EVL_JSON_FILE_PATH = "text_files/Samples2/evl_%d_1.json" % n
    # config.WAV_FILE_PATH = "audio/Professional2/%d/1.wav" % n
    # config.RCG_JSON_FILE_PATH = "text_files/Professional2/rcg_%d_1.json" % n
    # config.EVL_JSON_FILE_PATH = "text_files/Professional2/evl_%d_1.json" % n

    """时间上的处理使用讯飞评测结果，cfc的计算使用讯飞识别结果"""

    evl_file_content = fetch_file_content(config.EVL_JSON_FILE_PATH)
    chapter_scores, simp_result = simplify_result(evl_file_content, category=config.XF_EVL_CATEGORY)
    with open(config.STD_TEXT_FILE_PATH) as f:
        text_std = f.read()
    words_std = rm_pctt(text_std)
    with open(config.RCG_JSON_FILE_PATH) as f:
        text_rcg = json.loads(f.read())['data']
    words_rcg = rm_pctt(text_rcg)

    print(get_volume(config.WAV_FILE_PATH, segments=3))
