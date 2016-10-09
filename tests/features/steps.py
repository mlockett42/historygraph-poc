from __future__ import print_function, absolute_import
from lettuce import *
from formsettings import *
from formviewmessage import FormViewMessage
from formnewmessage import FormNewMessage
from formcontacts import FormContacts
from Demux import Demux
from PySide import QtTest
from PySide import QtCore
import utils
from formmain import FormMain
from PySide.QtGui import QMenu, QAction
from mock import patch
import testingmailserver
import time
import mysmtplib as smtplib
from formmanagecheckersgames import FormManageCheckersGames
from formcheckers import ImgWhiteSquare, ImgBlackSquare, ImgWhiteOnBlack, ImgBlackOnBlack


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

@step(u'I enter the following values into the settings page')
def I_enter_the_following_values(step):
    assert len(step.hashes) == 1
    control_values = step.hashes[0]
    for (k, v) in control_values.iteritems():
        QtTest.QTest.keyClicks(getattr(world.formsettings,k), v, 0, 10)

@step(u'I enter the following values into main window (\d+) (new message|new checkers game) window')
def I_enter_the_following_values_into_main_window_new_message_window(step, window_index, sub_window_type):
    assert len(step.hashes) == 1
    control_values = step.hashes[0]
    formmain = getattr(world, 'formmain' + window_index, None)
    if sub_window_type == "new message":
        formtarget = formmain.formnewmessage
    elif sub_window_type == "new checkers game":
        formtarget = formmain.form_manage_checkers_games.form_new_checkers_game
    assert formmain is not None, "Matching form not found"
    for (k, v) in control_values.iteritems():
        QtTest.QTest.keyClicks(getattr(formtarget,k), v, 0, 10)

@step(u'I press the (\w+) button on the settings windows')
def I_press_the_ok_button(step, buttonname):
    if buttonname == "OK":
        button = world.formsettings.bnOK
    elif buttonname == "Cancel":
        button = world.formsettings.bnCancel
    else:
        assert False
    QtTest.QTest.mouseClick(button, Qt.LeftButton)

@step(u'I press the (\w+) button on main window (\d+) (new message|manage checkers games|new checkers game) window')
def I_press_the_ok_button_on_main_window_1_new_message_window(step, buttonname, window_index, which_window):
    formmain = getattr(world, 'formmain' + window_index)
    if which_window == "new message":
        theform = formmain.formnewmessage
    elif which_window == "manage checkers games":
        theform = formmain.form_manage_checkers_games
    elif which_window == "new checkers game":
        theform = formmain.form_manage_checkers_games.form_new_checkers_game
    button = getattr(theform, buttonname, None)
    assert button is not None, "No matching button with that name, looking for " + buttonname
    with patch.object(FormSettings, 'show') as mock_show1:
        with patch.object(FormNewMessage, 'show') as mock_show2:
            with patch.object(FormViewMessage, 'show') as mock_show3:
                with patch.object(FormContacts, 'show') as mock_show4:
                    mock_show1.return_value = None
                    mock_show2.return_value = None
                    mock_show3.return_value = None
                    mock_show4.return_value = None
                    QtTest.QTest.mouseClick(button, Qt.LeftButton)

@step(u'Then I see following values')
def Then_I_see_the_following_values(step):
    assert len(step.hashes) == 1
    control_values = step.hashes[0]
    for (k, v) in control_values.iteritems():
        assert getattr(world.formsettings,k).toPlainText() == v

@step(u'I set up demux (\d+) with the following values')
def I_set_up_demux_with_the_following_values(step, demux_index):
    assert demux_index == '1' or demux_index == '2'
    assert len(step.hashes) == 1
    demux = getattr(world, 'demux' + demux_index)
    control_values = step.hashes[0]
    for (k, v) in control_values.iteritems():
        if k == 'popport' or k == 'smtpport':
            v = int(v)
        setattr(demux, k, v)
        demux.settingsstore.SaveSetting(k, v)

@step(u'I open main window (\d+)')
def I_open_main_window(step, form_index):
    assert form_index == '1' or form_index == '2'
    demux = getattr(world, 'demux' + form_index)
    setattr(world, 'formmain' + form_index, FormMain(parent = None, demux=demux))

@step(u'I choose (\w+|New Message|Send/Receive) from the (\w+) menu on main window (\d+)')
def I_choose_Settings_from_the_Options_menu(step, menu_item_name, menu_name, window_index):
    menu_name = menu_name.upper()
    menu_item_name = menu_item_name.upper()
    menu_found = None
    formmain = getattr(world, 'formmain' + window_index)
    for menu in formmain.menubar.children():
        if type(menu) == QMenu and (menu.title().upper() == menu_name or menu.title().upper() == '&' + menu_name):
            menu_found = menu
    assert menu_found is not None, "No matching menu was found"
    
    menu_item_found = None
    for menu_item in menu_found.actions():
        if type(menu_item) == QAction and (menu_item.text().upper() == menu_item_name or menu_item.text().upper() == '&' + menu_item_name):
            menu_item_found = menu_item
    assert menu_item_found is not None, "No matching menu item was found"
    with patch.object(FormSettings, 'show') as mock_show1:
        with patch.object(FormNewMessage, 'show') as mock_show2:
            with patch.object(FormViewMessage, 'show') as mock_show3:
                with patch.object(FormContacts, 'show') as mock_show4:
                    with patch.object(FormManageCheckersGames, 'show') as mock_show5:
                        mock_show1.return_value = None
                        mock_show2.return_value = None
                        mock_show3.return_value = None
                        mock_show4.return_value = None
                        mock_show5.return_value = None
                        menu_item_found.trigger()
                        if hasattr(formmain, "formsettings"):
                            world.formsettings = formmain.formsettings

@step(u'I reset the email server dict')
def I_reset_the_email_server_dict(step):
    testingmailserver.ResetMailDict()

@step(u'I wait for the email server to run')
def I_wait_for_the_email_server_to_run(step):
    time.sleep(0.1) #Give background thread a chance to run

@step(u'When I release the email server')
def when_i_release_the_email_server(step):
    world.mail_server_tests = world.mail_server_tests - 1
    if world.mail_server_tests <= 0:
        testingmailserver.StopTestingMailServer()

@step(u'there is exactly (\d+) message in main window (\d+) with subject \'([^\']*)\' and (is|is not) encrypted')
def there_is_exactly_one_message_in_main_window_2_with_subject_group1(step, num_messages, window_index, subject, encryption_status):
    formmain = getattr(world, 'formmain' + window_index)
    assert formmain.messageheaders.rowCount() == int(num_messages), "There must be exactly " + num_messages + " message " + str(formmain.messageheaders.rowCount())  + " found"
    assert formmain.messageheaders.item(int(num_messages) - 1,1).text() == subject, "Subject does not match " + str(formmain.messageheaders.item(0,1).text()) + " vs " + str(subject)
    expected_encryption_status = "Encrypted" if (encryption_status == "is") else "Not Encrypted"
    assert formmain.messageheaders.item(int(num_messages) - 1,3).text() == expected_encryption_status, "Message not flagged as " + expected_encryption_status + " actuall got " + formmain.messageheaders.item(int(num_messages) - 1,3).text()

@step(u'Then the email server has exactly (\d+) waiting message')
def then_the_email_server_has_exactly_1_waiting_message(step, num_messages):
    count = testingmailserver.GetTotalEmailCount()
    assert count == 1, "There must be exactly one email on the server " + str(count) + " found"

@step(u'When I open message (\d+) in main window (\d+)')
def when_i_open_message_1_in_main_window_2(step, message_index, window_index):
    formmain = getattr(world, 'formmain' + window_index)
    class MI(object):
        def __init__(self,row,column):
            self._row = row
            self._column = column
        def row(self):
            return self._row
        def column(self):
            return self._column
    formmain.messagedoubleclicked(MI(int(message_index),1))

@step(u'Then the body of the message in main window (\d+) view message window is \'([^\']*)\'')
def then_the_body_of_the_message_in_main_window_2_view_message_window_is_group1(step, window_index, body):
    formmain = getattr(world, 'formmain' + window_index)
    assert formmain.formviewmessage.teBody.toPlainText().find(body) == 0, "Body receive not the same as sent " + formmain.formviewmessage.teBody.toPlainText() + " vs " + body

@step(u'When I close the message window in main window (\d+)')
def When_I_close_the_message_window_in_main_window(step, window_index):
    formmain = getattr(world, 'formmain' + window_index)
    formmain.formviewmessage.close()

@step(u'there is 1 (contact|checkers game) in main window (\d+) (contact|manage checkers games) window and the (contacts|checkers game) name is \'([^\']*)\'')
def there_is_one_contact_in_main_window_contact_window(step, object_type, window_index, window_name, object_type2, object_name):
    formmain = getattr(world, 'formmain' + window_index)
    #assert object_type == object_type2
    if object_type == "contact":
        l = formmain.formcontacts.contacts
    else:
        l = formmain.form_manage_checkers_games.games
    assert l.rowCount() == 1, "1 " + object_type + " expected actually found " + str(l.rowCount())
    control_name = l.item(0,0).text()
    if control_name[0] == '<':
        control_name = control_name[1:]
    if control_name[-1] == '>':
        control_name = control_name[:-1]
    assert control_name == object_name, "Contact name does not match " + str(control_name) + " vs " + str(object_name)

@step(u'The contact \'([^\']*)\' in main window (\d+) has the same public key as main window (\d+) private key')
def the_contact_group1_in_main_window_2_has_the_same_public_key_as_main_window_1_private_key(step, contact_name, window_index1, window_index2):
    formmain1 = getattr(world, 'formmain' + window_index1)
    formmain2 = getattr(world, 'formmain' + window_index2)
    contacts = list(formmain1.demux.contactstore.GetContacts())
    assert len(contacts) == 1
    assert contacts[0].publickey == formmain2.demux.key.publickey().exportKey("PEM"), contacts[0].publickey + " vs " + formmain2.demux.key.publickey().exportKey("PEM")

@step(u'I select checkers game 1 in main window 1 manage checkers games window and press \'([^\']*)\'')
def then_select_checkers_game_1_in_main_window_1_manage_checkers_games_window_and_press_group1(step, button_name):
    formmain = getattr(world, 'formmain1', None)
    formtarget = formmain.form_manage_checkers_games
    assert formmain is not None, "Matching form not found"
    button = getattr(formtarget, button_name)
    #QtTest.QTest.mouseClick(formtarget.games, Qt.LeftButton ,pos=QtCore.QPoint(1,1))
    formtarget.games.setCurrentCell(0,0)
    selecteditems = formtarget.games.selectedItems()
    assert len(selecteditems) == 1, "Unexpected selected items " + str(selecteditems)
    QtTest.QTest.mouseClick(button, Qt.LeftButton)

@step(u'the main window 1 play checkers window has the title \'([^\']*)\'')
def then_the_main_window_1_play_checkers_window_has_the_title_group1(step, title):
    formmain = getattr(world, 'formmain1', None)
    formtarget = formmain.form_manage_checkers_games.form_play_checkers
    assert formmain is not None, "Matching form not found"
    assert formtarget.windowTitle() == title, "Title does not match " + str(formtarget.windowTitle()) + " vs " + str(title)

@step(u'Given the main window 1 play checkers window board displayed matches')
def given_the_main_window_1_play_checkers_window_board_displayed_matches(step):
    formmain = getattr(world, 'formmain1', None)
    formtarget = formmain.form_manage_checkers_games.form_play_checkers
    assert len(step.hashes) == 8, "step.hashes=" + str(step.hashes)
    pieces = list()
    for control_values in step.hashes:
        l = list()
        pieces.append(l)
        for k in range(8):
            l.append(control_values[str(k)])
    for y in range(8):
        for x in range(8):
            piece = pieces[y][x]
            cellwidget = formtarget.boardScreen.cellWidget(x,y)
            if piece == "":
                assert isinstance(cellwidget, ImgWhiteSquare) or isinstance(cellwidget, ImgBlackSquare), "piece == '', cellwidget = " + str(cellwidget) + "x = " + str(x) + " y = " + str(y)
            elif piece == "W":
                assert isinstance(cellwidget, ImgWhiteOnBlack), "piece == 'W', cellwidget = " + str(cellwidget) + "x = " + str(x) + " y = " + str(y)
            elif piece == "B":
                assert isinstance(cellwidget, ImgBlackOnBlack), "piece == 'B', cellwidget = " + str(cellwidget) + "x = " + str(x) + " y = " + str(y)
            else:
                assert False, "Unknown piece type '" + piece + "'"

@step(u'the main window 1 play checkers window current player is \'([^\']*)\'')
def then_the_main_window_1_play_checkers_window_current_player_is_group1(step, player_colour):
    formmain = getattr(world, 'formmain1', None)
    formtarget = formmain.form_manage_checkers_games.form_play_checkers
    assert formtarget.labelCurrentPlayer.text() == "Current Player: " + player_colour, "label says = " + formtarget.labelCurrentPlayer.text() + " expected " + "Current Player: " + player_colour

@step(u'Then click on square (\d+) (\d+)')
def then_click_on_square_x_y(step, x, y):
    formmain = getattr(world, 'formmain1', None)
    formtarget = formmain.form_manage_checkers_games.form_play_checkers
    x = int(x)
    y = int(y)
    cellwidget = formtarget.boardScreen.cellWidget(y,x)
    QtTest.QTest.mouseClick(cellwidget, Qt.LeftButton)

