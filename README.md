# temp-mails

#### A basic wrapper around various temp mail sites, aiming to provide an almost identical api for every site.

The main purpose of this is to provide an easy way to quickly register an account on various sites and then discard the email.\
If there are any issues, please send me an email (bertigert@riseup.net) or create an issue, i cant test every email for every change I or the host makes.
## Installation
While every python3 version _should_ hypothetically work, python 3.12 is best
```
pip install temp-mails
```
### Requirements
```
pip install requests beautifulsoup4 lxml websocket-client
```
Note that you may need to uninstall all websocket packages in order for websocket-client to function properly

## Supported Sites (17)
- https://10minemail.com/ - semi-official
- https://10minutemail.com/ - unofficial
- https://internxt.com/temporary-email - unofficial
- https://www.minuteinbox.com/ - unofficial
- https://temp-mail.io/ - unofficial
- https://temp-mail.org/ - semi-official
- https://temp-mailbox.com/ - unofficial
- https://10minutesemail.net/ - unofficial
- https://etempmail.net/ - unofficial
- https://www.disposablemail.com/ - unofficial
- https://www.emailondeck.com/ - unofficial
- https://1secmail.com/ - official
- https://www.mohmal.com/en/inbox - unofficial
- https://www.fakemail.net/ - unofficial
- https://tempmail.email/ - unofficial
- https://tempmail.plus/ - unofficial
- https://generator.email/ - unofficial

### In Progress
- https://cryptogmail.com/
- https://mail.tm/
- ...

> unofficial = we use no official API, because the website does not offer one (at least for free)\
> semi-official = website hat an official API, but we don't use it, often because it is using RapidAPI\
> official = we use the websites official API

## Usage

Create an email on the site https://10minemail.com/
```python
from temp_mails import Tenminemail_com

mail = Tenminemail_com() # Generate a random email address
print(mail.email) # get the name of the email (e.g. example@examplehost.com)

print(mail.get_inbox()) # get all emails in the inbox

data = mail.wait_for_new_email(delay=1.0, timeout=120) # wait for a new email for 120 seconds and get the email data
print(data)

print(mail.get_mail_content(message_id=data["_id"])) # get the content of the email
```

The wrapper api for each email host is very similar, so little refactoring is needed in order to change the email host. However, the email data may change in format or similar. One email host could just return a string with the html content of the email, another one could return a dict with subject, content etc.\
Also note that only some hosts support user defined names/domains.