from util.BaseUtils import getTime
import os

rootlog = 'log'
if not os.path.exists(rootlog):
    os.mkdir(rootlog)
LOG_FILE = rootlog + os.sep + 'log_' + getTime() + '.log'
LOG_LEVEL = 'debug' # debug,info,warn,error,critical
LOG_FILEMODE = 'w+' #'a','r', 'w', 'r+', 'w'
