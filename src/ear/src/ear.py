#!/usr/bin/env python
#coding=utf-8
#实现耳朵听的功能,install pyaudio commond:sudo apt-get install python-pyaudio
#record tools :sudo apt-get install   audacity

import sys,os
import time
import threading
import pyaudio
import numpy as np


APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir))
sys.path.append(os.path.join(APP_PATH,"sdk/"))
sys.path.append(os.path.join(APP_PATH,"util/"))


try:
    import baidu_audio
    from utils import *
    from config_helper import *
except ImportError:
    raise


class Ear:
    def __init__(self):
        self.CHUNK = 2048
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000
        #录音时长,单位秒
        self.record_seconds = 2
        self.engine = baidu_audio.BaiDuAudio()


    #录音
    def _recording(self,t=1400):
        if config.IS_DEBUG:
            print("开始录音.")
        self.audio = pyaudio.PyAudio()        
        filename = os.path.join(config.TEMP_PATH, 'output' + str(int(time.time())) + '.wav')
        wait = True  # 录音等待
        stream = ""
        try:
            stream = self.audio.open(format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.RATE,
                    input=True,output=False,
                    frames_per_buffer=self.CHUNK)
        except OSError as e:
            print("ear.py self.audio.open:",e)
        #这段代码用来判断是否有声音
        #录音阈值，正常1500，大于1500录音
        while wait:
            data = stream.read(self.CHUNK)
            audio_data = np.fromstring(data, dtype=np.short)
            temp = np.max(audio_data)
            if temp > t:
                wait = not True

        frames = [] #录制的音频流
        for i in range(0, int(self.RATE / self.CHUNK * self.record_seconds)):
            data = stream.read(self.CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        self.audio.terminate()

        if config.IS_DEBUG:
            print("录音结束.")
        wf = wave.open(filename,'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        return  filename

    def listening(self,listened_callback):
        print("calbb:",listened_callback)
        while True:
            wav_path = self._recording()
            # pcm_file = wav_to_pcm(filename)
            # print("pcm_filepath:", pcm_file)
            # voice_to_words = self.engine.stt(pcm_file)

            voice_to_words = self.engine.stt_fromwav(wav_path) #识别有问题，待解决
            check_and_delete(wav_path,60) #删除wav录音文件
            listened_callback(voice_to_words)

    def listen(self,listened_callback):
        if get_os() == os_type.windows:
            #thread.start_new_thread(self.listening,(listened_callback,))
             self.listening(listened_callback)
        elif get_os() == os_type.linux:
            self.listening(listened_callback)
            #thread.start_new_thread(self.listening,(listened_callback,))
            #threading.Thread(target=self.listening,args=(listened_callback,))
  






