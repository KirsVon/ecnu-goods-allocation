import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host="smtp.exmail.qq.com"  #设置服务器
mail_user="pangqiangnian@jczh56.com"    #用户名
mail_pass="r1104lR1104L"   #口令

sender = 'pangqiangnian@jczh56.com'
receivers = ['pangqiangnian@jczh56.com']

def mail(title, text):
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(text, 'plain', 'utf-8')
    message['From'] = Header("库存检测", 'utf-8')  # 发送者

    subject = title
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP_SSL(mail_host, 465)
        smtpObj.login(mail_user, mail_pass)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException as e:
        print("Error: 无法发送邮件")
        raise e


if __name__ == '__main__':
    subject = 'Python SMTP 邮件测试'
    body = 'Python 邮件发送测试...'
    mail(subject, body)
