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

def analysis2(wave_file, wordbase, timeout=30, rcg_txt=None, rcg_interface='baidu'):
    result = {
        'rcg_text': 0,
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
        'keywords_num': [0, 1],
        'keywords': [],
        'mainwords_num': [0, 1],
        'mainwords': [],
        'detailwords_nums': [],
        'detailwords': [],
        'keywords_num_main': [0, 1],
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
        if last > config.INTERVAL_TIME_THRESHOLD2 and start > 0 and start + last > result['last_time'] - 0.02:
            result['interval_num'] += 1
            result['interval_ratio'] += last
    if result['last_time'] == 0:
        result['interval_ratio'] = 1
    else:
        result['interval_ratio'] /= result['last_time']
    # 识别用擦除过的文件
    rcg_result_file = io.StringIO()
    # 分段识别
    if rcg_txt:
        rcg_text = rcg_txt
    else:
        base_recognise.rcg_and_save(wave_file_processed, rcg_result_file, timeout=timeout,
                                    segments=config.SEGMENTS_RCG2, rcg_interface=rcg_interface)
        temp = json.loads(rcg_result_file.getvalue()).get('data')
        if temp and len(temp) == config.SEGMENTS_RCG2:
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
    result['num'] = feature_text.len_without_punctuation(rcg_text)
    # 词性比例
    # proportions = feature_text.proportion(rcg_text)
    # all_words_num = proportions['all']
    # if all_words_num == 0:
    #     all_words_num = 1
    # result['n_ratio'] = proportions['n'] / all_words_num
    # result['v_ratio'] = proportions['v'] / all_words_num
    # result['vd_ratio'] = proportions['vd'] / all_words_num
    # result['vn_ratio'] = proportions['vn'] / all_words_num
    # result['a_ratio'] = proportions['a'] / all_words_num
    # result['ad_ratio'] = proportions['ad'] / all_words_num
    # result['an_ratio'] = proportions['an'] / all_words_num
    # result['d_ratio'] = proportions['d'] / all_words_num
    # result['m_ratio'] = proportions['m'] / all_words_num
    # result['q_ratio'] = proportions['q'] / all_words_num
    # result['r_ratio'] = proportions['r'] / all_words_num
    # result['p_ratio'] = proportions['p'] / all_words_num
    # result['c_ratio'] = proportions['c'] / all_words_num
    # result['u_ratio'] = proportions['u'] / all_words_num
    # result['xc_ratio'] = proportions['xc'] / all_words_num
    # result['w_ratio'] = proportions['w'] / all_words_num
    # result['ne_ratio'] = proportions['ne'] / all_words_num
    # result['word_num'] = all_words_num
    # # noun frequency 名词 人名 地名 机构名 作品名 其他专名 专名识别缩略词
    # nouns = proportions['nouns']
    # result['noun_frequency_2'], result['noun_frequency_3'], result['noun_frequency_4'] = feature_text.words_frequency(
    #     nouns)
    # sentence_num
    result['sentence_num'] = len(feature_text.divide_text_to_sentence(rcg_text))
    # 词库击中，谐音
    keywords, mainwords, detailwords = wordbase.get('keywords'), wordbase.get('mainwords'), wordbase.get('detailwords')
    for word in keywords:
        hitwords = feature_text.words_pronunciation(text=rcg_text, answers=word)
        if len(hitwords) >= 1:
            result['keywords_num'][0] += 1
            result['keywords'].append(hitwords[0])
        else:
            result['keywords'].append('')
        hitwords = feature_text.words_pronunciation(text=rcg_text[:config.MAIN_IDEA_WORD_COUNT], answers=word)
        if len(hitwords) >= 1:
            result['keywords_num_main'][0] += 1
    result['keywords_num'][1] = len(keywords)
    result['keywords_num_main'][1] = len(keywords)
    for word in mainwords:
        hitwords = feature_text.words_pronunciation(text=rcg_text, answers=word)
        if len(hitwords) >= 1:
            result['mainwords_num'][0] += 1
            result['mainwords'].append(hitwords[0])
        else:
            result['mainwords'].append('')
    result['mainwords_num'][1] = len(mainwords)
    for temp_l in detailwords:
        x = 0
        temp_x = []
        for word in temp_l:
            hitwords = feature_text.words_pronunciation(text=rcg_text, answers=word)
            if len(hitwords) >= 1:
                x += 1
                temp_x.append(hitwords[0])
            else:
                temp_x.append('')
        result['detailwords_nums'].append([x, len(temp_l)])
        result['detailwords'].append(temp_x)
    # volume
    result['volumes'] = feature_audio.get_volume(wave_file_processed, config.SEGMENTS_VOLUME2)
    return result


def score2(features, rcg_interface='baidu'):
    main_idea, detail = 0, 0
    mainidea_time_list = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 10000)]
    mainidea_wordcount_list = [(0, 10), (10, 30), (30, 40), (40, 50), (50, 100), (100, 120), (120, 10000)]
    mainidea_score_list = [[0, 0, 0, 0, 0, 0, 0],
                           [0, 40, 60, 100, 100, 100, 100],
                           [0, 100, 100, 100, 100, 100, 100],
                           [0, 100, 100, 100, 100, 100, 100],
                           [0, 100, 100, 100, 100, 100, 100],
                           [0, 100, 100, 100, 100, 100, 100]]
    detail_time_list = [(0, 5), (5, 10), (10, 15), (15, 20), (20, 30), (30, 10000)]
    detail_wordcount_list = [(0, 10), (10, 30), (30, 50), (50, 80), (80, 100), (100, 120), (120, 10000)]
    detail_score_list = [[0, 0, 0, 0, 0, 0, 0],
                         [0, 30, 30, 30, 30, 30, 30],
                         [0, 30, 60, 60, 60, 60, 60],
                         [0, 30, 60, 80, 80, 80, 80],
                         [0, 30, 60, 80, 100, 100, 100],
                         [0, 30, 80, 100, 100, 100, 100]]
    # 基础分
    last_time = features['last_time']
    words_count = features['num']
    for i in range(len(mainidea_time_list)):
        for j in range(len(mainidea_wordcount_list)):
            if mainidea_time_list[i][0] <= last_time < mainidea_time_list[i][1]:
                if mainidea_wordcount_list[j][0] <= words_count < mainidea_wordcount_list[j][1]:
                    main_idea = mainidea_score_list[i][j]
    for i in range(len(detail_time_list)):
        for j in range(len(detail_wordcount_list)):
            if detail_time_list[i][0] <= last_time < detail_time_list[i][1]:
                if detail_wordcount_list[j][0] <= words_count < detail_wordcount_list[j][1]:
                    detail = detail_score_list[i][j]
    keywords_num = features['keywords_num']
    mainwords_num = features['mainwords_num']
    details_num = features['detailwords_nums']
    # 按照比例乘
    main_idea *= (keywords_num[0] / keywords_num[1])
    # 每少1个主干关键词扣6分
    main_idea -= (mainwords_num[1] - mainwords_num[0]) * 6
    # 按照比例乘
    single_detail = detail / len(details_num)
    for temp in details_num:
        if temp[0] / temp[1] == 1:
            pass
        elif temp[0] / temp[1] >= 0.5:
            detail -= single_detail * 0.2
        elif temp[0] / temp[1] > 0:
            detail -= single_detail * 0.4
        else:
            detail -= single_detail
    # 其他可用属性：前n秒关键词['keywords_num_main']
    if main_idea <= 0:
        main_idea = 0
    if detail <= 0:
        detail = 0
    return {"main": main_idea, "detail": detail}