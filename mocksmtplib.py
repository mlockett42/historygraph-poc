#A mock of the python smtp library that allows us to test sending emails
#mocksmtplib.py

def SMTP(servername):
    return FakeSMTP()

class FakeSMTP(object):
    def sendmail(self, fromaddress, toaddresses, msg):
        pass

    def quit(self):
        pass

