#A mock of the python pop library that allows us to test getting emails
#mockpoplib.py

def POP3(host, message):
    return FakePOP(message)

class FakePOP(object):
    def set_debuglevel(self, level):
        #Not implemented
        assert False

    def getwelcome(self):
        return "Hello from Mock POP Lib"

    def user(self, username):
        #Do nothing
        pass

    def pass_(self, password):
        #Do nothing
        pass

    def apop(self, user, secret):
        #Do nothing
        pass

    def rpop(self, user):
        #Do nothing
        pass

    def stat(self):
        #Not implemented
        assert False

    def list(self, *which):
        assert len(which) == 0
        return ('+OK mockpoplib', ['1 16805'], 17)

    def retr(self, which):
        assert which == 1
        if self.message == 0:
            return ["+OK mockpoplib", """From nobody Mon Dec 30 17:45:19 2013
Delivered-To: livewiretest2@gmail.com
Received: by 10.96.28.165 with SMTP id c5csp418840qdh;
 Mon, 30 Dec 2013 01:12:41 -0800 (PST)
Return-Path: <mlockett42@gmail.com>
Received-SPF: pass (google.com: domain of mlockett42@gmail.com designates
 10.112.141.225 as permitted sender) client-ip=10.112.141.225
Authentication-Results: mr.google.com;
 spf=pass (google.com: domain of mlockett42@gmail.com designates 10.112.141.225
 as permitted sender) smtp.mail=mlockett42@gmail.com;
 dkim=pass header.i=@gmail.com
 X-Received: from mr.google.com ([10.112.141.225])
 by 10.112.141.225 with SMTP id rr1mr8832104lbb.59.1388394761135 (num_hops = 1);

 Mon, 30 Dec 2013 01:12:41 -0800 (PST)
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=gmail.com; s=20120113;
 h=mime-version:sender:date:message-id:subject:from:to:content-type;
 bh=TwU2PeS2Gok1uwEklXvhLL3W6fsuYNn5mNVZYJwtKkY=;
 b=LBjUltw+iQ82DhrTQUTUYwSbyaFWIgT2I8lXOpMya37mqNtg8+yl0gGpagRg1u9LNw
 hdazNT4H+gLKEgCwucOd5lrhUO90r225BKwhBsBdG6EZZCUNo8OqYU3HfQklhGX2cK60
 pW79CnAkVmSnwdPYaHPuFZXsmhZvM3/fZ4JEwBK3hbSpOEtvjtFHRj+cCq4ax8yQ7vzX
 z17nzTPbqS/MmHyVmTsI4jiEB5kYRfUhTs+cZYevgo04lWz6ZJ8UngZkrySwR6OhCk2i
 u//P/cKBUw42sfLZZqBjzUcR+WMLWgL03xsVnmUSze2UQzRgoSiFrFBYAzaSLYeqT3of
 3lJA==
MIME-Version: 1.0
X-Received: by 10.112.141.225 with SMTP id rr1mr8832104lbb.59.1388394761131;
 Mon, 30 Dec 2013 01:12:41 -0800 (PST)
Sender: mlockett42@gmail.com
Received: by 10.112.57.47 with HTTP; Mon, 30 Dec 2013 01:12:41 -0800 (PST)
Date: Mon, 30 Dec 2013 17:12:41 +0800
X-Google-Sender-Auth: cwWnFfb_w3aQg3O2Dopv1bcY5ds
Message-ID: <CAMvA9yMfZNtiOhzVGCQjO7fgpTkGxZMm7rRuW9XBMhqL-qQEVQ@mail.gmail.com>

Subject: Hello world
From: Mark Lockett <mlockett@bigpond.com>
To: livewiretest2@gmail.com
Content-Type: multipart/alternative; boundary=001a11c3415c8b9b7d04eebcd85f

--001a11c3415c8b9b7d04eebcd85f
Content-Type: text/plain; charset=ISO-8859-1

test body
hello

--001a11c3415c8b9b7d04eebcd85f
Content-Type: text/html; charset=ISO-8859-1

<div dir="ltr">test body<div>hello</div></div>

--001a11c3415c8b9b7d04eebcd85f--
"""]
        elif self.message == 1:
            return ["+OK mockpoplib", """From nobody Mon Dec 30 17:45:19 2013
Delivered-To: livewiretest2@gmail.com
Received: by 10.96.28.165 with SMTP id c5csp418840qdh;
 Mon, 30 Dec 2013 01:12:41 -0800 (PST)
Return-Path: <mlockett42@gmail.com>
Received-SPF: pass (google.com: domain of mlockett42@gmail.com designates
 10.112.141.225 as permitted sender) client-ip=10.112.141.225
Authentication-Results: mr.google.com;
 spf=pass (google.com: domain of mlockett42@gmail.com designates 10.112.141.225
 as permitted sender) smtp.mail=mlockett42@gmail.com;
 dkim=pass header.i=@gmail.com
 X-Received: from mr.google.com ([10.112.141.225])
 by 10.112.141.225 with SMTP id rr1mr8832104lbb.59.1388394761135 (num_hops = 1);

 Mon, 30 Dec 2013 01:12:41 -0800 (PST)
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=gmail.com; s=20120113;
 h=mime-version:sender:date:message-id:subject:from:to:content-type;
 bh=TwU2PeS2Gok1uwEklXvhLL3W6fsuYNn5mNVZYJwtKkY=;
 b=LBjUltw+iQ82DhrTQUTUYwSbyaFWIgT2I8lXOpMya37mqNtg8+yl0gGpagRg1u9LNw
 hdazNT4H+gLKEgCwucOd5lrhUO90r225BKwhBsBdG6EZZCUNo8OqYU3HfQklhGX2cK60
 pW79CnAkVmSnwdPYaHPuFZXsmhZvM3/fZ4JEwBK3hbSpOEtvjtFHRj+cCq4ax8yQ7vzX
 z17nzTPbqS/MmHyVmTsI4jiEB5kYRfUhTs+cZYevgo04lWz6ZJ8UngZkrySwR6OhCk2i
 u//P/cKBUw42sfLZZqBjzUcR+WMLWgL03xsVnmUSze2UQzRgoSiFrFBYAzaSLYeqT3of
 3lJA==
MIME-Version: 1.0
X-Received: by 10.112.141.225 with SMTP id rr1mr8832104lbb.59.1388394761131;
 Mon, 30 Dec 2013 01:12:41 -0800 (PST)
Sender: mlockett42@gmail.com
Received: by 10.112.57.47 with HTTP; Mon, 30 Dec 2013 01:12:41 -0800 (PST)
Date: Mon, 30 Dec 2013 17:12:41 +0800
X-Google-Sender-Auth: cwWnFfb_w3aQg3O2Dopv1bcY5ds
Message-ID: <CAMvA9yMfZNtiOhzVGCQjO7fgpTkGxZMm7rRuW9XBMhqL-qQEVQ@mail.gmail.com>

Subject: Hello world
From: <mlockett42@gmail.com>
To: livewiretest2@gmail.com
Content-Type: multipart/alternative; boundary=001a11c3415c8b9b7d04eebcd85f

--001a11c3415c8b9b7d04eebcd85f
Content-Type: text/plain; charset=ISO-8859-1

test body
hello

======================================================================================
Livewire enabled emailer http://wwww.livewirecommunicator.org (mlockett@bigpond.com)
======================================================================================


--001a11c3415c8b9b7d04eebcd85f
Content-Type: text/html; charset=ISO-8859-1

<div dir="ltr">test body<div>hello</div></div>

--001a11c3415c8b9b7d04eebcd85f--
"""]
        else:
            assert False
            
    def dele(self, which):
        #Not implemented
        assert False

    def rset(self):
        #Not implemented
        assert False

    def noop(self):
        #Do nothing
        pass

    def quit(self):
        #Do nothing
        pass

    def top(self, which, howmuch):
        #Not implemented
        assert False

    def uidl(self, *which):
        #Not implemented
        assert False

    def __init__(self, message):
        self.message = message
