Feature: Open up main window and view settings
    Opening up the main window should display correctly and then allow us to open the settings dialog which should contain the correct settings

    Scenario: Open main form then setting form and verify correct information is present
        When I clear the demux databases
        When I create a new demux 1
        Given I set up demux 1 with the following values
          | myemail              | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  |
          | mlockett1@timeca.io  | localhost1 | 10025   | mlockett1 | password1 | localhost2 | 10026    | mlockett1 | password2 |
        When I open main window 1
        When I choose Settings from the Options menu on main window 1
        Then I see following values on the settings page
          | teEmailAddress       | tePOPServerName | tePOPServerPort | tePOPUserName | tePOPPassword | teSMTPServerName | teSMTPServerPort | teSMTPUserName | teSMTPPassword |
          | mlockett1@timeca.io  | localhost1      | 10025           | mlockett1     | password1     | localhost2       | 10026            | mlockett1      | password2      |
        

