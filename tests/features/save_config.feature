Feature: Setup config
    In order to config the communicator
    We shall enter our settings
    and verify they save

    Scenario: Enter settings in the dialog save them in the database
        When I create a new demux
        When I open the settings page
        Given I enter the following values
          | teEmailAddress       | tePOPServerName | tePOPServerPort | tePOPUserName | tePOPPassword | teSMTPServerName | teSMTPServerPort | teSMTPUserName | teSMTPPassword |
          | mlockett1@timeca.io  | localhost1      | 10025           | mlockett1     | password1     | localhost2       | 10026            | mlockett1      | password2      |
        Given I press the OK button
        When I create a new demux
        When I open the settings page
        Then I see following values
          | teEmailAddress       | tePOPServerName | tePOPServerPort | tePOPUserName | tePOPPassword | teSMTPServerName | teSMTPServerPort | teSMTPUserName | teSMTPPassword |
          | mlockett1@timeca.io  | localhost1      | 10025           | mlockett1     | password1     | localhost2       | 10026            | mlockett1      | password2      |
        


