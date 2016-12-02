# -*- coding: UTF-8 -*-
# package: api.HttpClientUtil
'''

@author: Water.Zhang
'''
from log.Log import Log
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from util.jsonutil import strToDict, dictToStr
import StringIO
import cookielib
import gzip
import httplib
import json
import os
import re
import sys
import urllib
import urllib2

try:
    import httplib2
except:
    print 'please install httplib2'


def callbackfunc(blocknum, blocksize, totalsize):
    '''
    @blocknum: 已经下载的数据块
    @blocksize: 数据块的大小
    @totalsize: 远程文件的大小
    '''
    percent = 100.0 * blocknum * blocksize / totalsize
    if percent > 100:
        percent = 100
        print 'totalsize:', totalsize
    return "%.2f%%"% percent


def download(url, filename):
    contentlen = 0
    try:
        print "downloading with urllib"
        filename, header = urllib.urlretrieve(url, filename, callbackfunc)
        contentlen = header.getheader('Content-Length')
    except:
        print 'download error'
    return contentlen


class HttpClientUtil(object):
    
    _CLASSNAME = 'httputil.HttpClientUtil'
    
    headerinfo = ''
    serResp = None

    def __init__(self):
        self.token = ''
        self.referer = ''
        self.headers = {}
        #cookies
        self.cookie = ''
        self.cookies = urllib2.HTTPCookieProcessor()
        self.opener  = urllib2.build_opener(self.cookies)
    
    #调用前，需要设定header
    def dorequest1(self, url, args=None, \
                        methodname='POST'):
        response = None
        if methodname.upper() == 'POST':
            response = self.httppost(url, args)
        elif methodname.upper() == 'GET':
            response = self.get(url, args)
        else:
            print 'does not implement!'
        return response  

    def dorequest(self, url, args=None, \
                        content_type=None, \
                        methodname='POST'):
        response = None
        Log.info('url:', url)
        Log.info('args:', args)
        Log.info('request method:', methodname)
#        args = self.reqargsencode(args)
        self.setHeader()
        if methodname.upper() == 'POST':
            response = self.httppost(url, args, content_type)
        elif methodname.upper() == 'GET':
            response = self.get(url, args, content_type)
        elif methodname.upper() == 'UPLOAD':
            if  os.path.exists(args):
                response = self.uploadfile(url, args, content_type)
            else:
                Log.error('filepath is not exists: ', args)
                response = 'filepath does not exists'
        elif methodname.upper() == 'DELETE':
            response = self.delete(url, args, content_type)
        elif methodname.upper() == 'PUT':
            response = self.put(url, args, content_type)
        else:
            print 'does not implement!'
#        try:
#            cookie = self.getCookie(response.info())
#            self.setCookie(cookie)
#        except:
#            pass
        return response

    def httppost(self, url, args=None, content_type=None):
        params = urllib.urlencode(args)
        req = urllib2.Request(url, params)
        if self.headers:
            req = self.setReqHeader(req, self.headers)
        if content_type:
            req.add_header('Content-Type', content_type)
        response = self.opener.open(req)
        self.response = response
        return self.response

    def get(self, url, args=None, content_type=None, headers=None):
        params = ''
        Log.debug('start get' + self._CLASSNAME)
        if args and not isinstance(args, dict):
            args = self.strToJson(args)
        if args:
            params = urllib.urlencode(args)
        if params:
            url = url + '?' + params
        Log.debug(url)
        req = urllib2.Request(url)
        if self.headers:
            req = self.setReqHeader(req, self.headers)
        if content_type:
            req.add_header('Content-Type', content_type)
        response = self.opener.open(req)
        self.response = response
        Log.debug('start end' + self._CLASSNAME)
        return self.response

    def openUrl(self, url, args='', content_type=''):
        req = urllib2.Request(url)
        if content_type:
            req.add_header('Content-Type', content_type)
        if isinstance(args, dict):
            body = urllib.urlencode(args)
        else:
            body = args
        response = urllib2.urlopen(req, body)
        return response

    def auth(self, url, args, username, PWD):
        p = urllib2.HTTPPasswordMgrWithDefaultRealm()
        p.add_password(None, url, username, PWD)
        handler = urllib2.HTTPBasicAuthHandler(p)
        opener = urllib2.build_opener(handler)
        urllib2.install_opener(opener)
        feedbackParams = urllib.urlencode(args)
#        req = urllib2.Request(url)
#         print url + str(feedbackParams)
        response = urllib2.urlopen(url + str(feedbackParams))
        return response

    def do(self, url, args, methodname='POST'):
        http = httplib2.Http()
        if hasattr(self, 'cookie') and len(self.cookie) > 1:
            if self.cookie.find('JSESSIONID') > -1:
                self.headers['Cookie'] = self.cookie
        if isinstance(args, dict):
            body = urllib.urlencode(args)
        else:
            body = args
        if methodname == 'GET':
            url += '?' + body
            body = ''
        Log.debug('url:', url)
        Log.debug('methodname:', methodname)
        Log.debug('headers:', self.headers)
        response = http.request(url, methodname, \
                                headers=self.headers, body=body)
        return response

    def put(self, url, args):
        return self.do(url, args, methodname='PUT')

    def delete(self, url, args, content_type=None):
        return self.do(url, args, methodname='DELETE')

    def post(self, url, args):
        return self.do(url, args, methodname='post')

    def reqargsencode(self, args):
        Log.debug('args type', type(args))
        args = dictToStr(args)
        args = strToDict(args)
        Log.debug('args:', args)
        Log.debug('args type:', type(args))
        return args

    def setHeader(self):
        if hasattr(self, 'cookie') and len(self.cookie) > 1:
            if self.cookie.find('JSESSIONID') > -1:
                self.headers['Cookie'] = self.cookie
        if hasattr(self, 'referer') and len(self.referer) > 1:
            self.headers['Referer'] = self.referer
                
    def setReqHeader(self, request, headers=None):
        if headers:
            for header in headers:
                request.add_header(header, headers[header])
        return request
    
    def proceHeadInfo(self, info):
        try:
            if info and 'Set-Cookie' in info:
                self.headerinfo = info
                self.cookie = info['Set-Cookie']
        except:
            Log.debug('proceHeadInfo error') 

    def uploadfile(self, url, filepath, content_type="multipart/form-data"):
        register_openers()
        fi = open(filepath, "rb")
        datagen, headers = multipart_encode({'file': fi})
        request = urllib2.Request(url, datagen, headers)
        if self.headers:
            request = self.setReqHeader(request, self.headers)
        response = urllib2.urlopen(request)
        #response = self.opener.open(request)
        return response

    def postAndCooks(self, url, args, content_type=None):
        argDict = self.strToJson(args) 
        data = urllib.urlencode(argDict)
        urls = url.split('/')
        h = httplib.HTTPConnection(urls[2])
        path = ''
        for i in range(3, len(urls)):
            path += '/' + urls[i]
        h.request('POST', url, data, self.headers)
        r = h.getresponse()
#         print 'read', r.read()
#         print 'header', r.getheaders()
#         print 'cook', r.getheader('set-cookie')
        self.headers['Cookie'] = r.getheader('set-cookie')
#         print 'post', self.headers['Cookie'] 
        return r
    
#     def put(self, url, args, content_type=None):
#         req = urllib2.Request(url, data = urllib.urlencode(args) )
#         if content_type:
#             req.add_header('Content-Type', content_type)
#         req.get_method = lambda: 'PUT'
#         response = urllib2.urlopen(req)
#         return response
    def gzipToStr(self, data):
        data = StringIO.StringIO(data)
        gzipper = gzip.GzipFile(fileobj=data)
        html = gzipper.read()
        return html

    def strToDict(self, data):
        result = {}
        try:
            temp = re.compile(':null')
            data = temp.sub(":'result is null'", data)
            temp = re.compile(':false')
            data = temp.sub(':False', data)
            temp = re.compile(':true')
            data = temp.sub(':True', data)
            result = eval(data)
        except BaseException, e:
            print "strToDict exception"
            print e
        return result

    def strToJson(self, data):
        return json.loads(data)

    def dictToStr(self, dictData):
        strData = '{'
        for key in dictData.keys():
            temp = '"' + str(key) + '":' + '"' + dictData[key] + '"'
            if strData == '{':
                strData += temp
            else:
                strData += ','
                strData += temp
        return strData + '}'
    
    def setCookie(self, cookie):
        if cookie:
            self.cookie = cookie

    def getCookie(self, respInfo):
        cookie = ''
        try:
            if respInfo and 'Set-Cookie' in respInfo:
                cookie = respInfo['Set-Cookie']
        except BaseException, e:
            Log.error("get cookie value error", e)  
        return cookie
#test
if __name__ == '__main__':
    client = HttpClientUtil()

