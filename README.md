# temp-mails

#### A basic wrapper around various temp mail sites, aiming to provide an almost identical api for every site.

The main purpose of this is to provide an easy way to quickly register an account on various sites and then discard the email.

## Installation
While every python3 version _should_ hypothetically work, python 3.12 is best
```
pip install temp-mails
```
### Requirements
```
pip install requests beautifulsoup4 lxml
```

## Supported Sites
- https://10minemail.com/
- https://10minutemail.com/
- https://internxt.com/temporary-email
- https://10minutemail.com/
- https://temp-mail.io/
- https://temp-mail.org/
- https://temp-mailbox.com/
- https://etempmail.net/10minutemail
- https://10minutesemail.net/

## Usage

Create an email on the site https://10minemail.com/
```python
from temp_mails import tenminemail_com

mail = tenminemail_com() # Generate a random email address
print(mail.email) # get the name of the email (e.g. example@examplehost.com)

print(mail.get_inbox()) # get all emails in the inbox

print(mail.wait_for_new_email(delay=1.0, timeout=120)) # wait for a new email for 120 seconds and get the email data
```

The wrapper api for each email host is very similar, so little refactoring is needed in order to change the email host. However, the email data may change in format or similar. One email host could just return a string with the html content of the email, another one could return a dict with subject, content etc.