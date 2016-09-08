from __future__ import print_function, absolute_import
from lettuce import *
from formsettings import *
from Demux import Demux
from PySide import QtTest
from PySide import QtCore
import utils
from formmain import FormMain
from PySide.QtGui import QMenu, QAction
from mock import patch


@step(u'I open the settings page')
def open_the_settings_page(step):
    world.formsettings = FormSettings(None, world.demux1)

@step(u'I create a new demux (\d+)')
def I_create_a_new_demux(step, demux_index):
    assert demux_index == '1' or demux_index == '2'
    setattr(world, 'demux' + demux_index, Demux(fromfile = '/tmp/testdump' + demux_index + '.db'))

@step(u'I clear the demux databases')
def I_clear_the_demux_databases(step):
    utils.removepath('/tmp/testdump1.db')
    utils.removepath('/tmp/testdump2.db')

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
        utils.log_output("k = ",k)
        utils.log_output("getattr(world.formsettings,k).toPlainText() = ",getattr(world.formsettings,k).toPlainText())
        utils.log_output("v = ",v)
        assert getattr(world.formsettings,k).toPlainText() == v

@step(u'I set up the demux with the following values')
def I_set_up_the_demux_with_the_following_values(step):
    assert len(step.hashes) == 1
    control_values = step.hashes[0]
    for (k, v) in control_values.iteritems():
        setattr(world.demux1, k, v)
        world.demux1.settingsstore.SaveSetting(k, v)

@step(u'I open the main window')
def I_open_the_main_window(step):
    world.formmain = FormMain(parent = None, demux=world.demux1)

@step(u'I choose Settings from the Options menu')
def I_choose_Settings_from_the_Options_menu(step):
    menu_name = "OPTIONS"
    menu_item_name = "SETTINGS"
    menu_found = None
    for menu in world.formmain.menubar.children():
        if type(menu) == QMenu and (menu.title().upper() == menu_name or menu.title().upper() == '&' + menu_name):
            menu_found = menu
    assert menu_found is not None
    
    menu_item_found = None
    for menu_item in menu_found.actions():
        utils.log_output("menu_item = ",menu_item)
        if type(menu_item) == QAction:
            utils.log_output("menu_item = ",menu_item.text())
        if type(menu_item) == QAction and (menu_item.text().upper() == menu_item_name or menu_item.text().upper() == '&' + menu_item_name):
            menu_item_found = menu_item
    assert menu_item_found is not None
    with patch.object(FormSettings, 'show') as mock_show:
        mock_show.return_value = None
        menu_item_found.trigger()
        world.formsettings = world.formmain.formsettings


