#!/usr/bin/env python
# coding: utf-8

# This little project is hosted at: <https://gist.github.com/1455741>
# Copyright 2011-2012 Álvaro Justen [alvarojusten at gmail dot com]
# License: GPL <http://www.gnu.org/copyleft/gpl.html>

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from mimetypes import guess_type
from email.encoders import encode_base64
from getpass import getpass
import smtplib
from os.path import basename


class EmailConnection(object):
    def __init__(self, server, username, password):
        if ':' in server:
            data = server.split(':')
            self.server = data[0]
            self.port = int(data[1])
        else:
            self.server = server
            self.port = 25
        self.username = username
        self.password = password
        self.connect()

    def connect(self):
        self.connection = smtplib.SMTP(self.server, self.port)
        # self.connection.ehlo()
        self.connection.starttls()
        # self.connection.ehlo()
        self.connection.login(self.username, self.password)

    def send(self, send_from, send_to, subject, text, files):

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = send_to  
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        for f in files or []:
            with open(f, "rb") as fil: 
                ext = f.split('.')[-1:]
                attachedfile = MIMEApplication(fil.read(), _subtype = ext)
                attachedfile.add_header(
                    'content-disposition', 'attachment', filename=basename(f) )
            msg.attach(attachedfile)


        return self.connection.sendmail(send_from, send_to, msg.as_string())

    def close(self):
        self.connection.close()
