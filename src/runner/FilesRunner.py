# -*- coding: UTF-8 -*-
'''
@author: water
测试当前目录&子目录下所有的测试用例文件
'''

from cfg import GlobalSetting
from log.Log import Log
from runner.ExcelTestDriver import ExcelTestDriver
from util.sendmail import sendmail
import os
import sys


def getFiles(foldername, parentdir=None, filepaths=[]):
    '''
            获取当前目录&子目录下所有的文件名
    '''
    Log.debug('start: FilesRunner getFiles')
    if parentdir:
        curpath = os.path.join(parentdir, foldername)
    else:
        curpath = foldername
    if os.path.isdir(curpath):
        #当前目录下所有的文件或文件夹
        files = os.listdir(curpath)
        for filename in files:
            getFiles(filename, curpath, filepaths) 
    else:
        filepaths.append(curpath) 
    Log.debug('end: FilesRunner getFiles')
    return  filepaths


def makeTotalSummaryReport(filenames, toatalsummary):
    totalsummaryReport = open(GlobalSetting.REPORTERROOTPATH \
                              + 'totalsummary.html', 'w')
    reporterstr = '<h1>total summary report<h1>'
    try:
        header = "<html><meta charset='utf-8'/><body>\n"
        reporterstr += header
        for filename in filenames:
            reporterstr += toatalsummary[filename]
        tail = '\n</body>\n</html>\n'
        reporterstr += tail
        totalsummaryReport.write(reporterstr)
        totalsummaryReport.flush()
        totalsummaryReport.close()
    except BaseException, e:
        print e
    try:
        sendmail('total autmation testing summary', reporterstr)
    except BaseException, e:
        Log.error('send mail error', e)


def runFilesTest():
    foldername = sys.argv[1]
    files = getFiles(foldername)
    print 'start files test'
    toatalsummary = {}
    for filename in files:
        sys.argv[1] = filename
        print 'excute %s file testing '% filename
        test = ExcelTestDriver(sys.argv)
        test.run()
        toatalsummary[filename] = test.fixture.summarybody
    makeTotalSummaryReport(files, toatalsummary)
    print 'test over'
    os._exit(0)


if __name__ == '__main__':
    runFilesTest()
