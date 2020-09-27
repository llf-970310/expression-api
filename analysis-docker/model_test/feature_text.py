# -*— coding: utf-8 -*-
import bd_nlp
import time
import re
from pronunciation import in_pronunciation

'''
文本特性1：给定一段文本，给出其中各种词性的占比
'''


def is_all_zh(s):
    for c in s:
        if not ('\u4e00' <= c <= '\u9fa5'):
            return False
    return True


def proportion(text):
    parts = ['n', 'f', 's', 't', 'nr', 'ns', 'nt', 'nw', 'nz', 'v', 'vd', 'vn', 'a', 'ad', 'an', 'd', 'm', 'q', 'r',
             'p', 'c', 'u', 'xc', 'w', 'ne']
    nouns_parts = ['n', 'nr', 'ns', 'nt', 'nw', 'nz', 'ne']
    result = bd_nlp.divide_words(text)
    proportions = {
        'nouns': []
    }
    nums = len(result['all'])
    proportions['all'] = nums
    for key in parts:
        if key in result.keys():
            proportions[key] = len(result[key])
            if key in nouns_parts:
                proportions['nouns'] += result[key]
        else:
            proportions[key] = 0
    return proportions


'''
文本特性2：给定一段文本，给出其句法分析分词结果（分句）
'''


def parse(text):
    proportions = {}
    parts = ['all', 'Ag', 'a', 'ad', 'an', 'b', 'c', 'dg', 'd', 'e', 'f',
             'g', 'h', 'i', 'j', 'k', 'l', 'm', 'Ng', 'n', 'nr',
             'ns', 'nt', 'nz', 'o', 'p', 'q', 'r', 's', 'tg', 't',
             'u', 'vg', 'v', 'vd', 'vn', 'w', 'x', 'y', 'z', 'un',
             'ATT', 'QUN', 'COO', 'APP', 'ADJ', 'VOB', 'POB', 'SBV', 'SIM', 'TMP',
             'LOC', 'DE', 'DI', 'DEI', 'SUO', 'BA', 'BEI', 'ADV', 'CMP', 'DBL',
             'CNJ', 'CS', 'MT', 'VV', 'HED', 'FOB', 'DOB', 'TOP', 'IS', 'IC',
             'DC', 'VNV', 'YGC', 'WP']
    for key in parts:
        proportions[key] = 0

    group = divide_text_to_sentence(text)
    for sentence in group:
        if not sentence == '':
            result = bd_nlp.parser(sentence)
            proportions['all'] = len(result['all'])
            for key in parts:
                if key in result.keys():
                    proportions[key] += len(result[key])
    return proportions


'''
文本特性3：给定一段文本，给出其流利程度（分句）
'''


def fluency(text):
    result = 0
    group = divide_text_to_sentence(text)
    for temp in group:
        if not temp == '':
            result += bd_nlp.smooth_of_text(temp) * len(temp)
            time.sleep(0.1)
    if not len_without_punctuation(text) == 0:
        return 0
    return result / len_without_punctuation(text)


'''
文本特性4：给定一段文本和一个标准答案，给出其相似程度得分（分字节数）
'''


def similarity(text, standard):
    result = bd_nlp.similar_of_texts(text, standard)
    if len(text) == 0:
        return 0
    return result


'''
文本特性5：给定一段文本，给出其情感倾向，以及积极占比和消极占比）
'''


def classify(text):
    result = bd_nlp.text_classify(text)
    return result


'''
文本特性6：给定一段文本，给出其对话情绪（分句）
'''


def emotion(text):
    pessimistic, neutral = 0, 0
    group = divide_text_to_sentence(text)
    for temp in group:
        result = bd_nlp.emotion(temp)
        pessimistic += result['pessimistic'] * len(temp)
        neutral += result['neutral'] * len(temp)
    if len_without_punctuation(text) == 0:
        return {
            'pessimistic': 0,
            'neutral': 0
        }
    return {
        'pessimistic': pessimistic / len_without_punctuation(text),
        'neutral': neutral / len_without_punctuation(text)
    }


'''
文本特性7：给定一段文本，给出其在特定词库上的踩点率（相同）
'''


def words(text, answers):
    n = 0
    for answer in answers:
        if answer in text:
            n += 1
    return n


'''
文本特性7.1：给定一段文本，给出其在特定词库上的踩点率（谐音）
'''


def words_pronunciation(text, answers):
    hitwords = []

    for answer in answers:
        if not is_all_zh(answer) and answer in text:
            hitwords.append(answer)
        if in_pronunciation(word=answer, sentence=text):
            hitwords.append(answer)
    return hitwords


'''
文本特性8：给定一段文本，给出其在特定词库上的击中率（同义词同音词算一个）
'''


def words_hit(text, answer_groups):
    n = 0
    for answer_group in answer_groups:
        for answer in answer_group:
            if answer in text:
                n += 1
                break
    return n


'''
文本特性9：给定词汇组，给出其重复频率超过2，3，4次的词数个数
'''


def words_frequency(nouns):
    temp = {}
    result = [0, 0, 0]
    for noun in nouns:
        if noun in temp.keys():
            temp[noun] += 1
        else:
            temp[noun] = 1
    for key, value in temp.items():
        if value >= 2:
            result[0] += 1
        if value >= 3:
            result[1] += 1
        if value >= 4:
            result[2] += 1
    return tuple(result)


def group_text(text, byte_nums=400):
    size = int(byte_nums / 4)
    groups = []
    for i in range(0, len(text), size):
        groups.append(text[i:i + size])
    return groups


def divide_text_to_sentence(text):
    pattern = r',|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|’|【|】|·|！| |…|（|）|？'
    return re.split(pattern, text)


def len_without_punctuation(text):
    pattern = r',|\.|/|;|\'|`|\[|\]|<|>|\?|:|"|\{|\}|\~|!|@|#|\$|%|\^|&|\(|\)|-|=|\_|\+|，|。|、|；|‘|’|【|】|·|！| |…|（|）|？'
    return len(text) - len(re.findall(pattern, text))


if __name__ == '__main__':
    print(words_pronunciation('2011年我们签订了很多条款', ['2011', '我', '挑款']))
    # print(similarity('嗯，肯德基和麦当劳作为，嗯，当下最火的两大快餐品牌，嗯，他们都诞生于1957年，然后并且都分布在全世界110，多个国家，但是能在中',
    #                  '肯德基和麦当劳是两大餐厅巨头。很多中国人觉得肯德基比麦当劳大，但事实上，麦当劳才是世界上最大的快餐企业。'))
    # print(words_frequency(['肯德基', '肯德基']))
