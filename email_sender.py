import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import json

class EmailSender():
    def __init__(self, content='每周论文列表', 
                    file_path=""):
        f = open("configs/mail_config.json")
        configs = json.load(f)
        self.addr = configs['addr']
        self.pswd = configs['pswd']
        self.server = configs['server']
        self.sender_address = configs['sender_address']
        self.receiver_address = configs['receiver_address']
        self.content = content
        self.file_path = file_path
        self.mail = ""
        self.sent = False
        f.close()

    def generate_email(self):
        message = MIMEMultipart()
        message['From'] = Header("论文轮询服务", 'utf-8')
        message['To'] =  Header("stone", 'utf-8')
        subject = '每周论文'
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(MIMEText(self.content, 'plain', 'utf-8'))
        
        # 附件
        if self.file_path == '':
            return
        att1 = MIMEText(open(self.file_path, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        att1["Content-Disposition"] = 'attachment; filename="%s"'%self.file_path
        message.attach(att1)
        self.mail = message

    def send_email(self):
        self.generate_email()
        if self.mail == '':
            return
        try:

            smtpObj = smtplib.SMTP(self.server, 25)
            smtpObj.set_debuglevel(1)
            smtpObj.login(self.addr, self.pswd)
            smtpObj.set_debuglevel(1)
            smtpObj.sendmail(self.sender_address, self.receiver_address, self.mail.as_string())
            print("邮件发送成功")
            self.sent = True
        except smtplib.SMTPException:
            print("Error: 无法发送邮件")


if __name__ == "__main__":
    mail_sender = EmailSender(file_path='zips/list-2020-04-06.txt')
    mail_sender.send_email()