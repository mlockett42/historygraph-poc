from __future__ import print_function, absolute_import
import os

def log_output(*args):
    with open('/tmp/output.txt', 'a') as f:
        print(*args, file=f)

def removepath(pathname):
    log_output("removepath(",pathname,")")
    if os.path.exists(pathname):
        os.remove(pathname)
    else:
        pass



