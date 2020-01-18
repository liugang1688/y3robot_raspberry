#!/usr/bin/env python
#coding=utf-8
import os
import sys
import time
import qqmusic

import rospy
from threading import Thread
from pygame import mixer


APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir))
sys.path.append(os.path.join(APP_PATH,"sdk/"))
sys.path.append(os.path.join(APP_PATH,"util/"))




try:
    import utils
    import baidu_audio
except ImportError:
    raise

class Mouth():
    def __init__(self):
        self.machine_wav =  full_path = os.path.join(APP_PATH,"audio/bullet.wav")
        self.engine = baidu_audio.BaiDuAudio()
        self.music_manager = qqmusic.QQmusic(os.path.join(APP_PATH,"downloads/music/"))       
        self._mouth_threading = None
        self._hasMsg = False
        self._mgs_is_words = True
        self.msg = ""
        mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        mixer.music.set_volume(0.5)

    def play_music(self,msg):
        self.music_manager.get_muisc(msg,self.syn_playAudio)
    def syn_playAudio(self,audioFilePath):
        if len(audioFilePath) >0:
            self.say(audioFilePath,False,False)
        else:
            self.say("下载音乐失败",True,True)

    def playAudio(self,audioFilePath):
        print("start play audio")
        while self.__get_busy():
            time.sleep(0.1)
        print("play file path-->",audioFilePath)
        mixer.music.load(audioFilePath)
        mixer.music.play()

        
        #等待音频播放结束
        while self.__get_busy():
            time.sleep(0.1)
        mixer.music.load(self.machine_wav)  # 使用pygame加载一个别的音频，释放掉audioFilePath，不然权限出错
        time.sleep(0.1)
        

    def __get_busy(self):
        return mixer.music.get_busy()
    #说文字
    def say(self,msg,mgs_is_words=True,is_ending_saying=False):
        print("mouth start say:",msg)
        if len(msg)>0 :
            self._hasMsg = True
            self.msg = msg
            self._mgs_is_words = mgs_is_words

            print("is_ending_saying-->",is_ending_saying)
            print(" self._mouth_threading-->", self._mouth_threading)
            if self._mouth_threading is None: #如果当前没有线程则启动新线程
                self._mouth_threading = Thread(target=self._speak)
                self._mouth_threading.start()
            elif is_ending_saying and self._mouth_threading is not None:                                
                mixer.stop()
                mixer.music.stop()
                print("mixer.stop-->")
            else:
                pass


    def _speak(self):
        while True:
            if self._hasMsg:
                print("_speak->>")
                self._hasMsg = False
                msg = self.msg
                cache_path = ''
                if self._mgs_is_words:
                    if utils.getCache(msg):
                        print("命中缓存，播放缓存语音")
                        voice = utils.getCache(msg)
                        cache_path = utils.getCache(msg)
                    else:
                        try:
                            voice = self.engine.tts(msg)
                            cache_path = utils.saveCache(voice, msg)
                        except Exception as e:
                            print(e)
                    if len(cache_path) > 0:
                        self.playAudio(cache_path)
                else:
                    self.playAudio(msg)
            time.sleep(0.1)



if __name__ == '__main__':   
    m = Mouth()
    m.playAudio("/home/y1robot/y3robot_ws/src/downloads/music/12.mp3")
    m.say("stop",True)
