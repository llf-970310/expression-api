# -*— coding: utf-8 -*-
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
