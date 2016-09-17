#very hacky way of allowing SSL and still making tests pass
import smtplib
testingmode = False

def SMTP(*args):
    return smtplib.SMTP(*args)

def SMTP_SSL(*args):
    if testingmode:
        return smtplib.SMTP(*args)
    else:
        return smtplib.SMTP_SSL(*args)

