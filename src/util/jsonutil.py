# -*- coding: UTF-8 -*-
'''

@author: water
'''
from log.Log import Log
import json
import re


def strToDict(data):
        result = {}
        try:
            temp = re.compile(':null')
            # data = temp.sub(":'empty'",data)
            temp = re.compile(':false')
            data = temp.sub(':False',data)
            temp = re.compile(':true')
            data = temp.sub(':True',data)
            result = eval(data)
#            if isinstance(result, str):
#                result = json.loads(result, encoding='utf-8')
        except BaseException, e:
            Log.debug("strToDict exception",  e)
            Log.debug('the data is:', data)
        return result


def strToJson(data):
    datajson = {}
    try:
        data = data.strip()
        datajson = json.loads(data, encoding='utf-8')
    except BaseException, e:
        Log.debug("strToJson",  e)
        Log.debug('the data is:', data)
        datajson = strToDict(data)
    return datajson


def dictToStr(data):
    return json.dumps(data, ensure_ascii=False, encoding='UTF-8')


def dictToStr1(dictData):
    strData = '{'
    for key in dictData.keys():
        temp = '"' + str(key) + '":' + '"' + dictData[key] + '"'
        if strData == '{':
            strData += temp
        else:
            strData += ','
            strData += temp
    return strData + '}'


def checkIsJsonpath(s):
    checkResult = False
    if s.lower().find('jsonpath') == 0 \
            or s.find('$') == 0 or s.find('[') == 0:
        checkResult = True
    return checkResult

def ff(z):
    return z

if __name__ == "__main__":
    s = 'jsonpath=dfd'
#    print checkIsJsonpath(s)
#    print s.split('=')[-1]
    s = {"data":"中文".decode('utf-8')}
    print 's type', type(s), s
    d = dictToStr(s)
    print 'd', type(d), d
    z= strToDict(d)
    print 'z', type(ff(z)), ff(z)
    print ff(z)['data'].decode('utf-8').encode('utf-8')
    