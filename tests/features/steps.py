from lettuce import *
from formsettings import *
from Demux import Demux

@step(u'Go to the settings page')
def go_to_the_settings_page(step):
    form = FormSettings(Demux('', '', 0, '', '', '', '', '', 0))

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
