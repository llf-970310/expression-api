#!/usr/bin/env python3
# coding: utf-8
#
# Created by dylanchu on 18-7-25

import glob
import logging
import os
import wave
import numpy as np
import webrtcvad
import io

translation_dict = {
    'num': '字数',
    'last_time': '长度',
    'interval_num': '时间间隔数量',
    'interval_ratio': '时间间隔比率',
    'clr_ratio': '清晰度',
    'ftl_ratio': '无效表达比率',
    'cpl_ratio': '完成度',
    'phone_score': '声韵分',
    'fluency_score': '流畅度分',
    'tone_score': '调型分',
    'integrity_score': '完整度分',
    'main_idea_similarity': '主旨相似度',
    'n_ratio': '普通名词占比',
    'v_ratio': '普通动词占比',
    'vd_ratio': '动副词占比',
    'vn_ratio': '动名词占比',
    'a_ratio': '形容词占比',
    'ad_ratio': '副形词占比',
    'an_ratio': '名形词占比',
    'd_ratio': '副词占比',
    'm_ratio': '数量词占比',
    'q_ratio': '量词占比',
    'r_ratio': '代词占比',
    'p_ratio': '介词占比',
    'c_ratio': '连词占比',
    'u_ratio': '助词占比',
    'xc_ratio': '其他虚词占比',
    'w_ratio': '标点符号占比',
    'ne_ratio': '专有名词占比',
    'word_num': '总词数',
    'noun_frequency_2': '名词重复词数超过2个',
    'noun_frequency_3': '名词重复词数超过3个',
    'noun_frequency_4': '名词重复词数超过4个',
    'classA_ratio': '一级词库词占比',
    'classB_ratio': '二级词库词占比',
    'classA_hit_count': '一级词库击中次数',
    'classB_hit_count': '二级词库击中次数',
    'classA_ratio_30': '前30s一级词库词占比',
    'classB_ratio_30': '前30s二级词库占比',
    'classA_hit_count_30': '前30s一级词库击中次数',
    'classB_hit_count_30': '前30s二级词库击中次数',
    'deduct_count': '减分词库词量',
    'deduct_num': '减分词库词量',
    'detail_time_hit_count': '时间类细节关键词击中次数',
    'detail_name_hit_count': '名称类细节关键词击中次数',
    'detail_num_hit_count': '数字类细节关键词击中次数',
    'detail_m_hit_count': '地名类细节关键词击中次数',
    'detail_store_hit_count': '店名类细节关键词击中次数',
    'detail_welcome_hit_count': '欢迎程度细节关键词击中次数',
    'detail_speed_hit_count': '速度细节关键词击中次数',
    'detail_on_time_hit_count': '准时细节关键词击中次数',
    'detail_comfortable_hit_count': '舒适细节关键词击中次数',
    'detail_cost_hit_count': '成本细节关键词击中次数',
    'speed1': '第一段语速',
    'speed2': '第二段语速',
    'speed3': '第三段语速',
    'speed': '平均语速',
    'speed_deviation': '语速标准差',
    'volume1': '第一段音量',
    'volume2': '第二段音量',
    'volume3': '第三段音量',
    'sentence_num': '句子数',
    'fluency_baidu_sum': '通顺值总分',
    'sum-aspects_num': '总分词库词数量',
    'aspects_num': '分点词库词数量',
    'example_num': '举例词库词数量',
    'opinion_num': '亮观点词库词数量',
    'sum_num': '总结词库词数量',
    'classA_num': '高级词库词数量',
    'cause-affect_num': '因果词库数量',
    'transition_num': '转折词库数量',
    'progressive_num': '递进词库数量',
    'parallel_num': '并列词库数量',

    'tone-quality': '音调分',
    'main-idea': '主旨分',
    'detail': '细节分',
    'structure': '结构分',
    'logistic': '逻辑分',
    'total-score': '总分'
}


def check_wav_format(wav_file, valid_framerate=8000):
    if isinstance(wav_file, io.BytesIO):
        wav_file.seek(0)  # seek(0) before read
    with wave.open(wav_file, 'rb') as f:
        params = f.getparams()  # file header, return tuple
        logging.info(params)
        nchannels, sampwidth, framerate, nframes = params[:4]
    if nchannels != 1:
        logging.warn("---- THE WAV FILE IS NOT MONOPHONIC, MAYBE NOT SUPPORTED BY XUNFEI API!! ----")
    if framerate != valid_framerate:
        logging.warn("---- THE FRAMERATE IS %d !! ----" % framerate)


def check_video_count(folder_path):
    videos = glob.glob(folder_path + "/*.m4v")
    videos2 = glob.glob(folder_path + "/*.MOV")
    videos.extend(videos2)
    videos.sort()
    if len(videos) != 4:
        logging.warn("---- Caution: not 4 videos in %s !! ----" % folder_path)
        # raise Exception("---- Caution: not 4 videos in %s !! ----" % folder_path)


def extract_wav_files(from_folder, **kwargs):
    to_folder = kwargs.get('to_folder')
    if not to_folder:
        to_folder = from_folder
    videos = glob.glob(from_folder + "/*.m4v")
    videos2 = glob.glob(from_folder + "/*.MOV")
    videos.extend(videos2)
    videos.sort()
    logging.info(videos)
    if len(videos) == 4:
        if not os.path.exists(to_folder):
            os.system('mkdir -p "%s"' % to_folder)
        if not has_program('ffmpeg'):
            raise Exception('No ffmpeg found in PATH. Please Install ffmpeg first.')
        # os.system('rm -f "%s/[1-5].wav"' % to_folder)
        # os.system('ffmpeg -i "%s" -ss 0 -t 60 -f wav -ar 16000 -y "%s/1.wav" > /dev/null' % (videos[0], to_folder))
        for i in range(0, 4):
            os.system('ffmpeg -i "%s" -f wav -ar 8000 -y "%s/1.wav" > /dev/null 2>&1' % (videos[i], to_folder))
    else:
        logging.warn("---- NOT PROCESSED: not 4 videos, please check it! FOLDER: %s ----" % from_folder)


def save_wave_file(filename, data, framerate=8000):
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(framerate)
        if isinstance(data, np.ndarray):
            wf.writeframes(data.tobytes())
        else:
            wf.writeframes(b"".join(data))


def wav_8kto16k(wav_file, new_file_path):
    """ input wav file must be mono, 8k/16k """
    if isinstance(wav_file, io.BytesIO):
        wav_file.seek(0)  # seek(0) before read
    with wave.open(wav_file, 'rb') as f:
        params = f.getparams()  # file header, return tuple
        nchannels, sampwidth, framerate, nframes = params[:4]
        if framerate != 16000 and framerate != 8000 or nchannels != 1:
            raise Exception('RESAMPLE: Input file error: Wrong framerate or Stereo!')
        data_str = f.readframes(nframes)
        # save wav data as numpy array
        wave_data = np.fromstring(data_str, dtype=np.short)
    if framerate == 8000:
        x = np.linspace(0, nframes, nframes, False)
        xx = np.linspace(0, nframes, nframes * 2, False)
        wave_data = np.array(np.interp(xx, x, wave_data), dtype=np.short)
    with wave.open(new_file_path, 'wb') as wf:
        wf.setnchannels(nchannels)
        wf.setsampwidth(sampwidth)
        wf.setframerate(16000)
        wf.writeframes(wave_data.tobytes())


def find_and_remove_intervals(wav_file, new_wave_file_path=None, threshold=0.4):
    """ support 8k, 16k, 32k framerate, mono audio """
    intervals_lst = list()
    vad = webrtcvad.Vad()
    vad.set_mode(2)
    duration = 20  # ms
    _MAX_SILENCE_CHUNKS = threshold * 1000 // duration  # 0.4s/20ms = 20

    if isinstance(wav_file, io.BytesIO):
        wav_file.seek(0)  # seek(0) before read
    with wave.open(wav_file, 'rb') as f:
        params = f.getparams()  # file header, return tuple
        nchannels, sampwidth, framerate, nframes = params[:4]
        frame_count = int(framerate * duration / 1000)
        valid_len = 2 * frame_count  # 16bit -> 2B

        stats = 0
        # binarized_chunks = list()
        chunk = f.readframes(frame_count)
        chunk_num = 1
        if new_wave_file_path is not None:
            new_wf_frames = np.frombuffer(chunk, dtype=np.int16)  # new wave file data
        while len(chunk) == valid_len:
            contains_speech = vad.is_speech(chunk, framerate)
            # binarized_chunks.append(int(contains_speech))

            """ make intervals list and copy new wave file frames """
            if contains_speech:
                if stats != 0:
                    intervals_lst.append((round((chunk_num - stats) * 0.02, 2), round((stats * 0.02), 2)))
                    stats = 0
                if new_wave_file_path is not None:
                    new_wf_frames = np.append(new_wf_frames, np.frombuffer(chunk, dtype=np.int16))
            else:
                stats += 1
                if stats < _MAX_SILENCE_CHUNKS and new_wave_file_path is not None:
                    new_wf_frames = np.append(new_wf_frames, np.frombuffer(chunk, dtype=np.int16))

            chunk = f.readframes(frame_count)
            chunk_num += 1
        else:
            if new_wave_file_path is not None:
                new_wf_frames = np.append(new_wf_frames, np.frombuffer(chunk, dtype=np.int16))
        # logging.debug(binarized_chunks)
        if new_wave_file_path is not None:
            save_wave_file(new_wave_file_path, new_wf_frames)
    return intervals_lst


def auto_magnify_audio(wav_file, new_wav_file_path=None):
    """ support 16bit audio """
    if isinstance(wav_file, io.BytesIO):
        wav_file.seek(0)  # seek(0) before read
    with wave.open(wav_file, 'rb') as f:
        params = f.getparams()  # file header, tuple
        nchannels, sampwidth, framerate, nframes = params[:4]
        data_bytes = f.readframes(nframes)
        wf_data = np.frombuffer(data_bytes, dtype=np.int16)
        mx = np.max(np.abs(wf_data))
        # ratio = (32768 // mx)  # value is signed type
        ratio = (30000 // mx)  # value is signed type
        if new_wav_file_path is not None:
            if ratio >= 2:
                logging.debug("Current max amplitude: %s, the audio can be magnified %sx." % (mx, ratio))
                wf_data = wf_data * ratio
                logging.debug("New max amplitude: %s" % np.max(wf_data))
                logging.info("Audio amplitude magnified by %sx. Now saving new file..." % ratio)
            with wave.open(new_wav_file_path, 'wb') as nf:
                nf.setnchannels(nchannels)
                nf.setsampwidth(sampwidth)
                nf.setframerate(framerate)
                nf.writeframes(wf_data.tostring())
        return ratio


def list_to_sheet(sheet, obj):
    if not excel_check(obj):
        raise Exception('This object cannot be written into an Excel file.')
    else:
        sheet.write(0, 0, '#')
        keys = list(obj[0].keys())
        for i in range(len(keys)):
            sheet.write(0, i + 1, translation_dict[keys[i]])
        for i in range(len(obj)):
            sheet.write(i + 1, 0, i + 1)
            for j in range(len(keys)):
                value = obj[i][keys[j]]
                sheet.write(i + 1, j + 1, value)
        return sheet


def has_program(program_name):
    has_cmd = False
    for path in os.environ['PATH'].split(':'):
        if os.path.isdir(path) and program_name in os.listdir(path):
            has_cmd = True
            break
    return has_cmd


def excel_check(obj):
    if not isinstance(obj, list):
        return False
    for i in range(len(obj) - 1):
        keys1 = obj[i].keys()
        keys2 = obj[i + 1].keys()
        if not keys1 == keys2:
            return False
    return True


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
                    sd.append((word_count, duration / 100))
                duration = 0
                word_count = 0
    return sd


def read(target, mode='r'):
    if isinstance(target, io.StringIO) or isinstance(target, io.BytesIO):
        return target.getvalue()
    else:
        with open(target, mode) as f:
            return f.read()


def write(target, content, mode='w'):
    if isinstance(target, io.StringIO) or isinstance(target, io.BytesIO):
        return target.write(content)
    else:
        with open(target, mode) as f:
            return f.write(content)


def get_audio_length(wav_file):
    if isinstance(wav_file, io.BytesIO) or isinstance(wav_file, io.StringIO):
        wav_file.seek(0)  # seek(0) before read
    with wave.open(wav_file, 'rb') as wav:
        return wav.getnframes() / wav.getframerate()
