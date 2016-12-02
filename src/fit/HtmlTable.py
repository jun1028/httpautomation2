# -*- coding: UTF-8 -*-
#fit.HtmlTable.HtmlTable
'''
@author: water
'''


class HtmlTable(object):

    '''
        实现对所有类型的测试数据封装成标准的HTML TABLE
    '''
    _CLASSNAME = 'fit.HtmlTable.HtmlTable'

    tableDatas      = [] #
    tableDatasDict  = {} #
    curTableData    = [] #当前table data

    def __init__(self):
        '''
        Constructor
        '''
        pass

    def initTableDatas(self):
        tables = self.getTables()
        if tables:
            for table in tables:
                self.setTable(table)
                tablename = self.getTableByName()
                tableData = self.setTableData()
                self.tableDatas.append(tableData)
                self.tableDatasDict[tablename] = tableData

    def setTableData(self, startRowPos=0, startClumnPos=0, nrows=0, \
                                ncols=0, table=None):
        if nrows == 0:
            nrows = self.getnrows()
        if ncols == 0:
            ncols = self.getncols()
        for row in range(startRowPos, nrows):
            colData = []
            for col in range(startClumnPos, ncols):
                colData.append(self.getCellStrValue(row, col, table))
            self.curTableData.append(colData)
        return self.curTableData

    def getnrows(self):
        pass

    def getncols(self):
        pass

    def getTableNames(self):
        pass

    def getTableDataByName(self):
        return ''

    #获取所有的table data
    def getTableDatas(self):
        return self.tableDatas

    #获取当前的table data
    def getTableData(self):
        return self.curTableData

    #获取当前的table data
    def getTableDatasDict(self):
        return self.tableDatasDict

    def getCellStrValue(self, row, col, table=None):
        pass

