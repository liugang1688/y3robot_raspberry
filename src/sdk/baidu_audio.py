#!/usr/bin/env python
#coding=utf-8
# -*- coding: utf-8 -*-
import os
import sys



from aip import AipSpeech

APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.append(os.path.join(APP_PATH,"sdk/"))
sys.path.append(os.path.join(APP_PATH,"util/"))


try:
    from config_helper import config
    from utils import *
except ImportError:
    raise

#first,install baidu api use commond :pip install baidu-aip

# 发音者
class SPEEKER:
    XIAOMEI = 0
    XIAOYU = 1
    XIAOYAO = 3
    YAYA = 4


# 百度语音封装
class BaiDuAudio:
    APP_ID =config.APP_ID # '17971491'
    API_KEY = config.API_KEY # 'lDeumTi8MzVlITqsl7OG0Wn0'
    SECRET_KEY = config.SECRET_KEY #'wmb2PR0xk9IzfP6dfOhEhYIOvvoZzXLn'
    DEV_PID = config.DEV_PID #"1536" #1536	普通话(支持简单的英文识别) 1537	普通话(纯中文识别)



    # 度小宇 = 1，度小美 = 0，度逍遥 = 3，度丫丫 = 4
    # 精品音库 度博文 = 106，度小童 = 110，度小萌 = 111，度米朵 = 103，度小娇 = 5

    # 初始化
    def __init__(self):
        self.client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    # 文本转语音
    def tts(self, words, audioName=config.SPEECH_OUTPUT_PATH):
        result = self.client.synthesis(words, 'zh', 1, {
            'vol': 5, 'per': config.BAIDU_PER
        })

        # 合成正确返回.mp3，错误则返回dict
        if not isinstance(result, dict):
            full_path = os.path.join(APP_PATH,audioName)
            with open(full_path, 'wb') as f:
                f.write(result)
            f.close()
            return full_path

    # 获取语音文件stream
    def __get_file_content(self,filePath):
        with open(filePath,'rb') as fp:
            return fp.read()

    # 语音转文本
    def stt(self, pcm_file_Path = config.SPEECH_INPUT_PATH):
        out_words = ""
        if os.path.exists(pcm_file_Path):
            res = self.client.asr(self.__get_file_content(pcm_file_Path), 'pcm', 16000, {
                'dev_pid': self.DEV_PID,
            })
            if res['err_msg'] == 'success.':
                out_words = res.get("result")[0]
            else:
                print(res)
        else:
            if config.IS_DEBUG:
                print("baiduAudio转换语音文件不存在:",pcm_file_Path)
        return  out_words

    def stt_fromwav(self,fp):
        out_words = ''
        pcm = get_pcm_from_wav(fp)
        res = self.client.asr(pcm, 'pcm', 16000, {
                'dev_pid': self.DEV_PID,
            })
        
        if res['err_msg'] == 'success.':
            out_words = res.get("result")[0]
        else:
            print(res)
        return out_words
