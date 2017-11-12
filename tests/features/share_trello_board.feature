Feature: Open up 2 main windows and edit a shared trello board
    Window 1 opens the trello board chooses new board, shares with window 2, both windows make change make sure they end up with the same board

    Scenario: Open trello board and make some changes
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
        When I choose Trello from the Apps menu on main window 1
        When I press the bnNewBoard button on main window 1 manage trello boards window
        Given I enter the following values into main window 1 new trello board window
          | teEmailAddress            | teBoardName |
          | mlockett2@historygraph.io | Trello1     |
        When I press the bnOK button on main window 1 new trello board window
        Then there is 1 trello board in main window 1 manage trello boards window and the trello board name is 'Trello1'
        Given I select trello board 1 in main window 1 manage trello boards window and press 'bnEditBoard'
        Then the main window 1 edit trello board window has the title 'Trello Board Trello1 mlockett1@historygraph.io'

        Given the main window 1 trello board displayed matches
          | 0      | 
          | List 1 | 

        Then I press the 'bnAddList' button in main window 1 edit trello board window cell 0, 1

        Given the main window 1 trello board displayed matches
          | 0      | 1      |
          | List 1 | List 2 |

        Then edit in the main window 1 trello board 'teContent' in cell 0, 1 and change to 'My List'

        Given the main window 1 trello board displayed matches
          | 0      | 1       |
          | List 1 | My List |

        Then I press the 'bnSave' button in main window 1 edit trello board window cell 0, 1        

        When I wait for the email server to run
        When I choose Send/Receive from the File menu on main window 2

        When I choose Trello from the Apps menu on main window 2
        Then there is 1 trello board in main window 2 manage trello boards window and the trello board name is 'Trello1'
        Given I select trello board 1 in main window 2 manage trello boards window and press 'bnEditBoard'
        Then the main window 2 edit trello board window has the title 'Trello Board Trello1 mlockett2@historygraph.io'

        When I reset the email server dict

        Given the main window 2 trello board displayed matches
          | 0      | 1       |
          | List 1 | My List |
        
        Given the main window 1 trello board displayed matches
          | 0      | 1       |
          | List 1 | My List |

        Then I press the 'bnAddItem' button in main window 1 edit trello board window cell 0, 0        
        Given the main window 1 trello board displayed matches
          | 0      | 1       |
          | List 1 | My List |
          | Item 1 |         |

        Then edit in the main window 1 trello board 'teContent' in cell 1, 0 and change to 'User 1 Item 1'
        Then I press the 'bnSave' button in main window 1 edit trello board window cell 1, 0       

        Given the main window 1 trello board displayed matches
          | 0             | 1       |
          | List 1        | My List |
          | User 1 Item 1 |         |

        Then I press the 'bnAddItem' button in main window 2 edit trello board window cell 0, 0        
        Given the main window 2 trello board displayed matches
          | 0      | 1       |
          | List 1 | My List |
          | Item 1 |         |

        Then edit in the main window 2 trello board 'teContent' in cell 1, 0 and change to 'User 2 Item 1'
        Then I press the 'bnSave' button in main window 2 edit trello board window cell 1, 0       

        Given the main window 2 trello board displayed matches
          | 0             | 1       |
          | List 1        | My List |
          | User 2 Item 1 |         |

        When I wait for the email server to run
        When I choose Send/Receive from the File menu on edit trello board window belonging to main window 1
        #When I choose Send/Receive from the File menu on main window 1

        #When I choose Trello from the Apps menu on main window 1
        #Then there is 1 trello board in main window 1 manage trello boards window and the trello board name is 'Trello1'
        #Given I select trello board 1 in main window 1 manage trello boards window and press 'bnEditBoard'
        Then the main window 1 edit trello board window has the title 'Trello Board Trello1 mlockett1@historygraph.io'

        Given the main window 1 trello board double option displayed match
          | 0             | 1       |
          | List 1        | My List |
          | User 2 Item 1 |         |
          | User 1 Item 1 |         |
          | or            | or      |
          | List 1        | My List |
          | User 1 Item 1 |         |
          | User 2 Item 1 |         |
        
        When I wait for the email server to run
        When I choose Send/Receive from the File menu on edit trello board window belonging to main window 2
        #When I choose Send/Receive from the File menu on main window 2

        #When I choose Trello from the Apps menu on main window 2
        #Then there is 1 trello board in main window 2 manage trello boards window and the trello board name is 'Trello1'
        #Given I select trello board 1 in main window 2 manage trello boards window and press 'bnEditBoard'
        Then the main window 2 edit trello board window has the title 'Trello Board Trello1 mlockett2@historygraph.io'

        Given the main window 1 trello board double option displayed match
          | 0             | 1       |
          | List 1        | My List |
          | User 2 Item 1 |         |
          | User 1 Item 1 |         |
          | or            | or      |
          | List 1        | My List |
          | User 1 Item 1 |         |
          | User 2 Item 1 |         |

        Given the main window 1 and main window 2 trello boards match


