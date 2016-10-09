Feature: Open up 2 main windows and play a shared checkers games
    Window 1 opens the checkers windows chooses new game, shares with window 2, both windows make moves make sure they both have the same board layout 

    Scenario: Open checkers game and make some moves
        #Copied from send messages and establish encrypted link
        When I reset the email server dict
        When I clear the demux databases
        When I create a new demux 1
        When I create a new demux 2
        Given I set up demux 1 with the following values
          | myemail                | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  |
          | mlockett1@livewire.io  | localhost  | 10026   | mlockett1 |           | localhost  | 10025    | mlockett1 |           |
        Given I set up demux 2 with the following values
          | myemail                | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  |
          | mlockett2@livewire.io  | localhost  | 10026   | mlockett2 |           | localhost  | 10025    | mlockett2 |           |
        When I open main window 1
        When I open main window 2
        When I choose New Message from the File menu on main window 1
        Given I enter the following values into main window 1 new message window
          |  tesubject  |  teBody    | tetoaddress
          | Hello world | Frist post | mlockett2@livewire.io
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
        Then there is 1 contact in main window 2 contact window and the contacts name is 'mlockett1@livewire.io'
        
        When I wait for the email server to run
        When I choose Send/Receive from the File menu on main window 1
        When I choose Contacts from the File menu on main window 1
        Then there is 1 contact in main window 1 contact window and the contacts name is 'mlockett2@livewire.io'
        The contact 'mlockett2@livewire.io' in main window 1 has the same public key as main window 2 private key
        When I choose Send/Receive from the File menu on main window 2
        The contact 'mlockett1@livewire.io' in main window 2 has the same public key as main window 1 private key
        
        When I choose Checkers from the Apps menu on main window 1
        When I press the bnNewGame button on main window 1 manage checkers games window
        Given I enter the following values into main window 1 new checkers game window
          | teEmailAddress       | teGameName |
          | mlockett2@timeca.io  | Checkers1  |
        When I press the bnOK button on main window 1 new checkers game window
        Then there is 1 checkers game in main window 1 manage checkers games window and the checkers game name is 'Checkers1'
        Given I select checkers game 1 in main window 1 manage checkers games window and press 'bnPlayGame'
        Then the main window 1 play checkers window has the title 'Play Checkers: Checkers1'

        Given the main window 1 play checkers window board displayed matches
          | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  |
          |    | W  |    | W  |    | W  |    | W  |
          | W  |    | W  |    | W  |    | W  |    |
          |    | W  |    | W  |    | W  |    | W  |
          |    |    |    |    |    |    |    |    |
          |    |    |    |    |    |    |    |    |
          | B  |    | B  |    | B  |    | B  |    |
          |    | B  |    | B  |    | B  |    | B  |
          | B  |    | B  |    | B  |    | B  |    |
        Given the main window 1 play checkers window current player is 'White'

        Then click on square 0 0
        Given the main window 1 play checkers window status does not start with 'Selected piece at '
        Then click on square 0 5
        Given the main window 1 play checkers window status does not start with 'Selected piece at '
          
        Then click on square 1 2
        Given the main window 1 play checkers window equals 'Selected piece at (1, 2)'
        Then click on square 7 7
        Given the main window 1 play checkers window equals 'Invalid move.'

        Then click on square 1 2
        Given the main window 1 play checkers window equals 'Selected piece at (1, 2)'
        Then click on square 2 3
        Given the main window 1 play checkers window equals 'Piece moved from (1, 2) to (2, 3)'
        Given the main window 1 play checkers window board displayed matches
          | 0  | 1  | 2  | 3  | 4  | 5  | 6  | 7  |
          |    | W  |    | W  |    | W  |    | W  |
          | W  |    | W  |    | W  |    | W  |    |
          |    |    |    | W  |    | W  |    | W  |
          |    |    | W  |    |    |    |    |    |
          |    |    |    |    |    |    |    |    |
          | B  |    | B  |    | B  |    | B  |    |
          |    | B  |    | B  |    | B  |    | B  |
          | B  |    | B  |    | B  |    | B  |    |
        Given the main window 1 play checkers window current player is 'Black'




