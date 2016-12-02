# -*- coding: UTF-8 -*-
'''
@author: water
'''
from log.Log import Log
from util.BaseUtils import *


def randnum(num):
    return  str(randNum(num))


def getProjectName(length):
    name = "Project"
    randstr1s = randstr(int(length))
    projectName = str(name) + str(randstr1s)
    print projectName
    Log.debug('projectName:', projectName)
    return projectName


def getTableName(length):
    name = "TableName"
    randstr1s = randstr(int(length))
    tableName = str(name) + str(randstr1s)
    print tableName
    Log.debug('TableName:', tableName)
    return tableName
    
if __name__ == '__main__':
    getTableName(10)