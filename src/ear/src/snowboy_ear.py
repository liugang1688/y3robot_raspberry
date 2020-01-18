#!/usr/bin/env python
#coding=utf-8

import sys,os
import time
import signal
from voice_record import VoiceRecord

APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir))
sys.path.append(os.path.join(APP_PATH,"sdk/"))
sys.path.append(os.path.join(APP_PATH,"util/"))
sys.path.append(os.path.join(APP_PATH,"snowboy/"))

try:
    import baidu_audio 
    from config_helper import *
    from utils import *
    import snowboydetect
    import snowboydecoder
except ImportError:
    raise
class Ear:
    def __init__(self):
        self.detector = None
        self._listened_callback = None
        self._interrupted = False
        self._voice_record = VoiceRecord()
        self.engine = baidu_audio.BaiDuAudio()


    def _signal_handler(self,signal, frame):
        self._interrupted = True

    def _interrupt_callback(self):
        return self._interrupted
    def _passive_callback(self):
         if self._listened_callback  is not None:     
            self._listened_callback("ear_status:0")
    def _detected_callback(self):
        self._voice_record.listening(self._listened_callback)
   
    def _snowboy_record_callback(self,fp, callback = None):
        voice_to_words = self.engine.stt_fromwav(fp) #识别有问题，待解决  
        #check_and_delete(fp,60) #删除wav录音文件 
        print("voice_to_words-->",voice_to_words)
        if self._listened_callback  is not None:     
            self._listened_callback(voice_to_words)

    def initDetector(self):
        if self.detector is not None:
            self.detector.terminate() 
        #print("snowboy_path:",os.path.join(APP_PATH,"snowboy/"))       
        #print("hotword:",config.SNOWBOY_HOTWORD)
        models = getHotwordModel(os.path.join(APP_PATH,"snowboy/"),(config.SNOWBOY_HOTWORD,))
        #print("models-->:",models)
        self.detector = snowboydecoder.HotwordDetector(models, sensitivity=config.SNOWBOY_SENSITIVITY)
        try:                        
            self.detector.start(            
            detected_callback=self._detected_callback,
            audio_recorder_callback=None,
            #self._snowboy_record_callback,
            interrupt_check= self._interrupt_callback,
            silent_count_threshold=config.SNOWBOY_SILENT_THRESHOLD ,
            recording_timeout=config.SNOWBOY_RECORDING_TIMEOUT * 4,
            sleep_time=0.03,
            passive_callback = self._passive_callback
	)
            self.detector.terminate()
        except Exception as e:
            print('离线唤醒机制初始化失败：{}'.format(e))

    def listen(self,listened_callback):
        if self._listened_callback is None:
            self._listened_callback = listened_callback         
        signal.signal(signal.SIGINT, self._signal_handler)
        print("listen main loop")
        self.initDetector()    


