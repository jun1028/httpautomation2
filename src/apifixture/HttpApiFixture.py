#!/usr/bin/python
# -*- coding: UTF-8 -*-
# package: fixture.HttpApiFixture
'''
@author: Water.Zhang
'''
from action.BasicAction import *
from apifixture import LOGFIELPATH
from cfg.GlobalSetting import getEncoding
from cfg.HttpConf import DEFAULT_CONTENT_TYPE
from check.ResultCheck import ResultCheck
from fixture.CommonColumnFixture import CommonColumnFixture
from httputil import HttpClientUtil
from jsonpath_rw import parse
from log.Log import Log
from urllib2 import HTTPError
from util.jsonutil import strToDict, strToJson, checkIsJsonpath, dictToStr
import fixture
import os
import re


class HttpApiFixture(CommonColumnFixture):

    """
    process http api common test fixture
    1.read excel file, process header of http request.
    2.e.g. url = interface + function..
    """

    _CLASSNAME = 'apifixture.HttpApiFixture'

    interface = ''  # http url, like http://www.xxx.com:8080
    function  = ''  #path

    comments  = ['note', 'Note', 'comment', 'Comment']
    note      = ''

    initSetupFixture  = [] #在测试运行前需要执行的测试构建的【构建名，构建参数】
    preResultInfo = {} #前一次请求response的需要保存的结果信息
    client = HttpClientUtil() #客户端请求
    previousResp = None  #前一次请求的response
    link = '' #json link,返回
    userdefinefixtureresult = {} #测试执行过程中测试构建执行的测试结果信息，单个测试用例执行结果
    reqargs = {} #http请求参数
    initInfoBeforeTest = {} #执行测试前的初始化的信息，如登录的cookie,token等等
    publicParams = {}
    content_type = {}
    respHeader = {}

    # test method, ruturn actual test result 
    # @return {} json, response data
    def test(self):
        Log.debug('start test: ' + self._CLASSNAME)
        testResult = None
        self.reqargs = {}
        self.clearBeforeTestCase()
        self.beforTestCase()
        (testcaseFixture, beforeFlag) = self.getTestcaseFixture()
        if beforeFlag and testcaseFixture:
            execResult = testcaseFixture.run()
            if execResult:
                self.genBuildinVar()
        self.setUrl()
        self.setReqParams()
        #self.addPreResultToParams() #从上次请求产生的response中取得需要保存的参数信息，并保存到本次请求的参数列表中
        try:
            Log.debug('testCaseId:', self.testCaseId)
            self.setRequestMethod()
            #若果请求的路径信息中含有动态变量，则从参数列表中读取
            self.setDynamicUrlPath()
            #若果是上传文件，先调用fielupload,后做doRequest()
            self.userDefineTest()
            respData = self.doRequest(self.url, self.reqargs, self.requestMethod)
            if not beforeFlag and testcaseFixture:
                testcaseFixture = self.initExecFixture(testcaseFixture)
                execResult = testcaseFixture.run()
                if self.getResultTestCaseFixture(execResult):
                    testResult = self.getResultTestCaseFixture(execResult)
                else:
                    testResult = respData
            else:
                testResult = respData
            self.previousResp = testResult
            self.updatePublicParams()
            try:
                self.saveRespDataToFile(testResult)
            except:
                pass
            self.genResultLink(testResult)
        except BaseException, e:
            Log.error(e)
        Log.debug('end test: ' + self._CLASSNAME)
        return testResult

    def runTest(self, cell, a):
        Log.debug('start runTest: ' + self._CLASSNAME)
        try:
            if not self.expected:
                self.expected = a.parse(cell.text)
        except BaseException, e:
            Log.debug("testcaseid " + str(self.testCaseId))  
            Log.debug(e)
            self.expected = ''
        try:
            actualresult = a.get() #调用用例文件定义的构件定义的方法
            try:
                if hasattr(self, 'needSavePreResults') and self.needSavePreResults:
                    self.preResultInfo = {} #clear上次保存的信息
                    self.savePreResultInfo(actualresult)
                Log.debug('preResultInfo', self.preResultInfo)
            except BaseException, e:
                Log.error('invoke savePreResultInfo error', e)
            bresult = 0
            message = ''
            if self.expected and actualresult:
                try:
                    results = ResultCheck.checkResult(actualresult, \
                                                           self.expected)
                    bresult, message = self.parseResults(results)
                except BaseException, e:
                    Log.error('ResultCheck.checkResult error', e)
            elif not self.expected:
                bresult = 0
                message = "expect result column is null, only output!\n"
            else:
                if actualresult and actualresult.find('error') < 0:
                    bresult = 0
                    message = "expect result column is null, only output!\n"
                else:
                    bresult = -1
                    message = "expect result column is null, maybe error!\n the url:%s \n" % self.url
            if bresult > 0:
                self.right(cell, message)
            elif bresult < 0:
                self.wrong(cell, message)
            else:
                self.output(cell, message)
            try:
                cell.text = cell.text + self.link
            except:
                cell.text = self.link
        except BaseException, e:
            self.exception(cell, e)
            Log.exception(e)
        Log.debug('end runTest: ' + self._CLASSNAME)

    def doRequest(self, url, reqargs, requestMethod):
        Log.debug('start doRequest: ' + self._CLASSNAME)
        respData = ''
        try:
            if not self.content_type:
                self.content_type = DEFAULT_CONTENT_TYPE
                Log.debug('content: ', self.content_type)
            resp = self.client.dorequest(url, reqargs, \
                                     methodname=requestMethod)
            if self.url.find('login') > -1: #如果是一个登陆的url,则保存其登录返回的cookie
                self.initInfoBeforeTest['cookie'] = self.client.getCookie(resp.info())
            respData = self.getRespData(resp)
        except HTTPError, e:
            respData = '{"error":"' + str(e) + '"}'
        except Exception, e:
            respData = '{"error":"' + str(e) + '"}'
        self.previousResp = respData
        Log.debug('end doRequest: ' + self._CLASSNAME)
        return respData

    def getRespData(self, resp):
        if isinstance(resp, str) or isinstance(resp, unicode) or \
                 isinstance(resp, tuple):
            if isinstance(resp, tuple):
                self.respHeader = resp[0]
                respData = resp[1]
            else:
                respData = resp
        else:
            respData = resp.read()
        Log.debug('respData is ', respData.decode('utf-8').encode(getEncoding()))
        return respData
    
    #处理表头中的一些共有的testsuite级别的全局参数
    def processHeads(self, rowpos):
        Log.debug('start processHeads: ' + self._CLASSNAME)
        self.interface, rowpos = self.getInterface(rowpos)
        self.function, rowpos = self.getFunction(rowpos)
        self.requestMethod, rowpos = self.getRequestMethod(rowpos)
        self.content_type, rowpos = self.getContenttype(rowpos)
        Log.debug('content_type rowpos:', rowpos)
        self.auth, rowpos = self.getAuth(rowpos)
        Log.debug('auth rowpos:', rowpos)
        self.argCounts, rowpos = self.getArgCounts(rowpos)
        Log.debug('argCounts rowpos:', rowpos)
        self.initSetupFixture, rowpos = self.getInitSetupFixture(rowpos)
        Log.debug('initBeforeTest rowpos:', rowpos)
        self.publicParams, rowpos = self.getPublicparams(rowpos)
        Log.debug('publicParams rowpos:', rowpos)
        self.note, rowpos = self.getComment(rowpos)
        Log.debug('note rowpos:', rowpos)
        Log.debug('end processHeads: ' + self._CLASSNAME)
        return rowpos

    # @return: interface, rowpos
    def getInterface(self, rowpos, ncols=2):
        interface = ''
        for col in range(0, ncols):
            interface = self.tableData[rowpos][col]
            if len(interface) > 1 and interface.lower().find('interface') > -1:
                interface = self.tableData[rowpos][col + 1]
                rowpos += 1
                break
        return interface, rowpos

    # @return: function, rowpos
    def getFunction(self, rowpos, ncols=2):
        function = ''
        for col in range(0, ncols):
            function = self.tableData[rowpos][col]
            if len(function) > 1 and function.lower().find('function') > -1:
                function = self.tableData[rowpos][col + 1]
                rowpos += 1
                break
        return function, rowpos

    # @return: request, rowpos
    def getRequestMethod(self, rowpos, ncols=2):
        request = None
        for col in range(0, ncols):
            request = self.tableData[rowpos][col]
            if len(request) > 1 and request.lower().find('request') > -1:
                request = self.tableData[rowpos][col + 1]
                request = request.strip()
                rowpos += 1
                break
        if len(request) < 2:
            request = None
        return request, rowpos

    # @return: request, rowpos
    def getContenttype(self, rowpos, ncols=2):
        content_type = ''
        for col in range(0, ncols):
            content_type = self.tableData[rowpos][col]
            if len(content_type) > 1 and content_type.lower().find('content') > -1:
                content_type = self.tableData[rowpos][col + 1]
                content_type = content_type.strip()
                rowpos += 1
                break
        return content_type, rowpos

    # @return: function, rowpos
    def getAuth(self, rowpos):
        auth = self.tableData[rowpos][0]
        if len(auth) > 1 and auth.lower().find('auth') > -1:
            rowpos += 1
        return auth, rowpos

    def getPath(self, rowpos):
        request = ''
        for col in range(0, 2):
            request = self.tableData[rowpos][col]
            if len(request) > 1 and request.lower().find('path') > -1:
                request = self.tableData[rowpos][col + 1]
                request = request.strip()
                rowpos += 1
                break
        return request, rowpos

    # @return: interface, rowpos
    def getArgCounts(self, rowpos):
        argCounts = 0
        for col in range(0, 2):
            argCounts = self.tableData[rowpos][col]
            if len(argCounts) > 1 and argCounts.lower().find('argcount') > -1:
                argCounts = self.tableData[rowpos][col + 1]
                rowpos += 1
                break
        return argCounts, rowpos

    #在执行测试集前需要执行测试构建，如登录，造数据构建
    # @return:返回一个构建名，构建参数
    def getInitSetupFixture(self, rowpos):
        result = []
        fixtureName = ''
        fixtureParams = ''
        returnparam = ''
        for col in range(0, 2):
            temp = self.tableData[rowpos][col]
            if len(temp) > 1 and temp.lower().find('fixture') > -1:
                fixtureName   = self.tableData[rowpos][col]
                fixtureParams = self.tableData[rowpos][col + 1]
                returnparam   = self.tableData[rowpos][col + 2]
                rowpos += 1
                break
        if fixtureName:
            result = [fixtureName, fixtureParams, returnparam]
        return result, rowpos

    def getPublicparams(self, rowpos):
        publicParams = {}
        for col in range(0, 2):
            try:
                temp = self.tableData[rowpos][col]
                if len(temp) > 1 and temp.lower().find('publicparam') > -1:
                    publicParamStr = self.tableData[rowpos][col + 1]
                    publicParams = self.initPublicParamsDictByList(publicParamStr)
                    rowpos += 1
                    break
            except BaseException, e:
                Log.error('getPublicparams ERROR', e)
        return publicParams, rowpos

    # @return: note, rowpos
    def getComment(self, rowpos):
        note = ''
        while True:  # multiple rows comment
            noteFlag = False
            temp = self.tableData[rowpos][0]
            if len(temp) > 1:
                for comment in self.comments:
                    if temp.find(comment) > -1:
                        note = note + temp
                        noteFlag = True
                        break
            if noteFlag:
                rowpos += 1
                noteFlag = False
            else:
                break
        return note, rowpos

    #通过列表初始化字典
    def initPublicParamsDictByList(self, publicParamStr):
        publicparams = {}
        if publicParamStr:
            publicParamList = re.split("[,|;]", publicParamStr)
            for publicParam in publicParamList:
                publicparams[publicParam] = ''
        return publicparams

    #把保存上次请求的结果信息
    #param: type dict {} result, 上次请求的response信息
    #param getvalueway ,从response取值的方式，=0 dict方式,=1 通过正则
    #return type dict {}
    def savePreResultInfo(self, resp):
        Log.debug('start savePreResultInfo: ' + self._CLASSNAME)
        try:
            Log.debug('start savePreResultInfo: ' + resp)
            respDict = strToJson(resp)
            Log.debug('respDict: ', respDict)
            Log.debug('needSavePreResults: ', self.needSavePreResults)
            if respDict and self.needSavePreResults.find('{') > -1:
                needSavePreResultDict = strToJson(self.needSavePreResults)
                if needSavePreResultDict:
                    Log.debug('needSavePreResultDict: ', needSavePreResultDict)
                    for key in needSavePreResultDict:
                        self.preResultInfo[key] = self.getKeyValueFromDict(key, respDict)
                else:
                    print 'json or dictionary is error'  + self.needSavePreResults#忽略
            else:
                if not ('error' in respDict and respDict['error']):
                    needSavePreResultList = self.needSavePreResults.split(';')
                    for savePreResult in needSavePreResultList:
                        [key, value] = savePreResult.split('=')
                        self.preResultInfo[key] = self.getValueFromRespByPattern(value, resp)
        except BaseException, e:
            Log.error(e)
        Log.debug('end savePreResultInfo: ' + self._CLASSNAME)
        return self.preResultInfo

    def getKeyValueFromRespDict(self, key):
        fromdict = strToJson(self.previousResp)
        return self.getKeyValueFromDict(key, fromdict)

    def getKeyValueFromDict(self, key, fromdict):
        keyvalue = ''
        if isinstance(fromdict, dict) and key in fromdict:
            if fromdict[key] == 0:
                keyvalue = fromdict[key]
            else:
                if fromdict[key]:
                    keyvalue = str(fromdict[key])
        return keyvalue

    def getValueFromRespByPattern(self, pattern, resp):
        result = ''
        temp = re.findall(pattern, resp, re.IGNORECASE)
        if temp:
            #获取匹配的第一个元组
            try:
                result = temp[0].split(":")[-1]#
            except BaseException, e:
                Log.error('getValueFromRespByPattern: ', e)
        return result

    def getJsonpathValueFromResp(self, jsonpathExprStr, resp):
        jsonpathValue = None
        try:
            jsonpathExpr = parse(jsonpathExprStr)
            respDict = strToJson(resp)
            m = jsonpathExpr.find(respDict)
            if len(m) > 0:
                jsonpathValue = m[0].value
        except BaseException, e:
            Log.error('getJsonpathValueFromResp error', e)
        return jsonpathValue

    def addPreResultToParams(self):
        self.addSpeficPreResultToParams()

    def setLoginInfo(self, client):
        Log.debug('start setLoginInfo: ' + self._CLASSNAME)
        if hasattr(self, 'initInfoBeforeTest') and self.initInfoBeforeTest:
            if "cookie" in self.initInfoBeforeTest:
                #如果包含sessionid信息，则更新cookie
                if self.initInfoBeforeTest['cookie'].find('JSESSIONID') > -1:
                    client.cookie = self.initInfoBeforeTest['cookie']
            if "token" in self.initInfoBeforeTest:
                client.token = self.initInfoBeforeTest['token']
            Log.debug("initInfoBeforeTest: ", self.initInfoBeforeTest)
        Log.debug('end setLoginInfo: ' + self._CLASSNAME)

    def addSpeficPreResultToParams(self):
        if hasattr(self, 'preResultInfo') and self.preResultInfo is dict \
            and self.preResultInfo:
            self.reqargs.update(self.preResultInfo)

    def setUrl(self):
        #如果测试用例没有url列,或者为空，则用列头的url值
        if not hasattr(self, 'url') or not self.url:
            if self.interface and self.function:
                self.url = self.interface + self.function
            else:
                Log.debug("self.interface or  self.function is none")
                Log.debug("self.url", self.url)
        return self.url

    def setRequestMethod(self):
        if not hasattr(self, 'requestMethod') and not self.requestMethod:
            self.requestMethod = 'post'

    #从测试文件，如excel或许excel中获取fixturename 列，并调用其run(),
    #@return result type, dict    
    def execFixture(self, paramsDict={}):
        userdefinefixtureresult = {}
        if hasattr(self, 'userdefinefixture') and self.userdefinefixture:
            userdefinefixture = self.getFixture(self.userdefinefixture)
            userdefinefixture = self.initExecFixture(userdefinefixture)
            userdefinefixtureresult = userdefinefixture.run(paramsDict)
        return userdefinefixtureresult

    #从测试文件，如excel或许excel中获取fixturename 列，并调用其run(),
    #@return testcaseFixture, beforeFlag    
    def getTestcaseFixture(self):
        testcaseFixture = None
        beforeFlag = False
        if hasattr(self, 'userdefinefixture') and self.userdefinefixture:
            if self.userdefinefixture.find('before') > -1:
                beforeFlag = True
            testcaseFixture = self.getFixture(self.userdefinefixture)
        return testcaseFixture, beforeFlag

    def getResultTestCaseFixture(self, execResult):
        testResult = None
        if execResult and 'actualResult' in execResult :
            if execResult['actualResult']:
                testResult = execResult['actualResult']
                self.userdefinefixtureresult['actualResult'] = \
                                                    testResult
        return testResult

    #将当前构建的部分值传给将要执行构建
    def initExecFixture(self, userdefinefixture):
        userdefinefixture.previousResp = self.previousResp
        userdefinefixture.url = self.url
        userdefinefixture.reqargs = self.reqargs
        userdefinefixture.initInfoBeforeTest = self.initInfoBeforeTest
        userdefinefixture.requestMethod = self.requestMethod
        userdefinefixture.publicParams = self.publicParams
        return userdefinefixture

    def getFixture(self, fixturePath):
        fixture = None
        temp = fixturePath.split('.')
        _CLASSNAME = temp[-1]
        if len(temp) == 1:
            fixturePath = 'fixture.' + _CLASSNAME
        try:
            exec 'import ' + fixturePath
            exec 'fixture = ' + fixturePath + '.' + _CLASSNAME + '()' 
        except BaseException, e:
            Log.error('getFixture error:', e)
        return fixture

    def runInitSetupFixture(self):
        Log.debug('start runInitSetupFixture: ' + self._CLASSNAME)
        fixturePath   = self.initSetupFixture[0]
        fixtureParams = self.initSetupFixture[1]
        returnparam   = self.initSetupFixture[2]
        fixture = self.getFixture(fixturePath)
        if fixture:
            self.initInfoBeforeTest = fixture.run(fixtureParams, returnparam)
            Log.debug('end runInitSetupFixture: ', self.initInfoBeforeTest)
        Log.debug('end runInitSetupFixture: ' + self._CLASSNAME)

    def genResultLink(self, respData):
        Log.debug('start genResultLink: ' + self._CLASSNAME)
        try:
            jsonResult = strToJson(respData)
            if jsonResult and 'data' in jsonResult:
                divName = 'div' + self.testCaseId
                self.link =  "<p align='left' ><br><a href=javascript:show('" + divName + "');>show json text</a></p>"  + \
                                "<br><div id='" + divName + "' style='display:none;'>"+ respData + "</div>"
            else:
                self.link = "<i>the Data of Response is %s<i>" %  respData
        except BaseException, e:
            print e
            self.link = " response data is %s " %  respData
        Log.info('self.link', self.link)
        Log.debug('end genResultLink: ' + self._CLASSNAME)

    def saveRespDataToFile(self, respData):
        fileName = str(self.testCaseId + 'json.txt')
        path = LOGFIELPATH + self.curTableName
        if not os.path.exists(LOGFIELPATH):
            os.mkdir(LOGFIELPATH)
        try:
            if not os.path.exists(path):
                os.mkdir(path)
            fileObject = open(path + os.sep + fileName, 'w')
            fileObject.write(respData)
            fileObject.close()
        except BaseException, e:
            Log.error("create jsontxt fail!", e)

    #若果请求的路径参数包含{变量}的变量，则从当期的测试参数中取
    #foxexample: url= http://www.xxx.com:8080/path1/{patah2}/p
    def setDynamicUrlPath(self, params={}):
        Log.debug('start setDynamicUrlPath: ' + self._CLASSNAME)
        pattern = '{\\w+}' #{}
        if not params:
            params = self.reqargs
        dynamicPathList = re.findall(pattern, self.url, re.IGNORECASE)
        try:
            for dynamicpath in dynamicPathList:
                dynamicpathVar = dynamicpath[1:-1] #去掉{}
                if dynamicpathVar in params:
                    params[dynamicpathVar] = params[dynamicpathVar].replace('"', '')
                    self.url = self.url.replace(dynamicpath, params[dynamicpathVar])
                    params.pop(dynamicpathVar)
                else:
                    Log.error('setDynamicUrlPath fail, reqargs has not ' + dynamicpathVar)
        except Exception, e:
            Log.error(e)
        Log.debug('end setDynamicUrlPath: ' + self._CLASSNAME)

    #需要重新编写,去掉不做请求的参数
    def skipNoNeedParam(self):
        Log.debug('start skipNoNeedParam: ' + self._CLASSNAME)
        paramList = []
        for param in self._typeDict:
            #如果包含_下划线，表明不是用作请求参数
            if isinstance(param, str) or isinstance(param, unicode):
                if  param.find('_') == 0 or param.lower().find('url') > -1 \
                    or param.lower().find('savepre') > -1 or \
                    param.lower().find('fixture') > -1 or \
                    param.lower().find('test') == 0 or \
                    param.lower().find('testcaseid') > -1:
                    continue
                paramList.append(param)
        return paramList
        Log.debug('end skipNoNeedParam: ' + self._CLASSNAME)

    def setReqParams(self):
        #如果有_args变量
        if hasattr(self, '_args') and self._args != 'empty':
            self.setReqParamsByArgjson()
        else:
            self.setReqParamsByBuildinVar()

    def setReqParamsByBuildinVar(self):
        argv = self.skipNoNeedParam()
        if isinstance(argv, list):
            for arg in argv:
                self._addValueToParam(arg)

    def setReqParamsByArgjson(self):
        if isinstance(self._args, str) or (isinstance(self._args, unicode)):
            if self._args.find('\\') > -1:
                self.reqargs = strToDict(self._args)
            else:
                self.reqargs = strToJson(self._args)
        if self.reqargs:
            for reqarg in self.reqargs:
                value = self.reqargs[reqarg]
                value = self.getBuildinVarValue(value)
                self.reqargs[reqarg] = value
        else:
            Log.error('setReqParamsByArgjson error', self._args)

    def updateVarvalueInDict(self, paramvalue):
        Log.debug('start updateVarvalueInDict: ' + self._CLASSNAME)
        paramDict = strToJson(paramvalue)
        for param in paramDict:
            value = paramDict[param]
            try:
                value = self.getBuildinVarValue(value)
                paramDict[param] = value
            except BaseException, e:
                Log.error('updateVarvalueInDict error', e)
        Log.debug('end updateVarvalueInDict: ' + self._CLASSNAME)
        return dictToStr(paramDict)

    def getDynamicParamVlaueByInvokeMethod(self, methodstr):
        Log.debug('start getDynamicParamVlaueByInvokeMethod: ' + self._CLASSNAME)
        dynamicParamVlaue = ''
        methodstr = methodstr[1:-1] #strip %%
        methods = methodstr.split('(')
        methodname = methods[0]
        paramstr = methods[1][:-1] #strip ')'
        params = paramstr.split(',')
        paramtemp = ''
        for param in params:
            if paramtemp:
                paramtemp += ','
            paramtemp += '\'' + param + '\''
        try:
            execstr = 'dynamicParamVlaue =' + methodname + '(' + paramtemp + ')'
            exec execstr
        except:
            Log.error('exec error', execstr)
        Log.debug('end getDynamicParamVlaueByInvokeMethod: ' + self._CLASSNAME)
        return dynamicParamVlaue

    def getDynamicParamVlaue(self, paramvalue, fromWhDict={}):
        Log.debug('start getDynamicParamVlaue: ' + self._CLASSNAME)
        result = paramvalue
        key    = paramvalue[1:-1] #去掉%%
        try:
            Log.debug('self.previousResp: ', self.previousResp)
            if key.find('\\') > -1: #正则表达式
                result = self.getValueFromRespByPattern(key, self.previousResp)
            else:
                if checkIsJsonpath(key):
                    key = key.split('=')[-1] #取=号的值
                    result = self.getJsonpathValueFromResp(key, self.previousResp)
                else:
                    result = self.getKeyValueFromRespDict(key)
                #过滤从response字典中获取的值，data,或id key取值可能是一个大的列表
                result = self.fliterParamValue(key, result)
            if not result: #如果当前值没有，则试着从公有变量中获取
                result = self.getKeyValueFromDict(key, self.publicParams)
        except BaseException, e:
            Log.error('getDynamicParamVlaue error:', e)
        Log.debug('end getDynamicParamVlaue: ' + self._CLASSNAME)
        return result

    #为请求参数中含有变量名进行赋值
    def updateBuildinVar(self):
        Log.debug('start updateBuildinVar: ' + self._CLASSNAME)
        for param in self._typeDict:
            #如果包含_下划线，表明不是用作请求参数
            if param.find('_') == 0 or param.find('url') == 0\
                or param.find('fixture') > -1 or param.find('test') == 0:
                continue
            else:
                try:
                    Log.debug('param:', param)
                    exec 'paramvalue = self.' + param
                    if (isinstance(paramvalue, str) or isinstance(paramvalue, unicode)) and \
                        paramvalue.find('{') == 0 and param != '_args' and \
                        paramvalue.find('%') > -1:
                        paramvalue = self.updateVarvalueInDict(paramvalue)
                    else:
                        paramvalue = self.getBuildinVarValue(paramvalue)
                    execstr =  'self.' + param +'= paramvalue'
                    exec execstr
                except BaseException, e:
                    Log.error('updateBuildinVar error')
                    Log.error('paramvalue', param)
                    Log.error(e)
        Log.debug('end updateBuildinVar: ' + self._CLASSNAME)

    #设定%%的变量值
    def getBuildinVarValue(self, paramvalue):
        Log.debug('start getBuildinVarValue: ' + self._CLASSNAME)
        varvalue = paramvalue
        if isinstance(paramvalue, str) or isinstance(paramvalue, unicode):
            if self.checkIsMethod(paramvalue):
                varvalue = self.getDynamicParamVlaueByInvokeMethod(paramvalue)
                Log.debug('getDynamicParamVlaueByInvokeMethod value: ',  varvalue)
            elif self.checkIsVar(paramvalue): #如果包含动态变量
                varvalue = self.getDynamicParamVlaue(paramvalue)
                Log.debug('getDynamicParamVlaue value: ',  varvalue)
        Log.debug('the varvalue: ', varvalue)
        Log.debug('end getBuildinVarValue: ' + self._CLASSNAME)
        return varvalue

    def _addValueToParam(self, arg):
        if hasattr(self, arg):
            # self.arg的内容不为空
            #exec "isnull = (self." + arg + " != '')"
            exec 'temp = self.' + arg
            if temp != 'empty': #如果是关键词empty则意味不作为请求参数
                self.reqargs[arg] = temp

    def checkIsVar(self, varName):
        checkResult = False
#        pattern = '%\w+%'
        try:
            if varName.find('%') == 0:
#                temp = re.findall(pattern, varName)
#                if temp and len(temp) == 1:
                checkResult = True
        except:
            Log.error('checkIsVar error, the varName is:', varName)
        Log.debug('checkIsVar result', checkResult)
        return checkResult

    def checkIsMethod(self, methodName):
        checkResult = False
        pattern = '\([\w|,]+\)' #match ()
        try:
            if methodName.find('%') == 0:
                mgroup = re.findall(pattern, methodName)
                if mgroup and len(mgroup) == 1:
                    checkResult = True
        except:
            Log.error('checkIsVar error')
        return checkResult

    def processData(self, data):
        return  ''

    def parseResults(self, results):
        finalresultvalue = 1
        message = ''
        try:
            for i in range(0, len(results)):
                #有一个结果校验失败，则最终整体校验结果为失败
                if i < 6:
                    sequense = CommonColumnFixture.DIGITSEQUENCE[i]
                else:
                    sequense = 'more'
                if results[i][0] < 0:
                    finalresultvalue = results[i][0]
                    message += 'the ' + sequense + ' check fail, check message:' \
                    + results[i][1] + '\n'
                else:
                    message += 'the ' + sequense + ' check pass, check message:' \
                    + results[i][1] + '\n'
        except BaseException, e:
            Log.error('parseResults error', e)
        return finalresultvalue, message

    def updatePublicParams(self, key=''):
        Log.debug('start updatePublicParams: ' + self._CLASSNAME)
        respDict = strToJson(self.previousResp)
        if respDict:
            if not key: #如果没有指定key
                for publicparam in self.publicParams:
                    self.updatePublicParamsByKey(publicparam, respDict)
            else:
                self.updatePublicParamsByKey(key, respDict)
        Log.debug('end updatePublicParams: ' + self._CLASSNAME)

    def updatePublicParamsByKey(self, publicparam, respDict):
        publicparamvalue = self.getKeyValueFromDict(publicparam, respDict)
        publicparamvalue = self.fliterParamValue(publicparam, publicparamvalue)
        if publicparamvalue:
            self.publicParams[publicparam] = publicparamvalue

    #如果key为data 或者id,使用\w+正则过滤下
    def fliterParamValue(self, key, value):
        result = ''
        value = str(value).strip()
        if key == 'data' or key == 'id':
            m = re.findall(r"\w+", value)
            if m and len(m) == 1:
                result = m[0]
        else:
            result = value
        return result

    def clearBeforeTestCase(self):
        if self.reqargs and isinstance(self.reqargs, dict):
            self.reqargs.clear()

    def beforTestCase(self):
        Log.debug('start beforTestCase: ' + self._CLASSNAME)
        self.setLoginInfo(self.client)
        self.updateBuildinVar()
        Log.debug('end beforTestCase: ' + self._CLASSNAME)

    def genBuildinVar(self, params={}):
        for key in params:
            exec 'self.' + key + '=' +  params[key]

    def userDefineTest(self):
        print 'super class, does not implement'

if __name__ == "__main__":
    testhttpapi = HttpApiFixture()
    print testhttpapi.checkIsVar('%randnum%')
    print testhttpapi.getDynamicParamVlaueByInvokeMethod('%randnum(4)%')
#    print testhttpapi.fliterParamValue('data', 'dfdfhjkdfhjkdhfkj')
#    print testhttpapi.fliterParamValue('data', 'dfdfhjkdfdfdf232hjkdh52364572fkj')
#    print testhttpapi.fliterParamValue('data', 'dfdfhj-kdfdfdf2-32hjk-dh52364572fkj')
#    