# -*- coding: UTF-8 -*-
'''
@author: water
'''
DEFAULT_CONTYPE = 0
CONTYPE_MYSQL   = 0
CONTYPE_MSSQL   = 1
CONTYPE_ORCALE  = 2

MYSQLDB = {
'dbhost':'121.41.76.135',
'dbuser': 'dreambox',
'dbpwd' :'dream613',
'dbname':'analy_db',
'port'  :3306
}

MSSQLDB = {}

ORCALEDB = {}

def getDbCfg(dbType=DEFAULT_CONTYPE):
    dbconfg = {}
    if dbType == CONTYPE_MYSQL:
        dbconfg = MYSQLDB
    elif dbType == CONTYPE_MSSQL:
        dbconfg = MYSQLDB
    elif dbType == CONTYPE_ORCALE:
        dbconfg = ORCALEDB
    return dbconfg

def init():
    global DEFAULTHOST, DEFAULTUSER, DEFAULTPWD, DEFAULTDBNAME, DEFAULTDBNAMEPORT
