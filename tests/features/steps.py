from __future__ import print_function
from lettuce import *
from formsettings import *
from Demux import Demux
from PySide import QtTest
from PySide import QtCore

def log_output(*args):
    with open('/tmp/output.txt', 'a') as f:
        print(*args, file=f)


@step(u'I open the settings page')
def open_the_settings_page(step):
    world.formsettings = FormSettings(world.demux1)

@step(u'I create a new demux')
def I_create_a_new_demux(step):
    world.demux1 = Demux(fromfile = '/tmp/testdump1.db')

@step(u'I enter the following values')
def I_enter_the_following_values(step):
    assert len(step.hashes) == 1
    control_values = step.hashes[0]
    for (k, v) in control_values.iteritems():
        QtTest.QTest.keyClicks(getattr(world.formsettings,k), v, 0, 10)

@step(u'I press the (\w+) button')
def I_press_the_ok_button(step, buttonname):
    if buttonname == "OK":
        button = world.formsettings.bnOK
    elif buttonname == "Cancel":
        button = world.formsettings.bnCancel
    else:
        assert False
    QtTest.QTest.mouseClick(button, Qt.LeftButton)

@step(u'Then I see following values')
def Then_I_see_the_following_values(step):
    assert len(step.hashes) == 1
    control_values = step.hashes[0]
    for (k, v) in control_values.iteritems():
        assert getattr(world.formsettings,k).toPlainText() == v

@step(u'Go to the settings page')
def go_to_the_settings_page(step):
    demux = Demux(fromfile = '/tmp/testdump.db')
    form = FormSettings(demux)
    QtTest.QTest.keyClicks(form.teEmailAddress, "mlockett1@livewire.io", 0, 10)
    QtTest.QTest.keyClicks(form.tePOPServerName, "localhost1", 0, 10)
    QtTest.QTest.keyClicks(form.tePOPServerPort, "10026", 0, 10)
    QtTest.QTest.keyClicks(form.tePOPUserName, "mlockett1+1@livewire.io", 0, 10)
    QtTest.QTest.keyClicks(form.tePOPPassword, "password1", 0, 10)
    QtTest.QTest.keyClicks(form.teSMTPServerName, "localhost2", 0, 10)
    QtTest.QTest.keyClicks(form.teSMTPServerPort, "10025", 0, 10)
    QtTest.QTest.keyClicks(form.teSMTPUserName, "mlockett1+2@livewire.io", 0, 10)
    QtTest.QTest.keyClicks(form.teSMTPPassword, "password2", 0, 10)

    QtTest.QTest.mouseClick(form.bnOK, Qt.LeftButton)
    
    assert demux.myemail == "mlockett1@livewire.io"
    assert demux.popserver == "localhost1"
    assert demux.popport == "10026"
    assert demux.popuser == "mlockett1+1@livewire.io"
    assert demux.poppass == "password1"
    assert demux.smtpserver == "localhost2"
    assert demux.smtpuser == "mlockett1+2@livewire.io"
    assert demux.smtppass == "password2"
    assert demux.smtpport == "10025"

    assert demux.settingsstore.LoadSetting('myemail') == "mlockett1@livewire.io"
    assert demux.settingsstore.LoadSetting('smtpserver') == "localhost2"
    assert demux.settingsstore.LoadSettingInt('smtpport') == 10025
    assert demux.settingsstore.LoadSetting('smtpuser') == "mlockett1+2@livewire.io"
    assert demux.settingsstore.LoadSetting('smtppass') == "password2"
    assert demux.settingsstore.LoadSetting('popserver') == "localhost1"
    assert demux.settingsstore.LoadSetting('popuser') == "mlockett1+1@livewire.io"
    assert demux.settingsstore.LoadSetting('poppass') == "password1"
    assert demux.settingsstore.LoadSettingInt('popport') == 10026

    #Get a new demux from the database and test everything is loaded correctly
    demux = Demux(fromfile = '/tmp/testdump.db')
    form = FormSettings(demux)

    assert demux.myemail == "mlockett1@livewire.io"
    assert demux.popserver == "localhost1"
    assert demux.popport == 10026
    assert demux.popuser == "mlockett1+1@livewire.io"
    assert demux.poppass == "password1"
    assert demux.smtpserver == "localhost2"
    assert demux.smtpuser == "mlockett1+2@livewire.io"
    assert demux.smtppass == "password2"
    assert demux.smtpport == 10025

    assert demux.settingsstore.LoadSetting('myemail') == "mlockett1@livewire.io"
    assert demux.settingsstore.LoadSetting('smtpserver') == "localhost2"
    assert demux.settingsstore.LoadSettingInt('smtpport') == 10025
    assert demux.settingsstore.LoadSetting('smtpuser') == "mlockett1+2@livewire.io"
    assert demux.settingsstore.LoadSetting('smtppass') == "password2"
    assert demux.settingsstore.LoadSetting('popserver') == "localhost1"
    assert demux.settingsstore.LoadSetting('popuser') == "mlockett1+1@livewire.io"
    assert demux.settingsstore.LoadSetting('poppass') == "password1"
    assert demux.settingsstore.LoadSettingInt('popport') == 10026

    assert demux.myemail == form.teEmailAddress.toPlainText()
    assert demux.popport == int(form.tePOPServerPort.toPlainText())
    assert demux.popserver == form.tePOPServerName.toPlainText()
    assert demux.popuser == form.tePOPUserName.toPlainText()
    assert demux.poppass == form.tePOPPassword.toPlainText()
    assert demux.smtpserver == form.teSMTPServerName.toPlainText()
    assert demux.smtpport == int(form.teSMTPServerPort.toPlainText())
    assert demux.smtpuser == form.teSMTPUserName.toPlainText()
    assert demux.smtppass == form.teSMTPPassword.toPlainText()
    #assert False, 'This step must be implemented'
"""
@step(u'Fill in the field with the name "([^"]*)" with "([^"]*)"')
def fill_in_the_field_with_the_name_group1_with_group2(step, group1, group2):
    assert False, 'This step must be implemented'
@step(u'Fill in the field with the name "([^"]*)" with ""')
def fill_in_the_field_with_the_name_group1_with(step, group1):
    assert False, 'This step must be implemented'
@step(u'Then I see that the settings contain:')
def then_i_see_that_the_settings_contain(step):
    assert False, 'This step must be implemented'
@step(u'email_address       | pop_server | pop_port | pop_username | pop_password | smtp_server | smtp_port | smtp_username | smtp_password |')
def email_address_pop_server_pop_port_pop_username_pop_password_smtp_server_smtp_port_smtp_username_smtp_password(step):
    assert False, 'This step must be implemented'
@step(u'mlockett1@timeca.io | localhost  | 10025    | mlockett1    |              | localhost   | 10026     | mlockett1     |               |')
def mlockett1_timeca_io_localhost_10025_mlockett1_localhost_10026_mlockett1(step):
    assert False, 'This step must be implemented'
"""
