Readme
======

Installation
------------

Under Ubuntu
------------

Checkout the historygraph libary
git clone https://github.com/mlockett42/historygraph.git

Checkout the historygraph-poc library
git clone https://github.com/mlockett42/historygraph-poc.git

Link the historygraph library into the correct place
cd ~/historygraph-poc
ln -s ../historygraph/historygraph historygraph


sudo apt-get install libssl-dev libffi-dev

Use these insstructions to get python qt4 / pyside to work in virtual env

Create the virtual environment
from the historygraph-poc directory

virtualenv .
source bin/activate
pip install pip --upgrade
pip install setuptools urllib3[secure]
pip install -r requirements.txt

pyside will take a long time to install.

Under Windows
-------------

Note only tested under Windows 7. Thanks to http://timmyreilly.azurewebsites.net/python-pip-virtualenv-installation-on-windows/
Download and install the git-scm tools for Windows
Also install Python 2.7.13 for Windows
Also install VC++ for Python compiler from http://aka.ms/vcpython27

Start up Git Bash shell

Type in
cd c:\
mkdir hg
cd hg

We will make all of our directories in here

Checkout the historygraph libary
git clone https://github.com/mlockett42/historygraph.git

Checkout the historygraph-poc library
git clone https://github.com/mlockett42/historygraph-poc.git

Link the historygraph library into the correct place
cd historygraph-poc
ln -s ../historygraph/historygraph historygraph
cd ..

pip install virtualenv

virtualenv .
Scripts\activate
pip install pip --upgrade
pip install setuptools
pip install urllib3[secure]
pip install -r requirements.txt


Running Tests (Linux)
---------------------

To run the unittests (TDD) run ./unittests

To run the BDD functional tests 
from the historygraph-poc directory
source bin/activate
export PYTHONPATH=$PWD
cd tests
lettuce

Running Tests (Windows)
---------------------

The tests fail under Windows because files get stored in non-portable locations

Running the Application
-----------------------
From the historygraph-poc directory
source bin/activate
python main.py

Running the Application in IDLE
-------------------------------
From the historygraph-poc directory
source bin/activate
python -m idlelib.idle main.py
(From this stackoverflow answer https://stackoverflow.com/a/38104835)

Testing for yourself
--------------------

Test under Ubuntu Linux
-----------------------

Set up a real test email server in AWS
--------------------------------------

In this section we shall test HistoryGraph-poc with two seperate fake accounts on our own email server.
This will involve setting up a test server in AWS you will need a domain you can test against and an SSH key
You will not need a SSL key for you test domain, we use unencrypted connections to the server to keep this easy.
These instruction assume familarity with Ubuntu Linux and AWS. Advanced users will be able to translate
into their favourite platform

sudo apt-get install libssl-dev libffi-dev

cd ~
mkdir 1
cd 1

git clone https://github.com/mlockett42/historygraph.git
git clone https://github.com/mlockett42/historygraph-poc.git
cd historygraph-poc
ln -s ../historygraph/historygraph historygraph

virtualenv .
source bin/activate
pip install pip --upgrade
pip install setuptools urllib3[secure]
pip install -r requirements.txt

pyside will take a long time to install.

cd ~
mkdir 2
cd 2

git clone https://github.com/mlockett42/historygraph.git
git clone https://github.com/mlockett42/historygraph-poc.git
cd historygraph-poc
ln -s ../historygraph/historygraph historygraph

virtualenv .
source bin/activate
pip install pip --upgrade
pip install setuptools urllib3[secure]
pip install -r requirements.txt

pyside will take a long time to install.

Create the test emailer in the cloud
------------------------------------

First we won't use SSL for this test so turn it off

Edit the 

Point your domain's DNS server's at AWS's
This page will have useful information on this
http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/MigratingDNS.html

Load your SSH public key into AWS under EC2 Dashboard -> Security and Network
->Key Pairs

Create an EC2 instance using the Ubuntu 16.04 Operating System and to be accessed
Getting an Elastic IP might make your server slightly more reliable
A t2.nano instance should be fine, if you have Free-tier on a t2.micro feel free
to use it

Launch the instance and wait for it to start

Be careful with the security group I normally give only my IP access to ports 25, 80 and 110

Connect to it with ssh

Update the packages with
sudo apt-get update ; sudo apt-get dist-upgrade --auto-remove && sudo apt-get autoremove

this may require you to update the kernel and reboot
We shall be basing our server on dovecot and these instructions (except for the parts relating to the SSL cert)
https://www.digitalocean.com/community/tutorials/how-to-set-up-a-postfix-e-mail-server-with-dovecot

sudo apt-get install postfix

Choose
Internet Site from the available configs
Set the mailname to your domain name

Edit /etc/postfix/master/cf and add the following

submission inet n       -       -       -       -       smtpd
  -o syslog_name=postfix/submission
  -o smtpd_tls_wrappermode=no
  -o smtpd_tls_security_level=encrypt
  -o smtpd_sasl_auth_enable=yes
  -o smtpd_recipient_restrictions=permit_mynetworks,permit_sasl_authenticated,reject
  -o milter_macro_daemon_name=ORIGINATING
  -o smtpd_sasl_type=dovecot
  -o smtpd_sasl_path=private/auth

Next type in

sudo mv /etc/postfix/main.cf /etc/postfix/main.cf.orig

Create a new main.cf file containing only the following

myhostname = mail.domain.com
myorigin = /etc/mailname
mydestination = mail.domain.com, domain.com, localhost, localhost.localdomain
relayhost =
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all

Edit /etc/mailname to contain the FQDN of your server

NExt we install dovecot at the console type in
sudo apt-get install dovecot-core dovecot-pop3d

Next we clear out the default dovecot config file
sudo mv /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.orig

Enter the following as a new dovecot config file /etc/dovecot/dovecot.conf

disable_plaintext_auth = no
mail_privileged_group = mail
mail_location = mbox:~/mail:INBOX=/var/mail/%u
userdb {
  driver = passwd
}
passdb {
  args = %s
  driver = pam
}
protocols = " pop3"

service auth {
  unix_listener /var/spool/postfix/private/auth {
    group = postfix
    mode = 0660
    user = postfix
  }
}
ssl=no

Type in the following to restart the services
sudo service postfix restart
sudo service dovecot restart

Add the following line to /etc/rc.local (before the exit 0 of course)
iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 25

Maybe ISP block port 25 so we can also use port 80
Then reboot

Type sudo reboot

Reconnect then create some new users
sudo adduser test1
sudo adduser test2

Don't forget the passwords you create for them

On you computer open the mypoplib.py and mysmtplib.py files and set testing_mode=True in both of them
For both the number 1 and 2 directories

-------------------------------------------
Next start up historygraph communcator in
the ~/1/historygraph-poc directory

python main.py

Go to the settings and configure the following

Email address = test1@mydomain.com
POP Server = mydomain.com
POP Server port=110
POP User Name=test1
POP Password=<password>
SMTP Server = mydomain.com
SMTP Server port=80 (or maybe 25)
SMTP User Name=test1
SMTP Password=<password>


Next start up historygraph communcator in
the ~/2/historygraph-poc directory

python main.py

Go to the settings and configure the following

Email address = test2@mydomain.com
POP Server = mydomain.com
POP Server port=110
POP User Name=test2
POP Password=<password>
SMTP Server = mydomain.com
SMTP Server port=80 (or maybe 25)
SMTP User Name=test2
SMTP Password=<password>

-------------------------------------

You may find to useful to setup an email client such as Thunderbird to watch the email traffic and
see what is going on. Use the same connection settings as above and dont forget to config the
email not to delete emails it has downloaded. The HistoryGraph-poc also will not delete them.

-------------------------------------

Shut down and restart the communicator after enter the settings - this updates the window titles

Open up the window for test1 and send a message to test 2

Go to the window for test2 do send and Receive the message from test1 should have arrive

Go to the window for test1 and choose Send/Receive

Go to the window for test2 and choose Send/Receive


In both communicators look at the contacts list they should see the other one and list them as 'Is encrypted'
If it says not encrypted they have not finished exchanging keys with each other

The two communicator will now have each others keys

In test1's communicator start a new checkers game and invite test2

Open the game and make the first move then choose Send/Receive from the menu. Note you need to make the first move to share the game

In test2 communicator window run Send/Receive and then look at the list of checkers games

You need to choose send/receive from the menus immediately after or before any move. This is not automatic (yet)

Test using a simulator local email server
-----------------------------------------
Open another console window
cd ~/1/historygraph-poc
source bin/activate
python
This will start the python prompt next type in
import testingmailserver
testingmailserver.StartTestingMailServer("historygraph.io", {"username":"password","username1":"password","username2":"password"})

The SMTP port is 10025 to POP3 port is 10026. The the server address is the first parameter. The second parameter
is a dict of usernames and passwords. You will also need to change the mypoplib.py and mysmtplib.py files to set
the testingmode variable to True, because we are emulating the test server

This will start the emailer running in another thread. Don't quit the Python interpreter that will close down the
email server.
Type in
testingmailserver.ResetMailDict()
if you wish to clear out all emails on this in memory server





