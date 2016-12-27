Feature: Open up 2 main windows send a message between them and check they are on each others contact lists and history graph contacts
    Window 1 must send a message to window 2 the message needs to be received
    afterwards there should be an exchange of livewire messages

    Scenario: Send_and_receive_message
        When I reset the email server dict
        When I clear the demux databases
        When I create a new demux 1
        When I create a new demux 2
        Given I set up demux 1 with the following values
          | myemail                    | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  |
          | mlockett1@historygraph.io  | localhost  | 10026   | mlockett1 |           | localhost  | 10025    | mlockett1 |           |
        Given I set up demux 2 with the following values
          | myemail                    | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  |
          | mlockett2@historygraph.io  | localhost  | 10026   | mlockett2 |           | localhost  | 10025    | mlockett2 |           |
        When I open main window 1
        When I open main window 2
        When I choose New Message from the File menu on main window 1
        Given I enter the following values into main window 1 new message window
          |  tesubject  |  teBody    | tetoaddress
          | Hello world | Frist post | mlockett2@historygraph.io
        When I press the bnOK button on main window 1 new message window
        When I wait for the email server to run
        Then the email server has exactly 1 waiting message
        When I choose Send/Receive from the File menu on main window 2
        Then the email server has exactly 1 waiting message
        Then there is exactly 1 message in main window 2 with subject 'Hello world' and is not encrypted

        When I open message 0 in main window 2
        Then the body of the message in main window 2 view message window is 'Frist post'
        When I close the message window in main window 2
        When I choose Contacts from the File menu on main window 2
        Then there is 1 contact in main window 2 contact window and the contacts name is 'mlockett1@historygraph.io'
        
        When I wait for the email server to run
        When I choose Send/Receive from the File menu on main window 1
        When I choose Contacts from the File menu on main window 1
        Then there is 1 contact in main window 1 contact window and the contacts name is 'mlockett2@historygraph.io'
        The contact 'mlockett2@historygraph.io' in main window 1 has the same public key as main window 2 private key
        When I choose Send/Receive from the File menu on main window 2
        The contact 'mlockett1@historygraph.io' in main window 2 has the same public key as main window 1 private key

        When I reset the email server dict
        When I choose New Message from the File menu on main window 1
        Given I enter the following values into main window 1 new message window
          |  tesubject       |  teBody     | tetoaddress
          | Hello encryption | Second post | mlockett2@historygraph.io
        When I press the bnOK button on main window 1 new message window
        When I wait for the email server to run
        Then the email server has exactly 1 waiting message
        When I choose Send/Receive from the File menu on main window 2
        #Then the email server has exactly 1 waiting message
        Then there is exactly 2 message in main window 2 with subject 'Hello encryption' and is encrypted
        
