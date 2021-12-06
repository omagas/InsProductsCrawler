#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 18:11:44 2020
@ref:https://www.learncodewithmike.com/2020/02/python-email.htmlreg
@author: apple
"""


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import configparser

#load configure
config = configparser.ConfigParser()
config.read('properties.ini')
notify_subject=config['PRO']['subject']
notify_from=config['PRO']['from']
notify_to=config['PRO']['to']
notify_cc=config['PRO']['cc']
notify_uatcc=config['UAT']['uatcc']
smtp_id=config['PRO']['smtp_id']
smtp_pw=config['PRO']['smtp_pw']

def send_message(datetime_str,datahtml):
    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = notify_subject  #郵件標題
    content["from"] = notify_from  #寄件者
    content["to"] = notify_to #收件者
    content["cc"] = notify_cc #cc
    part2 = MIMEText(datahtml, 'html')
    content.attach(MIMEText("python send email "+datetime_str))  #郵件內容
    content.attach(part2)
    
    
    
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(smtp_id, smtp_pw)  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            smtp.quit()
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)
            smtp.quit()
            
            
def send_message_uat(datetime_str,datahtml):
    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = "[TEST]"+notify_subject  #郵件標題
    content["from"] = notify_from  #寄件者
    content["to"] = notify_to #收件者
    content["cc"] = notify_uatcc #cc
    part2 = MIMEText(datahtml, 'html')
    content.attach(MIMEText("[TEST] python send email "+datetime_str))  #郵件內容
    content.attach(part2)
    
    
    
    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(smtp_id, smtp_pw)  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            smtp.quit()
            print("[TEST]Complete!")
        except Exception as e:
            print("[TEST]Error message: ", e)
            smtp.quit()