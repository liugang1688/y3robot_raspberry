#!/usr/bin/env python
#coding=utf-8
#配置文件
import  os
import yaml
from utils import *
import sys
reload(sys)
sys.setdefaultencoding('utf8')

has_init = False
_config = {}
def _init(config_file=os.path.join(APP_PATH, "default.yaml")):
    # Read config
    # logger.debug("Trying to read config file: '%s'", config_file)
    global _config
    global has_init
    try:
        with open(config_file,'r') as f:
            _config = yaml.safe_load(f)
        has_init = True
    except Exception as e:
        # logger.error("配置文件 {} 读取失败: {}".format(config_file, e))
        pass
        raise

def get(item='', default=None):
    """
    获取某个配置的值

    :param item: 配置项名。如果是多级配置，则以 "/a/b" 的形式提供
    :param default: 默认值（可选）
    :returns: 这个配置的值。如果没有该配置，则提供一个默认值
    """
    global _config
    global has_init

    if not has_init:
        _init()
    if not item:
        return _config
    if item[0] == '/':
        return get_path(item, default)
    try:
        return _config[item]
    except KeyError:
        print("%s not specified in profile, defaulting to '%s'",item, default)
        return default

def get_path(items, default=None):

    global _config
    curConfig = _config
    if isinstance(items, str) and items[0] == '/':
        items = items.split('/')[1:]
    for key in items:
        if key in curConfig:
            curConfig = curConfig[key]
        else:
            # logger.warning("/%s not specified in profile, defaulting to "
            #                "'%s'", '/'.join(items), default)
            return default
    return curConfig

class config:
    IS_DEBUG = True  # 是否调试
    APP_PATH = os.path.normpath(os.path.join(
        os.path.dirname(os.path.abspath(__file__)), os.pardir))
    
    START_AUDIO = get("/configs/myrobot/START_RECORD_PATH")
    SPEECH_OUTPUT_PATH = get("/configs/baiduApi/voice/SPEECH_OUTPUT_PATH")
    SPEECH_INPUT_PATH = get("/configs/baiduApi/voice/SPEECH_INPUT_PATH")
    START_RECORD_PATH = get("/configs/myrobot/START_RECORD_PATH")
    TEMP_PATH = os.path.join(APP_PATH, "Temp")

    SNOWBOY_HOTWORD = get('/configs/snowboy/hotword')
    SNOWBOY_SENSITIVITY = get('/configs/snowboy/sensitivity')
    SNOWBOY_RECORDING_TIMEOUT = get('/configs/snowboy/recording_timeout')
    SNOWBOY_SILENT_THRESHOLD = get('/configs/snowboy/silent_threshold')
    

    APP_ID = get('/configs/baiduApi/APP_ID')  # '17971491'
    API_KEY = get('/configs/baiduApi/API_KEY')  # 'lDeumTi8MzVlITqsl7OG0Wn0'
    SECRET_KEY = get('/configs/baiduApi/SECRET_KEY')  # 'wmb2PR0xk9IzfP6dfOhEhYIOvvoZzXLn'
    DEV_PID = get('/configs/baiduApi/DEV_PID')  # "1536" #1536	普通话(支持简单的英文识别) 1537	普通话(纯中文识别)
    BAIDU_PER =  get('/configs/baiduApi/per')

    ROBOT_ID =  get('/configs/baiduApi/ROBOT/ID')
    ROBOT_API_KEY = get('/configs/baiduApi/ROBOT/API_KEY')
    ROBOT_SECRET_KEY = get('/configs/baiduApi/ROBOT/SECRET_KEY')
    UNIT_TOKEN = None


'''
module_name, 模块
package_name, 包
ClassName, 类
method_name, 方法
ExceptionName, 异常
function_name, 函数
GLOBAL_VAR_NAME, 全局变量
instance_var_name, 实例
function_parameter_name, 参数
local_var_name. 本变量

快捷键
Ctrl+/:代码注释

#Python 函数注释 https://blog.csdn.net/liang19890820/article/details/74264380

函数
string: 

partition rpartition:  目标字符串的末尾也就是右边开始搜索分割符 
如果字符串包含指定的分隔符，则返回一个3元的元组，第一个为分隔符左边的子串，第二个为分隔符本身，第三个为分隔符右边的子串
join:方法用于将序列中的元素以指定的字符连接生成一个新的字符串,用法:"-".join("a","txt") 结果"a.txt"

lstrip() 方法用于截掉字符串左边的空格或指定字符。

format tools:autopep8


rosrun rqt_console rqt_console

rosrun rqt_graph rqt_graph


rostopic pub /brain_say std_msgs/String -'this is new topic message' 
 rostopic pub //brain_say std_msgs/String -r 1 'this is new topic message' 


custom message see this url:https://blog.csdn.net/NiYintang/article/details/86043621

--***app run must follow***
1.set environment variable
   1.1 sudo nano ~/.bashrc
   1.2 source ~/.bashrc
2.install pyaudio commond:sudo apt-get install python-pyaudio
#record tools :sudo apt-get install   audacity
3.install pygame commonds:sudo apt-get install python-pygame
4.install pip commonds:sudo apt install python-pip
5.install baiduapi commonds:pip install baidu-aip
6.install snowboy :https://blog.csdn.net/weixin_32393347/article/details/82863669



'''