Feature: Open up 2 main windows and edit a multichat
    Window 1 opens the multi chat chooses new chat, shares with window 2, both windows make change make sure they end up with the same chat session

    Scenario: Open multichat and create a chat
        #Copied from send messages and establish encrypted link
        When I reset the email server dict
        When I clear the demux databases
        When I create a new demux 1
        When I create a new demux 2
        When I clear directory '/run/shm/demux1'
        When I clear directory '/run/shm/demux2'
        Given I set up demux 1 with the following values
          | myemail                    | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  | appdir          |
          | mlockett1@historygraph.io  | localhost  | 10026   | mlockett1 |           | localhost  | 10025    | mlockett1 |           | /run/shm/demux1 |
        Given I set up demux 2 with the following values
          | myemail                    | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  | appdir          |
          | mlockett2@historygraph.io  | localhost  | 10026   | mlockett2 |           | localhost  | 10025    | mlockett2 |           | /run/shm/demux2 |
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
        When I choose MultiChat from the Apps menu on main window 1
        When I press the bnNewMultiChat button on main window 1 manage multichats window
        Given I enter the following values into main window 1 new multichat window
          | teEmailAddress            | teChatName |
          | mlockett2@historygraph.io | MultiChat1 |
        When I press the bnOK button on main window 1 new multichat window
        Then there is 1 multichat in main window 1 manage multichats window and the multichat name is 'MultiChat1'
        Given I select multichat 1 in main window 1 manage multichats window and press 'bnEditMultiChat'
        Then the main window 1 edit multichat window has the title 'Multichat MultiChat1 mlockett1@historygraph.io'

        Given the main window 1 edit multichat displayed matches
          | 0      | 

        Then I add the following comment on the main window 1 edit multichat window 'Message 1'

        Given the main window 1 edit multichat displayed matches
          | 0          | 
          | Message 1  | 

        When I wait for the email server to run
        When I choose Send/Receive from the File menu on main window 2

        When I choose MultiChat from the Apps menu on main window 2
        Then there is 1 multichat in main window 2 manage multichats window and the multichat name is 'MultiChat1'
        Given I select multichat 1 in main window 2 manage multichats window and press 'bnEditMultiChat'
        Then the main window 2 edit multichat window has the title 'Multichat MultiChat1 mlockett2@historygraph.io'

        Then I wait for 2 seconds

        Given the main window 2 edit multichat displayed matches
          | 0          | 
          | Message 1  | 

        Then I add the following comment on the main window 2 edit multichat window 'Message 2'

        Given the main window 2 edit multichat displayed matches
          | 0          | 
          | Message 1  | 
          | Message 2  | 

        Then I wait for 2 seconds
        Given the main window 1 edit multichat displayed matches
          | 0          | 
          | Message 1  | 

        #Then I press the 'bnAddComment' button in main window 1 edit multichat window
        #Given I enter the following values into main window 1 new multichat comment window
        #  | teContent  |
        #  | Message 3  | 
        Then I add the following comment on the main window 1 edit multichat window 'Message 3'

        Given the main window 1 edit multichat displayed matches
          | 0          | 
          | Message 1  | 
          | Message 3  | 

        When I wait for the email server to run
        When I choose Send/Receive from the File menu on edit multichat window belonging to main window 2

        #When I choose MultiChat from the Apps menu on main window 2
        #Then there is 1 multichat in main window 2 manage multichats window and the multichat name is 'MultiChat1'
        #Given I select multichat 1 in main window 2 manage multichats window and press 'bnEditMultiChat'
        #Then the main window 2 edit multichat window has the title 'Multichat MultiChat1 mlockett2@historygraph.io'

        Given the main window 2 edit multichat displayed matches
          | 0          | 
          | Message 1  | 
          | Message 2  | 
          | Message 3  | 

        When I wait for the email server to run
        When I choose Send/Receive from the File menu on edit multichat window belonging to main window 1

        When I choose MultiChat from the Apps menu on main window 1
        Then there is 1 multichat in main window 1 manage multichats window and the multichat name is 'MultiChat1'
        Given I select multichat 1 in main window 1 manage multichats window and press 'bnEditMultiChat'
        Then the main window 1 edit multichat window has the title 'Multichat MultiChat1 mlockett1@historygraph.io'

        Given the main window 1 edit multichat displayed matches
          | 0          | 
          | Message 1  | 
          | Message 2  | 
          | Message 3  | 


