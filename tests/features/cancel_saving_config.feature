Feature: Cancel config setup
    Pressing cancel on the config setup should do nothing

    Scenario: Enter settings in the dialog cancel and verify that nothing is saved 
        When I clear the demux databases
        When I create a new demux 1
        When I open the settings page
        Given I enter the following values into the settings page
          | teEmailAddress       | tePOPServerName | tePOPServerPort | tePOPUserName | tePOPPassword | teSMTPServerName | teSMTPServerPort | teSMTPUserName | teSMTPPassword |
          | mlockett1@timeca.io  | localhost1      | 10025           | mlockett1     | password1     | localhost2       | 10026            | mlockett1      | password2      |
        Given I press the Cancel button on the settings windows
        When I create a new demux 1
        When I open the settings page
        Then I see following values
          | teEmailAddress       | tePOPServerName | tePOPServerPort | tePOPUserName | tePOPPassword | teSMTPServerName | teSMTPServerPort | teSMTPUserName | teSMTPPassword |
          |                      |                 |                 |               |               |                  |                  |                |                |
        

