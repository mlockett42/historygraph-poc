#very hacky way of allowing SSL and still making tests pass
import poplib
testingmode = False

def POP3(*args):
    return poplib.POP3(*args)

def POP3_SSL(*args):
    if testingmode:
        return poplib.POP3(*args)
    else:
        return poplib.POP3_SSL(*args)

