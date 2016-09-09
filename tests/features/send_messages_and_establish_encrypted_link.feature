Feature: Open up 2 main windows send a message between them and check they are on each others contact lists and livewire contacts
    Window 1 must send a message to window 2 the message needs to be received
    afterwards there should be an exchange of livewire messages

    Scenario: Open main form then setting form and verify correct information is present
        When I reset the email server dict
        When I clear the demux databases
        When I create a new demux 1
        When I create a new demux 2
        Given I set up demux 1 with the following values
          | myemail              | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  |
          | mlockett1@localhost  | localhost  | 10025   | mlockett1 |           | localhost  | 10026    | mlockett1 |           |
        Given I set up demux 2 with the following values
          | myemail              | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  |
          | mlockett2@localhost  | localhost  | 10025   | mlockett2 |           | localhost  | 10026    | mlockett2 |           |
        When I open main window 1
        When I open main window 2
        #When I press New Message on main window 1
        #Given I enter the following values into main window 1 new message window
        #  |  Subject    |  Body      | To
        #  | Hello world | Frist post | mlockett2
        #When I press the send button on main window 1 new message window
        #When I wait for the email server to run
        #When I press the Send/Receive button on main window 2
        #Then there is one message in main window 2 with subject 'Hello world'
        #When I open message 1 in main window 2
        #Then the body of the message is 'Frist post'
        #When I close the message window in main window 2
        #When I open the contact window in main window 2
        #Then there is one contact in main window 2 contact window
        #Then the one contact is 'mlocket1@localhost' in main window 2 contact window
        #The contact 'mlockett1@localhost' in main window 2 has the same public key as main window 1 private key
        
        #When I wait for the email server to run
        #When I press the Send/Receive button on main window 1
        #When I open the contact window in main window 1
        #Then there is one contact in main window 1 contact window
        #Then the one contact is 'mlockett2@localhost'
        #The contact 'mlockett2@localhost' in main window 1 has the same public key as main window 2 private key

