#!/usr/bin/env python
#!coding=utf-8
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

import requests
import json
import os


class QQmusic:
    def __init__(self,music_path = ""):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}
        if len(music_path) >0:
            self.download_filepath = music_path
        else:
            self.download_filepath = APP_PATH =os.path.normpath(os.path.join(
                os.path.abspath(__file__), os.pardir))
        self.sl = []
        self.musicList = []
        self.mp3Dic = dict()
        self.init_musiclist()
    
    def init_musiclist(self):
        print("self.download_filepath-->",self.download_filepath)
        for i in os.listdir(self.download_filepath):
            path = os.path.join(self.download_filepath,i)
            if os.path.isdir(path):
                break
            else:
                if i.endswith((".mp3",)):                    
                    item = {i:path}
                    #item = {i.encode('utf8'):path}
                    self.mp3Dic.update(item)
                    #s1 = '\xe8\xae\xa9\xe6\x88\x91\xe4\xbb\xac\xe8\x8d\xa1\xe8\xb5\xb7\xe5\x8f\x8c\xe6\xa1\xa8.mp3'
                    #print("self.mp3Dic.get(s1,None)",self.mp3Dic.get(s1,None) is None)

    # 获取页面
    def _getPage(self,url,headers):
        res = requests.get(url,headers = headers)
        res.encoding = 'utf-8'
        return res

    # 获取音乐songmid
    def _getSongmid(self,num=1,name="世间始终你最好"):
        url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?p=1&n=%d&w=%s'%(num,name)
        # 搜索音乐
        res = self._getPage(url,headers=self.headers)
        html = res.text
        html = html[9:]
        html = html[:-1]
        # 获取songmid
        js = json.loads(html)
        songlist = js['data']['song']['list']
        for song in songlist:
            print(song)
            songmid = song['songmid']
            name = song['songname']
            self.sl.append((name,songmid))
            print('获取成功songmid')


    # 获取音乐资源，guid是登录后才能获取，nin也是
    def _getVkey(self):
        guid = "3481851020"
        uin = "27281729"
        for s in self.sl:
            print('开始获取资源')
            # 获取vkey,purl
            name = s[0]
            songmid = s[1]
            keyUrl = 'https://u.y.qq.com/cgi-bin/musicu.fcg?&data={"req":{"param":{"guid":" %s"}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"%s","songmid":["%s"],"uin":"%s"}},"comm":{"uin":%s}}'%(guid,guid,songmid,uin,uin)
            res = self._getPage(keyUrl,headers=self.headers)
            html = res.text
            keyjs = json.loads(html)
            purl = keyjs['req_0']['data']['midurlinfo'][0]['purl']
            # 拼凑资源url
            url = 'http://dl.stream.qqmusic.qq.com/' + purl
            self.musicList.append((name,url))
            print('资源地址获取成功')

    #   下载音乐
    def _downloadMusic(self,download_callback):
        for m in self.musicList:
            url = m[1]
            res = self._getPage(url,headers=self.headers)
            music = res.content
            name = m[0] + '.m4a'
            music_full_path = os.path.join(self.download_filepath,name)
            with open(music_full_path, 'wb') as f:
                f.write(music)
                print('下载OK')
                f.closed
            mp3 = self.m4a_to_mp3(self.download_filepath,name)
            if download_callback is not None:
                if os.path.exists(mp3):
                    item = {name:mp3}
                    self.mp3Dic.update(item) #add mp3Dic                    
                    download_callback(mp3)
                else:
                    download_callback("")
    def m4a_to_mp3(self,m4a_path,m4a):
        r_index = m4a.rindex(".")
        mp3_file = "%s.mp3" %(m4a[0:r_index])

        m4a_fpath = os.path.join(m4a_path,m4a)
        mp3_fpath = os.path.join(m4a_path,mp3_file)
        print("m4a_fpath-->",m4a_fpath)
        print("mp3_fpath-->",mp3_fpath)

        os.system("ffmpeg -i " +m4a_fpath + " " +mp3_fpath)
        return mp3_fpath

    def download_music(self,num,name,download_callback=None):
        self._getSongmid(num,name)
        self._getVkey()
        self._downloadMusic(download_callback)

    def get_muisc(self,name,download_callback=None):
        name = name+".mp3"
        print("len self.mp3Dic",len(self.mp3Dic))
        print("play name-->",name)
        print("self.mp3Dic.get(name,None) is None-->",self.mp3Dic.get(name,None) is None)
        if self.mp3Dic.get(name,None) is None:
            self.download_music(1,name,download_callback)
        else:
            download_callback(self.mp3Dic.get(name))
        print("len self.mp3Dic",len(self.mp3Dic))

APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), os.pardir))

if __name__ == '__main__':  
    path = "/home/y1robot/y3robot_ws/src/downloads/music" 
    QQ = QQmusic(path)
    #QQ.set_download_filepath("/home/y1robot/y3robot_ws/src/mouth/src/downloads/music")
    for k,v in QQ.mp3Dic.items():
        print(k+":"+v)
    #QQ.m4a_to_mp3('/home/y1robot/y3robot_ws/src/downloads/music','中国人.m4a')
  
    #QQ.set_download_filepath(os.path.join(APP_PATH,"downloads/music/"))
    #QQ.download_music(1,"我爱你中国")
