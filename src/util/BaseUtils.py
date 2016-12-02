# -*- coding: UTF-8 -*-
'''
@author: water
'''
import StringIO
import datetime
import gzip
import hashlib
import os
import random
import time


def gzipToStr(data):
    compressed_data = StringIO.StringIO(data)
    gzipper = gzip.GzipFile(fileobj=compressed_data)
    html = gzipper.read()
    return html


def strToGzip(uncompressed_data):
    buf = StringIO.StringIO()
    f = gzip.GzipFile(mode="wb", fileobj=buf)
    f.write(str(uncompressed_data))
    f.close()
    compressed_data = buf.getvalue()
    return compressed_data


def getCurTime():
    return  datetime.datetime.now()


#time.strftime('%Y-%m-%d-%H-%M-%S')
def getTime():
    timeStr = ''
    try:
        timeStr = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        if timeStr[5:6] == '0':
            timeStr = timeStr[:5] + timeStr[6:]
    except:
        pass
    return timeStr


#SLEN,字符串长度
def randstr(slen):
    chars = '0123456789ABCDEF'
    rstr = ''
    for i in range(slen):
        rstr += (random.choice(chars))
        i += 1
    return rstr


def randNum(slen):
    chars = '0123456789'
    rNum = ''
    for i in range(slen):
        rNum += (random.choice(chars))
        i += 1
    return rNum


def md5(inputstr=''):
    m = hashlib.md5()   
    if inputstr:
        m.update(inputstr)
    return m.hexdigest()


def compfilesize(filename, filesize):
    result = False
    size = os.path.getsize(filename)
    if filesize == size :
        result = True
    return result

if __name__ == '__main__':
    print getTime()
    print randNum(10)