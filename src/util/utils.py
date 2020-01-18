#!/usr/bin/env python
#coding=utf-8
import platform
import shutil
import  wave
import os
import hashlib
import time
import yaml
import sys
from threading import Thread

reload(sys)
sys.setdefaultencoding('utf8')

APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir))
TEMP_PATH = os.path.join(APP_PATH, "Temp")

try:
    sys.path.append(os.path.join(APP_PATH,"sdk/"))
    sys.path.append(os.path.join(APP_PATH,"util/"))
except ImportError:
    raise


class os_type:
    windows="Windows"
    linux="Linux"
    unknow="Unknow"

def get_os():
    sys = platform.system()
    if sys == os_type.windows:
        return os_type.windows
    elif sys == os_type.linux:
        return  os_type.linux
    else:
        return  os_type.unknow


def get_pcm_from_wav(wav_path):
    """
    从 wav 文件中读取 pcm

    :param wav_path: wav 文件路径
    :returns: pcm 数据
    """
    print("wav_path:",wav_path)
    wav = None
    try:
        wav = wave.open(wav_path, 'rb')
    except Exception as e:
        print("wav_path:",wav_path)
    if wav is not None:
        return wav.readframes(wav.getnframes())
    else:
        return wav


def wav_to_pcm(wav_file):
    # 假设 wav_file = "音频文件.wav"
    # wav_file.split(".") 得到["音频文件","wav"] 拿出第一个结果"音频文件"  与 ".pcm" 拼接 等到结果 "音频文件.pcm"
    fullpath = os.path.abspath(wav_file)
    #wav_filepath = os.path.splitext(fullpath)
    r_index = fullpath.rindex(".")
    pcm_file = "%s.pcm" %(fullpath[0:r_index])
    # 就是此前我们在cmd窗口中输入命令,这里面就是在让Python帮我们在cmd中执行命令
    os.system("ffmpeg -y  -i %s  -acodec pcm_s16le -f s16le -ac 1 -ar 16000 %s"%(fullpath,pcm_file))
    return pcm_file

def getCache(msg):
    """ 获取缓存的语音 """
    print("from cache get msg voice")
    md5 = hashlib.md5(msg.encode('utf-8')).hexdigest()
    mp3_cache = os.path.join(TEMP_PATH, md5 + '.mp3')
    wav_cache = os.path.join(TEMP_PATH, md5 + '.wav')
    if os.path.exists(mp3_cache):
        return mp3_cache
    elif os.path.exists(wav_cache):
        return wav_cache
    return None

def saveCache(voice, msg):
    """ 获取缓存的语音 """
    foo, ext = os.path.splitext(voice)
    md5 = hashlib.md5(msg.encode('utf-8')).hexdigest()
    target = os.path.join(TEMP_PATH, md5+ext)
    shutil.copyfile(voice, target)
    return target


def check_and_delete(fp, wait=0):
    """
    检查并删除文件/文件夹
    :param fp: 文件路径
    """

    def run():
        if wait > 0:
            time.sleep(wait)
        if isinstance(fp, str) and os.path.exists(fp):
            if os.path.isfile(fp):
                os.remove(fp)
            else:
                shutil.rmtree(fp)

    #thread.start_new_thread(run, ()) 
    new_thread = Thread(target=run) 
    new_thread.start()

def getHotwordModel(filepath,fname):
    full_path = os.path.join(filepath, *fname)
    print("full_path-->",full_path)
    if os.path.exists(full_path):
        return full_path
    else:
        return None

