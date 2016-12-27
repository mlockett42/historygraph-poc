Feature: Setup config
    In order to config the communicator
    We shall enter our settings
    and verify they save

    Scenario: Enter settings in the dialog save them in the database
        When I clear the demux databases
        When I create a new demux 1
        When I open the settings page
        Given I enter the following values into the settings page
          | teEmailAddress             | tePOPServerName | tePOPServerPort | tePOPUserName | tePOPPassword | teSMTPServerName | teSMTPServerPort | teSMTPUserName | teSMTPPassword |
          | mlockett1@historygraph.io  | localhost1      | 10025           | mlockett1     | password1     | localhost2       | 10026            | mlockett1      | password2      |
        Given I press the OK button on the settings windows
        Then demux 1 has the following values
          | myemail                    | popserver  | popport | popuser   | poppass   | smtpserver | smtpport | smtpuser  | smtppass  |
          | mlockett1@historygraph.io  | localhost1 | 10025   | mlockett1 | password1 | localhost2 | 10026    | mlockett1 | password2 |
        Then demux 1 has the following types
          | myemail | popserver | popport | popuser | poppass | smtpserver | smtpport | smtpuser | smtppass |
          | string  | string    | integer | string  | string  | string     | integer  | string   | string   |
        When I create a new demux 1
        When I open the settings page
        Then I see following values
          | teEmailAddress             | tePOPServerName | tePOPServerPort | tePOPUserName | tePOPPassword | teSMTPServerName | teSMTPServerPort | teSMTPUserName | teSMTPPassword |
          | mlockett1@historygraph.io  | localhost1      | 10025           | mlockett1     | password1     | localhost2       | 10026            | mlockett1      | password2      |
        


