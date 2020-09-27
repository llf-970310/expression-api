#!/your/real/python/path/python
# -*— coding: utf-8 -*-
# Time    : 2018/10/23 下午11:45
# Author  : tangdaye
# Desc    : 统一评分模型USM

# todo 参数化
"""
Desc:   第一种题型评分规则
Input:  第一题的特征列表
Output: 百分制得分
"""

import numpy as np
from functools import reduce

score_parameters = {
    'score1': {
        'tone_quality_total_score': 100,
        'clr_ratio_deduct_percent': 2,
        'clr_ratio_deduct_range': 18,
        'ftl_ratio_deduct_percent': 3,
        'ftl_ratio_deduct_range': 18,
        'time_range_min': 30,
        'time_range_max': 35,
        'time_deduct_persecond': 3,
        'time_deduct_range': 15,
        'phone_score_deduct_per': 0.2,
        'phone_score_deduct_start': 95,
        'phone_score_deduct_range': 6,
        'fluency_score_deduct_per': 0.2,
        'fluency_score_deduct_start': 85,
        'fluency_score_deduct_range': 6,
        'tone_score_deduct_per': 0.2,
        'tone_score_deduct_start': 90,
        'tone_score_deduct_range': 6,
        'integrity_score_deduct_per': 0.2,
        'integrity_score_deduct_start': 99,
        'integrity_score_deduct_range': 6,
        'interval_num_deduct_per': 5,

    },
    'score2': {
    },
    'score3': {}
}


def score1(features, rcg_interface='baidu'):
    para = score_parameters['score1']
    tone_quality = para.get('tone_quality_total_score')
    temp = para['clr_ratio_deduct_percent'] * 100 * (1 - features['clr_ratio'])
    if temp > para['clr_ratio_deduct_range']:
        temp = para['clr_ratio_deduct_range']
    tone_quality -= temp
    temp = para['ftl_ratio_deduct_percent'] * 100 * features['ftl_ratio']
    if temp > para['ftl_ratio_deduct_range']:
        temp = para['ftl_ratio_deduct_range']
    tone_quality -= temp
    if features['last_time'] > para['time_range_max']:
        temp = (features['last_time'] - para['time_range_max']) * para['time_deduct_persecond']
        if temp > para['time_deduct_range']:
            temp = para['time_deduct_range']
        tone_quality -= temp
    if features['last_time'] < para['time_range_min']:
        temp = (para['time_range_max'] - features['last_time']) * para['time_deduct_persecond']
        if temp > para['time_deduct_range']:
            temp = para['time_deduct_range']
        tone_quality -= temp
    if rcg_interface == 'xunfei':
        temp = para['phone_score_deduct_per'] * (para['phone_score_deduct_start'] - features['phone_score'])
        if temp >= 0:
            if temp >= para['phone_score_deduct_range']:
                temp = para['phone_score_deduct_range']
            tone_quality -= temp
        temp = para['fluency_score_deduct_per'] * (para['fluency_score_deduct_start'] - features['fluency_score'])
        if temp >= 0:
            if temp >= para['fluency_score_deduct_range']:
                temp = para['fluency_score_deduct_range']
            tone_quality -= temp
        temp = para['tone_score_deduct_per'] * (para['tone_score_deduct_start'] - features['tone_score'])
        if temp >= 0:
            if temp >= para['tone_score_deduct_range']:
                temp = para['tone_score_deduct_range']
            tone_quality -= temp
        temp = para['integrity_score_deduct_per'] * (para['integrity_score_deduct_start'] - features['integrity_score'])
        if temp >= 0:
            if temp >= para['integrity_score_deduct_range']:
                temp = para['integrity_score_deduct_range']
            tone_quality -= temp
    if features['interval_num'] == 1:
        tone_quality -= para['interval_num_deduct_per']
    if features['interval_num'] >= 2:
        tone_quality -= para['interval_num_deduct_per'] * 2
    tone_quality *= features['cpl_ratio']
    if tone_quality < 0:
        tone_quality = 0
    return {"quality": tone_quality}


def score2(key_hits, detail_hits, key_weights, detail_weights,  rcg_interface='baidu'):
    np_key_hits = np.array([1] + key_hits)
    temp_detail_hits = reduce(lambda x, y: x + y, detail_hits)
    np_detail_hits = np.array([1] + temp_detail_hits)
    np_key_weights = np.array(key_weights)
    np_detail_weights = np.array(detail_weights)
    key = float(0 if np_key_hits[1:].sum() == 0 else (np_key_hits * np_key_weights).sum())
    detail = float(0 if np_detail_hits[1:].sum() == 0 else (np_detail_hits * np_detail_weights).sum())
    return {
        'key': key if 0 <= key <= 100 else ( 0 if key < 0 else 100),
        'detail': detail if 0 <= detail <= 100 else ( 0 if detail < 0 else 100)
    }


def score3(features, rcg_interface='baidu'):
    # 结构
    # 结构判断所⽤用五个词库分别是: 总分，分点，举例，亮观点，总结
    # 评分标准: 按是否击中每类词库算，不不管击中⼏几个词，击中就算⼀一次。⽐比如说回答击中了了总分⼦子
    # 击中⼤于3类词库对应分数80
    # 击中2类词库对应分数70
    # 击中0-1类词库对应分数55
    # 按照字数加分和减分
    structure, logic = 0, 0
    [a1, a2, a3, a4, a5] = [features['sum-aspects_num'] > 0, features['aspects_num'] > 0,
                            features['example_num'] > 0, features['opinion_num'] > 0,
                            features['sum_num'] > 0]
    if a1 + a2 + a3 + a4 + a5 >= 3:
        structure = 80
    elif a1 + a2 + a3 + a4 + a5 == 2:
        structure = 70
    else:
        structure = 55
    if features['num'] > 280:
        structure *= 1.2
    if 45 <= features['num'] < 120:
        structure *= 0.5
    if 10 <= features['num'] < 45:
        structure *= 0.25
    if 5 <= features['num'] < 10:
        structure *= 0.1
    if features['num'] < 5:
        structure = 0

    # 逻辑评分
    # 逻辑判断所用四个词库分别是:因果，转折，并列，递进
    # 击中大于3类词库对应分数80
    # 击中2类词库对应分数75
    # 击中0-1类词库对应分数60
    # 按照字数加分和减分
    [a1, a2, a3, a4] = [features['cause-affect_num'] > 0, features['transition_num'] > 0,
                        features['progressive_num'] > 0, features['parallel_num'] > 0]
    if a1 + a2 + a3 + a4 >= 3:
        logic = 80
    elif a1 + a2 + a3 + a4 == 2:
        logic = 75
    else:
        logic = 60
    if features['num'] > 280:
        logic *= 1.2
    if 45 <= features['num'] < 120:
        logic *= 0.5
    if 10 <= features['num'] < 45:
        logic *= 0.25
    if 5 <= features['num'] < 10:
        logic *= 0.05
    if features['num'] < 5:
        logic = 0

    return {"structure": structure, "logic": logic}
