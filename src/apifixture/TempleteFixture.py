# -*- coding: UTF-8 -*-
# package: apifixture.TempleteFixture
'''
@author: water
'''

from apifixture.HttpApiFixture import HttpApiFixture
from log.Log import Log
from cfg.GlobalSetting import getEncoding


class TempleteFixture(HttpApiFixture):
    
    '''
            用于测试基于http restful,http协议接口的默认测试构件
    '''

    _CLASSNAME = 'apifixture.TempleteFixture'

    # test method, ruturn actual test result 
    # @return {} json, response data
#    def test(self):
#        Log.debug('start test: ' + self._CLASSNAME)
#        testResult = None
#        self.clearBeforeTestCase()
#        self.beforTestCase()
#        (testcaseFixture, beforeFlag) = self.getTestcaseFixture() 
#        if beforeFlag and testcaseFixture:
#            ExecResult = testcaseFixture.run()
#            if ExecResult:self.genBuildinVar()
#        self.setUrl()
#        self.setReqParams()
#        self.addPreResultToParams() #从上次请求产生的response中取得需要保存的参数信息，并保存到本次请求的参数列表中
#        try:
#            Log.debug('testCaseId:', self.testCaseId)
#            self.setRequestMethod()
#            #若果请求的路径信息中含有动态变量，则从参数列表中读取
#            self.setDynamicUrlPath()
#            #若果是上传文件，先调用fielupload,后做doRequest()
#            reqargs = self.fileUpload()
#            respData = self.doRequest(self.url, reqargs, self.requestMethod)
#            if not beforeFlag and testcaseFixture:
#                testcaseFixture = self.initExecFixture(testcaseFixture)
#                ExecResult = testcaseFixture.run()
#                if self.getResultTestCaseFixture(ExecResult):
#                    testResult = self.getResultTestCaseFixture(ExecResult)
#                else:
#                    testResult = respData 
#            else:
#                testResult = respData
#            self.saveRespDataToFile(testResult)
#            self.genResultLink(testResult)
#        except BaseException, e:
#            Log.error( e )
#        Log.debug('end test: ' + self._CLASSNAME)
#        return testResult

    def userDefineTest(self):
        self.fileUpload()

    def fileUpload(self):
        reqargs = self.reqargs
        if 'filepath' in self.reqargs:
            self.requestMethod = 'upload'
            filepath = self.reqargs['filepath']
            Log.debug("filepath:", filepath)
            reqargs = filepath.decode('utf-8').encode(getEncoding())
    #                     self.reqargs = filepath.decode('utf-8').encode('gb2312')
            self.client.referer = "http://pre.moojnn.com/datasource.html" 
        self.reqargs = reqargs
        return reqargs

if __name__ == "__main__":
    test = TempleteFixture()
