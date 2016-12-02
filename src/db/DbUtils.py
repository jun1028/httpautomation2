# -*- coding: UTF-8 -*-
# package: util.DbUtils.DB
'''

@author: water, xh
'''
from log.Log import Log
from util.DbConfig import getDbCfg, CONTYPE_ORCALE, CONTYPE_MSSQL
import MySQLdb


class Singleton(object):  
    
    ''''' A python style singleton '''  
    def __new__(cls, *args, **kw):  
        if not hasattr(cls, '_instance'):  
            org = super(Singleton, cls)  
            cls._instance = org.__new__(cls, *args, **kw)  
        return cls._instance
    
class DB(Singleton):
    
    def __init__(self):
        self.dbhost = ''
        self.dbuser = ''
        self.dbpwd  = ''
        self.dbname = ''
        self.port   = ''
        self.dbcfg = {}
        self.conn = None
        self.cur = None
    
    def con2Db(self, conType = 0):
        self.dbcfg = getDbCfg(conType)
        self.setDbCfg() #
        if not self.conn:
            if conType == CONTYPE_ORCALE:
                print 'does not implement'
            elif conType == CONTYPE_MSSQL:
                print 'does not implement'
            else:
                self.con2mysql()
    
    def con2mysql(self):
        try:
            self.port = int(self.port)
            self.conn = MySQLdb.connect(self.dbhost, self.dbuser, self.dbpwd, self.dbname, self.port, charset='utf8')
            self.cur = self.conn.cursor()
        except MySQLdb.Error,e:
            print "Mysql connect failed! Error %d: %s" % (e.args[0], e.args[1])
            Log.error("Mysql Error %d: %s" % (e.args[0], e.args[1]))
            
    def setDbCfg(self):
        if self.dbcfg:
            for dbkey in self.dbcfg:
                try:
                    exec 'self.'  + dbkey + '="' + str(self.dbcfg[dbkey]) + '"'
                except BaseException, e:
                    Log.error('setDbCfg error', e)
    
    def execute(self, sql):
        result = False
        try:
            result = self.cur.execute(sql)
            Log.debug("execute sql statement!", sql)
            print "execute sql success"
            result = True
        except Exception, e:
            print "Execute Fail!"
            Log.error("execute sql fail!", e)
        return result
    
    def commit(self):
        bresult = True
        try:
            self.conn.commit()
        except:
            bresult = False
        return bresult

    def query(self, sql):
        results = None
        try:
            if self.cur.execute(sql):
                results = self.cur.fetchall()
        except:
            Log.error("query fail!")
        return results
       
    def close(self):
        try:
            self.cur.close()
            self.conn.close()
            print "close DB success!"
        except:
            Log.error("close fail!")
            print 'close DB fail!'


class DataManagement():
    
    _CLASSNAME = 'DataManagement'
        
if __name__ == '__main__':
    db = DB()
    db.con2Db()
    sql = "INSERT INTO `niudata1` (`shop_name`) VALUES ('中文')" 
    db.execute(sql)
    db.close()