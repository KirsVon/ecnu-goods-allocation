# -*- coding: utf-8 -*-
# Description:
# Created: luchengkai 2021/05/20 14:57

from email.mime.text import MIMEText
import smtplib


def send_email(to_addr, subject, msg):
    from_addr = 'alert@jczh56.com'
    password = 'JCZh5566'
    msg = MIMEText(msg, 'html', 'utf-8')
    msg['From'] = u'<%s>' % from_addr
    msg['To'] = u'<%s>' % to_addr
    msg['Subject'] = subject
    smtp = smtplib.SMTP_SSL('smtp.exmail.qq.com', 465)
    smtp.login(from_addr, password)
    smtp.sendmail(from_addr, to_addr, msg.as_string())
