# -*- coding: utf-8 -*-
from django.test import TestCase
import smtplib
import email.utils
from email.mime.text import MIMEText
from front.models import Mail
from .recv_server import Sh8MailProcess
import time
from .util import nomalize_recip, nomalize_body


class RecvMailTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.msg = MIMEText('This is the body of the message.')
        cls.frommail = 'author@example.com'
        cls.peer = 'recipient@example.com'
        cls.peernickname = 'recipient'
        super(RecvMailTest, cls).setUpClass()
        RecvMailTest.start_mail_server(cls)
        # for wait running server
        time.sleep(0.1)
        RecvMailTest.send_test_mail(cls)

    def send_test_mail(self):
        self.set_self_msg(self)

        server = smtplib.SMTP('127.0.0.1', 25)
        # show communication with the server
        try:
            server.sendmail(self.frommail,
                            [self.peer],
                            self.msg.as_string())
        finally:
            server.quit()
        # for wait to process mail    
        time.sleep(0.1)

    def set_self_msg(self):
        self.msg['To'] = email.utils.formataddr(('Recipient',
                                            self.peer))
        self.msg['From'] = email.utils.formataddr(('Author', self.frommail))
        self.msg['Subject'] = 'Simple test message'
        
    def start_mail_server(self):
        p = Sh8MailProcessForTest()
        p.daemon = True
        p.start()

    def test_exist_a_mail(self):
        mail = Mail.objects.all()
        self.assertTrue(mail)

    def test_check_mail_value(self):
        mail = Mail.objects.first()
        self.assertEquals(self.msg['From'], mail.sender)
        self.assertEquals(self.peernickname, mail.recipient)
        self.assertEquals(self.msg['Subject'], mail.subject)
        self.assertEquals(self.msg.get_payload(), mail.contents)


class MailUtil(TestCase):
    empty_mailfrom = ""
    empty_peer = ""
    
    def assert_after_nomalize_recipent(self, param_email, expected):
        result = nomalize_recip(param_email)
        self.assertEquals(expected, result)

    def make_default_parameter_body(self):
        body = {}
        body['From'] = "From <from@example.com>"
        body['To'] = "recipient@exam.com"
        return body

    def test_nomalize_reciepent(self):
        self.assert_after_nomalize_recipent(
                            "recipient@example.com", "recipient")
        self.assert_after_nomalize_recipent(
                            "recip@ent@example.com", "recip@ent")
        self.assert_after_nomalize_recipent(
                            "Recipient : <recipient@example.com>", "recipient")
        self.assert_after_nomalize_recipent(
                            "Recipient : < recipient@example.com >", "recipient")

    def test_nomalize_body_case_with_only_body(self):
        p_body = self.make_default_parameter_body()

        result_body = nomalize_body(p_body, self.empty_mailfrom)

        self.assertEquals("From <from@example.com>", result_body['From'])
        self.assertEquals("recipient", result_body['To'])

    def test_nomalize_body_case_with_mailfrom(self):
        p_body = self.make_default_parameter_body()
        p_mailfrom = "mailfrom@example.com"
        
        result_body = nomalize_body(p_body, p_mailfrom)
        
        self.assertEquals("From <from@example.com>", result_body['From'])
        self.assertEquals("recipient", result_body['To'])
        
        


class Sh8MailProcessForTest(Sh8MailProcess):
    def run(self):
        super(Sh8MailProcessForTest, self).run()
