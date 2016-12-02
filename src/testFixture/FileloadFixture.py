# -*- coding: UTF-8 -*-
# package: testfixture.FileloadFixture
'''
Created on 2016年11月8日
@author: xh

'''

from apifixture.HttpApiFixture import HttpApiFixture
from log.Log import Log
from util.jsonutil import strToDict
import time

class FileloadFixture(HttpApiFixture):
    '''
        用于测试文件上传后获取table的sheets时候的多次请求服务器
    '''
    _CLASSNAME = 'test.FileloadFixture'

    def run(self, paramDict={}):
        Log.debug('start run method', self._CLASSNAME)
        returnResult = {}
        respData = self.previousResp
        url = self.url
        reqargs = self.reqargs
        i = 0
        while True:
            i += 1
            respDict = strToDict(respData)
            errorLevel = int(self.getKeyValueFromDict('errorLevel', respDict))
            if errorLevel == 0:
                break
            respData = self.doRequest(url, reqargs, \
                                      requestMethod=self.requestMethod)
            if i == 10:
                break
            time.sleep(2)
        if respData:
            returnResult['actualResult'] = respData
        Log.debug('end run method', self._CLASSNAME)
        return  returnResult  