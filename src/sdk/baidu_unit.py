#!/usr/bin/env python
# encoding:utf-8
import requests
import datetime
import uuid
import json
import os
from config_helper import config

class BaiDuUnit:
    def __init__(self):
        # self.access_token = self.get_token()
        self.session_id = ''
    def get_token(self,api_key = config.ROBOT_API_KEY, secret_key = config.ROBOT_SECRET_KEY):
        if config.UNIT_TOKEN is not None:
            return config.UNIT_TOKEN
        else:
            URL = 'http://openapi.baidu.com/oauth/2.0/token'
            params = {'grant_type': 'client_credentials',
                      'client_id': api_key,
                      'client_secret': secret_key}
            r = requests.get(URL, params=params)
            try:
                r.raise_for_status()
                token = r.json()['access_token']
                config.UNIT_TOKEN = token
            except requests.exceptions.HTTPError as e:
                print(e)
                return ''
            return config.UNIT_TOKEN


    def getUnit(self,query):
        """
        NLU 解析

        :param query: 用户的指令字符串
        :param service_id: UNIT 的 service_id
        :param api_key: UNIT apk_key
        :param secret_key: UNIT secret_key
        :returns: UNIT 解析结果。如果解析失败，返回 None
        """
        print("con sessionid:",self.session_id)
        url = 'https://aip.baidubce.com/rpc/2.0/unit/service/chat?access_token=' + self.get_token()
        request = {
            "query": query,
            "user_id": "888888",
        }
        body = {
            "log_id": str(uuid.uuid1()),
            "version": "2.0",
            "service_id": config.ROBOT_ID,
            "session_id": self.session_id,
            "request": request
        }
        try:
            headers = {'Content-Type': 'application/json'}
            request = requests.post(url, json=body, headers=headers)
            parsed = json.loads(request.text)
            self.session_id = self.getSessionId(parsed)
            return parsed
        except Exception:
            return None

    def getSessionId(self,parsed):
        if parsed is not None and 'result' in parsed :
            return parsed['result']['session_id']
        else:
            return ''
    def getIntent(self,parsed):
        """
        提取意图

        :param parsed: UNIT 解析结果
        :returns: 意图数组
        """
        if parsed is not None and 'result' in parsed and \
                'response_list' in parsed['result']:
            return parsed['result']['response_list'][0]['schema']['intent']
        else:
            return ''


    def hasIntent(self,parsed, intent):
        """
        判断是否包含某个意图

        :param parsed: UNIT 解析结果
        :param intent: 意图的名称
        :returns: True: 包含; False: 不包含
        """
        if parsed is not None and 'result' in parsed and \
                'response_list' in parsed['result']:
            response_list = parsed['result']['response_list']
            for response in response_list:
                if response['schema']['intent'] == intent:
                    return True
            return False
        else:
            return False


    def getSlots(self,parsed, intent=''):
        """
        提取某个意图的所有词槽

        :param parsed: UNIT 解析结果
        :param intent: 意图的名称
        :returns: 词槽列表。你可以通过 name 属性筛选词槽，
    再通过 normalized_word 属性取出相应的值
        """
        if parsed is not None and 'result' in parsed and \
                'response_list' in parsed['result']:
            response_list = parsed['result']['response_list']
            if intent == '':
                return parsed['result']['response_list'][0]['schema']['slots']
            for response in response_list:
                if response['schema']['intent'] == intent:
                    return response['schema']['slots']
        else:
            return []


    def getSlotWords(self,parsed, intent, name):
        """
        找出命中某个词槽的内容

        :param parsed: UNIT 解析结果
        :param intent: 意图的名称
        :param name: 词槽名
        :returns: 命中该词槽的值的列表。
        """
        slots = self.getSlots(parsed, intent)
        words = []
        for slot in slots:
            if slot['name'] == name:
                words.append(slot['normalized_word'])
        return words


    def getSay(self,parsed, intent=''):
        """
        提取 UNIT 的回复文本

        :param parsed: UNIT 解析结果
        :param intent: 意图的名称
        :returns: UNIT 的回复文本
        """
        if parsed is not None and 'result' in parsed and \
                'response_list' in parsed['result']:
            response_list = parsed['result']['response_list']
            if intent == '':
                return response_list[0]['action_list'][0]['say']
            for response in response_list:
                if response['schema']['intent'] == intent:
                    return response['action_list'][0]['say']
            return ''
        else:
            return ''


