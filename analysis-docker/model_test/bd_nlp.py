# -*— coding: utf-8 -*-
from aip import AipNlp
import config

client = AipNlp(config.BD_NLP_APP_ID, config.BD_NLP_API_KEY, config.BD_NLP_SECRET_KEY)


# 20000字节 词法分析
def divide_words(text):
    if len(text) == 0:
        return {
            'all': []
        }
    result = client.lexer(text)
    if 'error_code' in result.keys():
        raise Exception('\ndevide words error \n text:%s\nError code:' % text + str(
            result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        words = {
            'all': []
        }
        items = result['items']
        for item in items:
            content = item['item']
            words['all'].append(content)
            if not item['ne'] == '':
                if 'ne' in words.keys():
                    words['ne'].append(content)
                else:
                    words['ne'] = [content]
            if not item['pos'] == '':
                temp = item['pos']
                if temp in words.keys():
                    words[temp].append(content)
                else:
                    words[temp] = [content]
    return words


# 256字节 句法分析
def parser(text):
    if len(text) == 0:
        return {
            'all': []
        }
    options = {'mode': 1}
    result = client.depParser(text, options=options)
    if 'error_code' in result.keys():
        raise Exception('\n parse text error \n text:%s\nError code:' % text + str(
            result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        words = {
            'all': []
        }
        items = result['items']
        for item in items:
            content = item['word']
            words['all'].append(content)
            postag, deprel = item['postag'], item['deprel']
            if postag in words.keys():
                words[postag].append(content)
            else:
                words[postag] = [content]
            if deprel in words.keys():
                words[deprel].append(content)
            else:
                words[deprel] = [content]
        return words


# 512字节 文本流畅度
def smooth_of_text(text):
    if len(text) == 0:
        return 0
    result = client.dnnlm(text)
    if 'error_code' in result.keys():
        raise Exception('\nsmooth of text error\ntext:%s\nError code:' % text + str(
            result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        return result['ppl']


def similar_of_words(word1, word2):
    if len(word1) == 0 or len(word2) == 0:
        return 0
    result = client.wordSimEmbedding(word1, word2)
    if 'error_code' in result.keys():
        raise Exception('\nsimilar of words error \n word1:%s,word2:%s\nError code:' % (word1, word2) + str(
            result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        return result['score']


# 512字节 文本相似度
def similar_of_texts(text1, text2):
    if len(text1) == 0 or len(text2) == 0:
        return 0
    result = client.simnet(text1, text2)
    if 'error_code' in result.keys():
        if result['error_code'] == 282301 or result['error_code'] == 282302 or result['error_code'] == 28303:
            return 0
        else:
            raise Exception('\nsimilar of texts error \n text1:%s,text2:%s\nError code:' % (text1, text2) +
                            str(result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        return result['score']


# 2048字节 情感倾向
def text_classify(text):
    if len(text) == 0:
        return {
            'positive': 0,
            'negative': 0,
            'sentiment': 'neutral'
        }
    result = client.sentimentClassify(text)
    if 'error_code' in result.keys():
        raise Exception('\ntext classify error \n text:%s\nError code:' % text + str(
            result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        sentiment = result['items'][0]
        return {
            'positive': sentiment['positive_prob'],
            'negative': sentiment['negative_prob'],
            'sentiment': ['negative', 'neutral', 'positive'][sentiment['sentiment']]
        }


# 65535字节 文本关键词
def label_of_article(content, title='0'):
    if len(content) == 0:
        return ''
    result = client.keyword(title, content)
    if 'error_code' in result.keys():
        raise Exception('\nlabel of article error \n title:%s,content:%s\nError code:' % (content, title) + str(
            result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        return result['items']


# 511字节 文本错误数量，基本不可用
def wrongs_of_text(text):
    if len(text) == 0:
        return 0
    result = client.ecnet(text)
    if 'error_code' in result.keys():
        raise Exception('\nerror of article \n text: %s\nError code:' % text + str(
            result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        return len(result['item']['vec_fragment'])


# 512字节 文本对话情绪
def emotion(text):
    if len(text) == 0:
        return {
            'pessimistic': 0,
            'neutral': 0
        }
    result = client.emotion(text)
    if 'error_code' in result.keys():
        raise Exception('\nerror of article \n text: %s\nError code:' % text + str(
            result['error_code']) + '\nError Message:' + result['error_msg'])
    else:
        return {
            'pessimistic': result['items'][1]['prob'],
            'neutral': result['items'][0]['prob']
        }


if __name__ == '__main__':
    # print(divide_words(''))
    print(divide_words('我想吃饭'))
    # print(smooth_of_text('我想吃饭'))
    # print(similar_of_texts('的', '麦当劳'))
    # print(text_classify('我不想吃饭'))
    # print(label_of_article(
    #     '肯德基和麦当劳是世界快餐巨头。肯德基诞生于1952年，由创始人哈兰·山德士创建，'
    #     '在世界上115个国家和地区开设有18000多家肯德基餐厅，肯德基在1987 年进入中国，收到广大消费者的喜欢。麦当劳，1955年创立于美国芝加哥，在中国大陆早期译名是“麦克唐纳快餐”，'
    #     '直到后期才统一使用现在的名字。麦当劳遍布全球六大洲119个国家，在很多国家代表着一种美式生活方式。'
    #     '在中国，因为肯德基要比麦当劳更受欢迎，很多人会觉得肯德基是世界上最大的餐饮企业，但其实麦当劳才是。麦当劳在世界上拥有3万多家门店，而肯德基的门店数量只是拥麦当劳的三分之一。'))
