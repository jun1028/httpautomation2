# runner.GlobalSetting
# for stress test
import os
import sys
ITERATION = 0  # integer type,0 means don't iterate
RUNTIME = 0  # integer type,total run time(seconds),default is 0 ,means don't limit
#===============================================================================
# NEEDREPORTS means that it will produce report for every iteration
# if you run stress testing that only includes one test case
# suggest you set it False  
#===============================================================================
NEEDREPORTS = True
AUTOMATIONOPENREPORT = False
REPORTERROOTPATH = 'reports' + os.sep

SENDMAILFLAG = False
# specify test range
TESTCASEID_RANGE_FLAG = False  #    True or False
# TEST CASE ID RANGE:0 means the first test case,and  -1 means the last one 
TESTCASEID_START = '1'  # string type,like TESTCASEID_START = '001'
TESTCASEID_END   = '5'  # Don't include the testcaseid itself

# specify sheet name list will be tested, [] means all of sheet
SHEETS = ['lianxiang_test1']  # e.g. ['DDD', 'DDD']

def setTestcaseId_Range_Flag(param):
    global TESTCASEID_RANGE_FLAG  # Testcaseid_Range_Flag
    TESTCASEID_RANGE_FLAG = param

def setTestcaseIdRange(begin, end):
    global TESTCASEID_START, TESTCASEID_END  # Testcaseid_Start
    TESTCASEID_START = begin
    TESTCASEID_END = end

def getEncoding():
    encoding = 'gb2312'
    if sys.getfilesystemencoding().lower() == 'utf-8':
        encoding = 'UTF-8'
    return encoding

def init():
    global ITERATION, RUNTIME, NEEDREPORTS
    ITERATION = 1
    RUNTIME = 0
    NEEDREPORTS = True
    global SHEETS
    SHEETS = []

# test method    
if __name__ == '__main__':
    #init()
    print ITERATION
    print getEncoding()
