#!/your/real/python/path/python
# -*— coding: utf-8 -*-
# Time    : 2018/10/23 下午11:43
# Author  : tangdaye
# Desc    : 统一音频分析模型UAAM

# # do NOT use xf_recognise.rcg directly
# # do NOT use xf_evaluate.evl directly

import io
import base_recognise
import base_evaluate
import feature_text
import feature_audio
import wave
import utils
import config
import numpy
import json

"""
Desc:   第一种题型特征提取
Input:  源wav文件地址，标准文本
Output: feature列表
"""


def analysis1(wave_file, std_text, timeout=30, rcg_interface='baidu', segments=config.SEGMENTS_RCG1):
    result = {
        'rcg_text': '',
        'rcg_interface': rcg_interface,
        'num': 0,  # 字数
        'last_time': 0,  # 长度
        'interval_num': 0,  # 超过0.7秒时间间隔数量
        'interval_ratio': 0,  # 超过0.7秒时间间隔占比
        'clr_ratio': 0,  # 清晰度
        'ftl_ratio': 0,  # 无效表达比率
        'cpl_ratio': 0,  # 完成度
        'phone_score': 0,  # 声韵分
        'fluency_score': 0,  # 流畅度分
        'tone_score': 0,  # 调型分
        'integrity_score': 0,  # 完整度分
        'speed': 0,  # 平均语速
        'speed_deviation': 0,  # 语速标准差
        'speeds': [],
        'volumes': 0,  # 音量列表
    }
    wave_file_processed = io.BytesIO()
    # 间隔
    interval_list = utils.find_and_remove_intervals(wave_file, wave_file_processed)
    temp_std_text_file = io.StringIO()
    temp_std_text_file.write(std_text)
    rcg_result_file = io.StringIO()
    # last_time 时长 未擦除的文件
    result['last_time'] = utils.get_audio_length(wave_file)
    for (start, last) in interval_list:
        if last > config.INTERVAL_TIME_THRESHOLD1 and start > 0 and start + last > result['last_time'] - 0.02:
            result['interval_num'] += 1
            result['interval_ratio'] += last
    if result['last_time'] == 0:
        result['interval_ratio'] = 1
    else:
        result['interval_ratio'] /= result['last_time']
    # 识别
    rcg_text = ''
    if rcg_interface == 'xunfei':
        # rcg_text
        base_recognise.rcg_and_save(wave_file_processed, rcg_result_file, timeout=timeout, rcg_interface=rcg_interface)
        rcg_text = json.loads(rcg_result_file.getvalue()).get('data')
        result['rcg_text'] = rcg_text
        # phone_score,fluency_score,tone_score,integrity_score
        evl_result_file = io.StringIO()
        base_evaluate.evl_and_save(wave_file_processed, temp_std_text_file, evl_result_file, framerate=8000,
                                   timeout=timeout)
        eva_result = evl_result_file.getvalue()
        chapter_scores, simp_result = feature_audio.simplify_result(eva_result, category=config.XF_EVL_CATEGORY)
        result['phone_score'], result['fluency_score'], result['tone_score'], result['integrity_score'] = \
            float(chapter_scores['phone_score']), float(chapter_scores['fluency_score']), float(
                chapter_scores['tone_score']), float(chapter_scores['integrity_score'])
        # speeds
        speeds = numpy.array([wc / time for (wc, time) in utils.get_sentence_durations(simp_result)])
        result['speed'] = numpy.mean(speeds)
        result['speed_deviation'] = numpy.std(speeds)
    elif rcg_interface == 'baidu':
        # rcg_text，百度需要分段
        base_recognise.rcg_and_save(wave_file_processed, rcg_result_file, timeout=timeout,
                                    segments=segments, rcg_interface=rcg_interface)
        temp = json.loads(rcg_result_file.getvalue()).get('data')
        if temp :
            rcg_text = ''.join(temp)
        else:
            rcg_text = ''
        result['rcg_text'] = rcg_text
        # speed
        if not result['last_time'] == 0:
            result['speeds'] = [
                segments * feature_text.len_without_punctuation(rcg_text_seg) / result['last_time'] for
                rcg_text_seg in temp]
            result['speed'] = numpy.mean(result['speeds'])
            result['speed_deviation'] = numpy.std(result['speeds'])
    # clr_ratio,ftl_ratio,cpl_ratio
    cfc = feature_audio.get_cfc(rcg_text, std_text)
    result['clr_ratio'], result['ftl_ratio'], result['cpl_ratio'] = cfc['clr_ratio'], cfc['ftl_ratio'], cfc[
        'cpl_ratio']
    # 字数
    result['num'] = feature_text.len_without_punctuation(rcg_text)
    # volume
    volume_list = feature_audio.get_volume(wave_file_processed, config.SEGMENTS_VOLUME1)
    result['volumes'] = volume_list
    return result


def analysis2(wave_file, wordbase, timeout=30, voice_features=None, rcg_interface='baidu'):
    result = {
        'rcg_text': '',
        'key_hits': [],     # key击中列表
        'keywords': [],     # 击中的keyword列表
        'detail_hits': [],  # detail击中列表
        'detailwords': [],  # 击中的detailword列表
        'num': 0,           # 字数
        'sentence_num': 0,  # 句子数

        'last_time': 0,     # 持续时间
        'interval_num': 0,  # 中断次数
        'interval_ratio': 0,    # 中断比率
        'volumes': 0,
        'speeds': 0,

    }

    # 分析音频特征并分段识别，如果传入voice_features就不分析
    if voice_features:
        result['rcg_text'] = voice_features['rcg_text']
        result['last_time'] = voice_features['last_time']
        result['interval_num'] = voice_features['interval_num']
        result['interval_ratio'] = voice_features['interval_ratio']
        result['volumes'] = voice_features['volumes']
        result['speeds'] = voice_features['speeds']
    else:
        # last_time 时长 未擦除的文件
        with wave.open(wave_file) as wav:
            result['last_time'] = wav.getnframes() / wav.getframerate()
        # interval 未擦除的文件
        wave_file_processed = io.BytesIO()
        interval_list = utils.find_and_remove_intervals(wave_file, wave_file_processed)
        for (start, last) in interval_list:
            if last > config.INTERVAL_TIME_THRESHOLD2 and start > 0 and start + last > result['last_time'] - 0.02:
                result['interval_num'] += 1
                result['interval_ratio'] += last
        if result['last_time'] == 0:
            result['interval_ratio'] = 1
        else:
            result['interval_ratio'] /= result['last_time']
        # 识别用擦除过的文件
        rcg_result_file = io.StringIO()
        # volume
        result['volumes'] = feature_audio.get_volume(wave_file_processed, config.SEGMENTS_VOLUME2)

        # 分段识别
        base_recognise.rcg_and_save(wave_file_processed, rcg_result_file, timeout=timeout,
                                    segments=config.SEGMENTS_RCG2, rcg_interface=rcg_interface)
        temp = json.loads(rcg_result_file.getvalue()).get('data')
        if temp:
            rcg_text = ''.join(temp)
        else:
            rcg_text = ''
        # speed
        if not result['last_time'] == 0:
            result['speeds'] = [
                config.SEGMENTS_RCG2 * feature_text.len_without_punctuation(rcg_text_seg) / result['last_time'] for
                rcg_text_seg in temp]
        result['rcg_text'] = rcg_text

    # 字数
    result['num'] = feature_text.len_without_punctuation(result['rcg_text'])

    # 句子数
    result['sentence_num'] = len(feature_text.divide_text_to_sentence(result['rcg_text']))

    # 词库击中，谐音
    keywords, detailwords = wordbase.get('keywords'), wordbase.get('detailwords')

    for word in keywords:
        hitwords = feature_text.words_pronunciation(text=result['rcg_text'], answers=word)
        if len(hitwords) >= 1:
            result['key_hits'].append(1)  # 是否击中
            result['keywords'].append(hitwords[0])  # 添加被击中的词语
        else:
            result['key_hits'].append(0)
            result['keywords'].append('')

    for temp_l in detailwords:
        x = 0
        temp_words = []
        temp_hits = []
        for word in temp_l:
            hitwords = feature_text.words_pronunciation(text=result['rcg_text'], answers=word)
            if len(hitwords) >= 1:
                x += 1
                temp_hits.append(1)  # 是否击中
                temp_words.append(hitwords[0])  # 添加被击中的词语
            else:
                temp_hits.append(0)
                temp_words.append('')
        result['detail_hits'].append(temp_hits)
        result['detailwords'].append(temp_words)

    return result


def analysis3(wave_file, wordbase, timeout=30, rcg_interface='baidu'):
    result = {
        'rcg_text': '',
        'num': 0,
        'last_time': 0,
        'interval_num': 0,
        'interval_ratio': 0,
        'n_ratio': 0,
        'v_ratio': 0,
        'vd_ratio': 0,
        'vn_ratio': 0,
        'a_ratio': 0,
        'ad_ratio': 0,
        'an_ratio': 0,
        'd_ratio': 0,
        'm_ratio': 0,
        'q_ratio': 0,
        'r_ratio': 0,
        'p_ratio': 0,
        'c_ratio': 0,
        'u_ratio': 0,
        'xc_ratio': 0,
        'w_ratio': 0,
        'ne_ratio': 0,
        'word_num': 0,
        'noun_frequency_2': 0,
        'noun_frequency_3': 0,
        'noun_frequency_4': 0,
        'sentence_num': 0,
        'sum-aspects_num': 0,
        'aspects_num': 0,
        'example_num': 0,
        'opinion_num': 0,
        'sum_num': 0,
        'cause-affect_num': 0,
        'transition_num': 0,
        'progressive_num': 0,
        'parallel_num': 0,
        'speeds': 0,
        'volumes': 0,
    }
    # last_time 时长 未擦除的文件
    with wave.open(wave_file) as wav:
        result['last_time'] = wav.getnframes() / wav.getframerate()
    # interval 未擦除的文件
    wave_file_processed = io.BytesIO()
    interval_list = utils.find_and_remove_intervals(wave_file, wave_file_processed)
    for (start, last) in interval_list:
        if last > config.INTERVAL_TIME_THRESHOLD3 and start > 0 and start + last > result['last_time'] - 0.02:
            result['interval_num'] += 1
            result['interval_ratio'] += last
    if result['last_time'] == 0:
        result['interval_ratio'] = 1
    else:
        result['interval_ratio'] /= result['last_time']
    # 识别用擦除过的文件，显式指定分段
    rcg_result_file = io.StringIO()
    base_recognise.rcg_and_save(wave_file_processed, rcg_result_file, segments=config.SEGMENTS_RCG3, timeout=timeout,
                                rcg_interface=rcg_interface, use_pro_api=True)  # pro_api: 极速版50qps,16k
    temp = json.loads(rcg_result_file.getvalue()).get('data')
    if temp and len(temp) == config.SEGMENTS_RCG3:
        rcg_text = ''.join(temp)
    else:
        rcg_text = ''
    result['rcg_text'] = rcg_text
    # 字数
    result['num'] = feature_text.len_without_punctuation(rcg_text)
    # sentence_num
    result['sentence_num'] = len(feature_text.divide_text_to_sentence(rcg_text))
    # 词库击中 谐音
    result['sum-aspects_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('sum-aspects')))
    result['aspects_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('aspects')))
    result['example_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('example')))
    result['opinion_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('opinion')))
    result['sum_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('sum')))
    result['cause-affect_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('cause-affect')))
    result['transition_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('transition')))
    result['progressive_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('progressive')))
    result['parallel_num'] = len(feature_text.words_pronunciation(rcg_text, wordbase.get('parallel')))
    # speed
    if not result['last_time'] == 0:
        result['speeds'] = [
            config.SEGMENTS_RCG3 * feature_text.len_without_punctuation(rcg_text_seg) / result['last_time'] for
            rcg_text_seg in temp]
    # volume
    result['volumes'] = feature_audio.get_volume(wave_file_processed, config.SEGMENTS_VOLUME3)

    return result


if __name__ == '__main__':
    pass
