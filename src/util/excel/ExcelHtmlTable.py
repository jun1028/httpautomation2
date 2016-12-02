# -*- coding: UTF-8 -*-
'''
@author: water
'''
# -*- coding: UTF-8 -*-
# package: fit.ExcelHtmlTable.ExcelHtmlTable
from fit.HtmlTable import HtmlTable
from log.Log import Log
import os
import xlrd
'''
@author: Water.Zhang
'''


class ExcelHtmlTable(HtmlTable):

    '''
      ExcelHtmlTable
    '''
    _CLASSNAME = 'fit.ExcelHtmlTable.ExcelHtmlTable'

    numOfShs = 0
    lShNames = []
    curSheet = None # current Sheet class 

    __xlBook = None
    filename = ''

    def openExcel(self, filename, filepath = None):
        try:
            if filepath is not None:
                filename = filepath + filename
            else:
                filename = os.path.abspath(filename)
            if os.path.exists(filename):  
                print 'openExcel excel file'
                self.filename = filename
                self.__xlBook = xlrd.open_workbook(filename)
                self.numOfShs = self.__xlBook.nsheets
                self.lShNames = self.__xlBook.sheet_names()
                self.curSheet = self.__xlBook.sheet_by_index(0)
            else:
                print str(filename) + "Error: Excel File not exist in this path" 
                raise IOError
        except BaseException, e:
            print e

    def initTableDatas(self):
        shNames = self.getShNameList()
        if shNames:
            for shName in shNames:
                if shName.lower().find("test") == -1:
                    continue
                self.getShByName(shName)
                tablename = shName
                self.curTableData = []
                self.setTableData()
                self.tableDatas.append(self.curTableData)
                self.tableDatasDict[tablename] = self.curTableData

    def setTableData(self, startRowPos=0, startClumnPos=0, nrows=0, \
                                ncols=0):
        if nrows == 0:
            nrows = self.getnrows()
        if ncols == 0:
            ncols = self.getncols()
        startRowPos, startClumnPos = self.getStartColumnPos()
        for row in range(startRowPos, nrows):
            colData = []
            for col in range(startClumnPos, ncols):
                colData.append(self.getCellStrValue(row, col))
            self.curTableData.append(colData)

    def getTableNames(self):
        return self.lShNames

    def getShNameList(self):
        return self.lShNames

    def getTableDataByName(self, tableName):
        if not self.tableDatasDict:
            self.initTableDatas()
        if self.tableDatasDict:
            return self.tableDatasDict[tableName]
        else:
            return None

    def getShByName(self, name):
        sheet = None
        try:
            sheet = self.__xlBook.sheet_by_name(name)
            self.setSheet(sheet)
        except BaseException, e:
            Log.error('specify sheet does not exist')
            Log.error(e)
        return sheet

    def getShByIndex(self, index):
        sheet = None
        try:
            sheet = self.__xlBook.sheet_by_index(index)
            self.setSheet(sheet)
        except IndexError, e:
            Log.error('index error,the max index is:' + str(self.numOfShs))
            Log.error(e) 
        return sheet

    def getCell(self, row, col, sheet=None):
        cell = None
        if sheet is None:
            sheet = self.curSheet
        try:
            cell = sheet.cell(rowx=row, colx=col)
        except BaseException, e:
            print e
        return cell

    def getCellStrValue(self, row, col, sheet = None):
        value = ''
        if sheet is None:
            sheet = self.curSheet
        try:
            value = self.convertToStr(sheet.cell_type(rowx=row, colx=col), \
                                       sheet.cell_value(rowx=row, colx=col))
            value = value.encode('UTF-8')
        except BaseException, e:
            Log.error('sheet error', sheet.name)
            Log.error('getCellStrValue error', e)
            Log.error('sheet, nrows', sheet.nrows)
            Log.error('sheet ncols', sheet.ncols)
            Log.error('sheet row', row)
            Log.error('sheet col', col)
        return value

    def getCurSheet(self):
        return self.curSheet

    def getnrows(self, sheet = None):
        return self.curSheet.nrows

    def getncols(self, sheet = None):
        return self.curSheet.ncols 

    def getRow(self, index, sheet = None):
        if sheet is None:
            sheet = self.curSheet
        rows = sheet.row(index)
        return rows

    #定位不为为空某列某行
    def getStartColumnPos(self):
        startColumnPos = 0
        startRowPos    = 0 
        exitloopflg = False
        for row in range(0, 5):
            for col in range(0, 3):
                if(self.getCellStrValue(row, col)):
                    startColumnPos = col
                    startRowPos    = row
                    exitloopflg = True
                    break
            if exitloopflg:
                break
        return startRowPos, startColumnPos

    def setSheet(self, sheet):
        self.curSheet = sheet

#     Type symbol     Type number Python value 
#     XL_CELL_EMPTY   0           empty string u'' 
#     XL_CELL_TEXT    1           a Unicode string 
#     XL_CELL_NUMBER  2           float
#     XL_CELL_DATE    3           float
#     XL_CELL_BOOLEAN 4           int; 1 means TRUE, 0 means FALSE 
#     XL_CELL_ERROR   5           int representing internal Excel codes; for a text representation, refer to the supplied dictionary error_text_from_code 
#     XL_CELL_BLANK   6           empty string u''. Note: this type will appear only when open_workbook(..., formatting_info=True) is used. 
    def convertToStr(self, cellType, cellValue):
        value = ''
        if cellType == 0 or cellType == 6:
            pass
        elif cellType == 1:
            value = cellValue
        elif cellType == 2:
            value = str(int(cellValue))
        elif cellType == 3: ###need rewrite 
            value = str(float(cellValue))
        elif cellType == 4:
            value = str(bool(cellValue))
        else:
            value = str(cellValue)
        return value

if __name__ == "__main__":
    test = ExcelHtmlTable()
    test.openExcel('test.xlsx')
#    test.initTableDatas()
#    print test.getTableDatas()
    print test.getStartColumnPos()
  #  print test.getTableData()
#    sheet = test.getShByIndex(0)
#    for rx in range(sheet.nrows):
#        print sheet.row(rx)
#    print test.getCellStrValue(6, 4, sheet)
#    print test.getCellStrValue(6, 0, sheet),
#    print test.getCellStrValue(7, 4, sheet)
#    print test.getCellStrValue(7, 0, sheet)
#    print test.curSheet.name
#    print test.getRow(0)
    #sheet = test.getShByName(u'stat')