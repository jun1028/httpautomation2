# -*- coding: UTF-8 -*-
from cfg.MailConf import DEFAULTTOMAILRECEIVERFILE, SENDER, SMTPSERVER, USERNAME, \
    PWD, USEDEFAULTMAIL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from log.Log import Log
from os.path import os
import smtplib
import time


#from email.mime.image import MIMEImage
def getToMaillist(receiverfile=None):
    receiverList = []
    if not receiverfile:
        receiverfile = DEFAULTTOMAILRECEIVERFILE
    fp = open(receiverfile)
    lines = fp.readlines()
    fp.close()
    for line in lines:
        if line.find('#') > -1:
            continue
        for receiver in line.split(';'):
            if len(receiver) > 1:
                receiverList.append(receiver)
    return receiverList


def genAttchment(attachment, name='test_report.html'):
    att = MIMEText(open(attachment, 'rb').read(), 'html', 'utf-8')
    att["Content-Type"] = 'application/octet-stream'
    att["Content-Disposition"] = 'attachment; filename=%s' % name
    return att


def sendmail(subject, text, attachment1=None, \
             attachment2=None, receiver=''):
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    #“发件人和收件人参数没有进行定义,解决相关邮箱的554, 'DT:SPM的错误
    msgRoot['from'] = SENDER
    msgRoot['to']   = 'zzj@moojnn.com'
    #add utf-8,避免邮件正文乱码， content["Accept-Charset"]  = "ISO-8859-1,utf-8"
    content = MIMEText('<b>' + text + '</b>', 'html', 'utf-8')
    content["Accept-Language"] = "zh-CN"
    content["Accept-Charset"]  = "ISO-8859-1,utf-8"
    msgRoot.attach(content)
    if attachment1 and os.path.exists(attachment1):
        msgRoot.attach(genAttchment(attachment1))
#    smtp = smtplib.SMTP_SSL() #ssl 连接
    try:
        smtp = smtplib.SMTP(SMTPSERVER)
    except BaseException, e:
        Log.debug('mail server connect fail', e)
        return
    smtp.login(USERNAME, PWD)
    if USEDEFAULTMAIL:
        try:
            receivers = getToMaillist()
        except Exception, e:
            Log.debug('get mail list fail!', e)
    else:
        if receiver.find('@') > -1:
            receivers = receiver.split(';')
        else:
            message = 'receiver is null'
            Log.debug(message)
            print message
            return
    smtp.sendmail(SENDER, receivers, msgRoot.as_string())
    print 'send ok, please check your mail'
    time.sleep(10)
    smtp.quit()

if __name__ == '__main__':
    sendmail(' test report', 'This E-mail sent automatically by the automation testing platform!' \
        ) #attachment1 = 'x.html'