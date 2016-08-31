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
        
        #Fill in the field with the name "Email Address" with "mlockett1@timeca.io"
        #Fill in the field with the name "POP Server" with "localhost"
        #Fill in the field with the name "POP Server Port" with "10025"
        #Fill in the field with the name "POP User Name" with "mlockett1"
        #Fill in the field with the name "POP Password" with ""
        #Fill in the field with the name "SMTP Server" with "localhost"
        #Fill in the field with the name "SMTP Server Port" with "10026"
        #Fill in the field with the name "SMTP User Name" with "mlockett1"
        #Fill in the field with the name "SMTP Password" with ""
        #Then I see that the settings contain:
        #email_address       | pop_server | pop_port | pop_username | pop_password | smtp_server | smtp_port | smtp_username | smtp_password |
        #mlockett1@timeca.io | localhost  | 10025    | mlockett1    |              | localhost   | 10026     | mlockett1     |               |


