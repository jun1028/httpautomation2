# encoding=utf-8
from log.Log import Log
from util.jsonutil import strToDict, strToJson, checkIsJsonpath, dictToStr
import re
try:
    from jsonpath_rw import parse
except:
    print 'please install jsonpath_rw'

__version__ = '0.0.1'


def strip(datastr):
    datastr = datastr.strip()
    datastr = datastr.replace('\"', '')
    datastr = datastr.replace('\'', '')
    return datastr

class ResultCheck(object):
    """
    class to check result:
        对期望值exceptdResult, 实际结果进行比较，可以根据关键词包含，
        正则匹配，jsonpath的方式进行校验
    """

    version = "ResultCheck/%s" % __version__

    def __init__(self):
        pass

    @staticmethod
    def checkStrResult(actualResultStr, expectResultstr):
        results = []
        bCmpResult = 0
        message    = '' 
        #多个检查结果以分号分割
        expectResults = expectResultstr.split('|')
        for expectReStr in expectResults:
            expectReStr = expectReStr.decode('utf-8').encode('utf-8')
            actualResultStr = actualResultStr.decode('utf-8').encode('utf-8')
            #如果是 jsonpath的校验
            if checkIsJsonpath(expectReStr):
                expectReStr = expectReStr.split('=')[-1]
                bCmpResult, message = ResultCheck.checkStrResultByJsonpath( \
                                                actualResultStr, expectReStr)
            else:
                bCmpResult, message = ResultCheck.checkStrResultByRe( \
                                                actualResultStr, expectReStr)
            results.append((bCmpResult, message))
        return results

    #通过正则进行比对
    @staticmethod
    def checkStrResultByRe(actualResultStr, expectReStr):
        bCmpResult = 0
        message    = '' 
        matchResult = re.findall(expectReStr, \
                                     actualResultStr, re.IGNORECASE)
        if matchResult:
            bCmpResult = 1
            message    += ';' + ResultCheck.list2str(matchResult)
        else:
            bCmpResult = -1
            message    = actualResultStr
        return bCmpResult, message

    #通过Jsonpath进行比对,expectReStr 
    @staticmethod
    def checkStrResultByJsonpath(actualResultStr, expectStr):
        Log.debug('start checkStrResultByJsonpath')
        bCmpResult = -1
        message    = ''
        expectList = expectStr.split('=') #jsonpath=
        jsonpathstr= expectList[-1]#取jsonpath后面的值
        jsonpaths = jsonpathstr.split('&')
        jsonpathExpr = ''
        try:
            jsonpathExpr = parse(str(jsonpaths[0]))
        except AttributeError, e:
            Log.error('jsonpathExpr error', e)
            message = 'jsonpathExpr error' + str(e)
            return bCmpResult, message
        jsonpathExpectValue = ''
        if len(jsonpaths) > 1:
            jsonpathExpectValue = jsonpaths[-1]
        actualResultDict = strToJson(actualResultStr)
        m = jsonpathExpr.find(actualResultDict)
        Log.debug('jsonpathExpr: ', jsonpathExpr)
        Log.debug('jsonpathExpectValue: ', jsonpathExpectValue)
        if m and len(m) > 0:
            bCmpResult, message = \
                    ResultCheck.checkMatchValue(m, jsonpathExpectValue)
            if bCmpResult == -1:
                message = 'zhengjie wirte message' #
        else:
            bCmpResult = -1
            message    = 'jsonpathExpr is , ' + str(jsonpathExpr) \
                            + ',does not match'
        Log.debug('end checkStrResultByJsonpath')
        return bCmpResult, message

    @staticmethod
    def checkMatchValue(m, jsonpathExpectValue):
        bCmpResult = -1
        message    = '' 
        for match in m:
            if jsonpathExpectValue:
                jsonpathExpectValue = strip(jsonpathExpectValue)
                if str(match.value).find(jsonpathExpectValue) > -1:
                    bCmpResult = 1
                    message    = 'the jsonpath value compare successfull, \
                                the value' + str(match.value)
                    break
            else:
                bCmpResult = 1
                message    = 'jsonpathExpectValue is null, \
                                the jsonpath is right, the value' \
                                + str(match.value)
                break
        return bCmpResult, message
    @staticmethod
    def checkJsonResult(actualResult, expectResult):
        bCmpResult, message = 0, "only output"
        expectResultDict = strToDict(expectResult)
        if "type" in expectResultDict and expectResultDict['type'] == 'part':
            print 'part'
            bCmpResult, message = ResultCheck.partOutValue(actualResult, expectResultDict)
        elif 'error' in expectResultDict and  expectResultDict['type'] == 'error':
            bCmpResult, message = 1, str(expectResultDict)
        else:
            bCmpResult, message = ResultCheck.checkStrResult(actualResult, \
                                                             str(expectResultDict))
        return bCmpResult, message

    @staticmethod
    def checkResult(actualResult, expectResult):
        Log.debug('start checkResult')
        Log.debug('actualResult', actualResult)
        Log.debug('expectResult', expectResult)
        if isinstance(actualResult, str) or isinstance(actualResult, unicode):
            actualResult = actualResult.strip()
        results = []
        #如果是期望值是字典类型
        if expectResult.find('{') == 0 or isinstance(expectResult, dict):
            if isinstance(expectResult, str):
                expectResult = strToJson(expectResult)
            results = ResultCheck.checkJsonResult(actualResult,\
                                                               expectResult)
        else:
            results = ResultCheck.checkStrResult(actualResult, \
                                                             expectResult)
        Log.debug('results', results)
        Log.debug('end checkResult')
        return results

    @staticmethod
    def list2str(lists=[]):
        strvalues = ''
        for listvalue in lists:
            strvalues += listvalue
        return strvalues

#test
if __name__ == '__main__':
    test = ResultCheck()
    test.checkStrResultByJsonpath("", "jsonpath=[data][data]:fdkfhdjhf")
    x = '''Protocol error. Session setup failed'''
    y = '''
    the first check fail, check message:{"success":false,"errorMsg":{"title":null,"remark":null,"content":"Protocol error. Session setup failed.","warn":null,"params":null},"traceInfo":"","data":null,"loginStatus":1,"bindStatus":1,"errorLevel":3,"userFlag":0,"version":0,"code":null}
    '''
    print test.checkResult(y, x)

