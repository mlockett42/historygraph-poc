from lettuce import *
from formsettings import *
from Demux import Demux
from PySide import QtTest
from PySide import QtCore

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
