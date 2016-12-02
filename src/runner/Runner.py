#!/usr/bin/python
# -*- coding: UTF-8 -*-
'''
@author: water
'''
import os
import sys
#print os.path.split(os.path.realpath(__file__))[0] 
from runner.WikiRunner import WikiRunner
from runner.ExcelTestDriver import ExcelTestDriver
from runner.HtmlRunner import HtmlRunner
from runner.TextRunner import TextRunner

#UnicodeEncodeError: 'ascii' codec can't encode characters
reload(sys)
sys.setdefaultencoding('utf-8')

if __name__ == '__main__':
    lenparam = len(sys.argv)
    if lenparam < 2:
            sys.stderr.write("usage: python input-file output-file\n")
            sys.exit(-1)
        # output-file argv not exists,deafault name :Year-m-d-h-m-sreport.html
    else:
        filename = sys.argv[1]
        if filename.find(".txt") > 0:
            print 'start txt driver run test'
            TextRunner(sys.argv).run()
        elif filename.find(".html") > 0:
            print 'start HtmlRunner driver run test'
            HtmlRunner(sys.argv).run()
        elif filename.find(".xls") > 0:
            print 'start ExcelTestDriver driver run test'
            ExcelTestDriver(sys.argv).run()
        else:
            print 'start WikiRunner driver run test'
            WikiRunner(sys.argv).run()
