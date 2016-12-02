from util.BaseUtils import getTime
import os

LOG_FILE = 'log' + os.sep +  'log_' + getTime() + '.log'
LOG_LEVEL = 'debug' # debug,info,warn,error,critical
LOG_FILEMODE = 'w+' #'a','r', 'w', 'r+', 'w'
