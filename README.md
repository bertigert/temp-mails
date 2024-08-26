# temp-mails

#### A basic wrapper around almost all temp mail sites on google, aiming to provide an almost identical api for every site.

The main purpose of this is to provide an easy way to use different temp mail services with almost the same python api, meaning little refactoring is needed.\
If there are any issues, please send me an email (bertigert@riseup.net) or create an issue, i cant test every email for every change I or the host makes since this library supports all temp mail providers which I could find on google (see below) which work and are not captcha protected.
## Installation
While every python3 version _should_ hypothetically work, python 3.12 is best
```
pip install temp-mails
```
### Requirements
```
pip install requests beautifulsoup4 lxml websocket-client==1.7.0
```
Note that you may need to uninstall all websocket packages in order for websocket-client to function properly

## Usage

Create an email on the site https://10minemail.com/
```python
from temp_mails import Tenminemail_com
from send_email import send_email_sync

# Generate a random email address
mail = Tenminemail_com()
# Get the email (e.g. example, examplehost, example@examplehost.com)
print(mail.name, mail.domain, mail.email)

# Get all emails in the inbox
print(mail.get_inbox())

# Send the email (by signing up or similar)
send_email_sync(mail.email)

# Wait for a new email for 120 seconds and get the email data.
data = mail.wait_for_new_email(delay=1.0, timeout=120) 
print(data)

# Get the content of the email, some tempmail services don't need this step
if data: # It returns None if something unexpected happens
    print(mail.get_mail_content(message_id=data["id"]))
```

The wrapper api for each email host is very similar, so little refactoring is needed in order to change the email host. However, the email data may change in format or similar. One email host could just return a string with the html content of the email, another one could return a dict with subject, content etc, I will probably add better support for that at some point.\
Also note that only some hosts support user defined names/domains.\
Also note that the built in wait_for_mail can break if there are too many emails or too many emails at once. You can implement you own custom function for that case. It works for all my use cases though (verifications etc). Many built in wait_for_new_email functions have optimizations in them, so you should use them unless absolutely necessary.\
This libray is designed with minimal error handling built in. This is because if an error occurs in the library, something broke and it wouldn't work anyways, there is no way for automatic recovery since it is all based on 3rd party sites.

### Some additional information  
Some temp mails are really responsive, thus using wait_for_new_email in a sync program may be too slow. Because of this, for some tempmails there is a way to use threads (+3 loc):
```python
from time import sleep
from threading import Event
from concurrent.futures import ThreadPoolExecutor

from temp_mails import Byom_de
from send_email import send_email_sync

mail = Byom_de()
print(mail.email)
  
# Set up the event which can be used by the wait_for_new_email function to signal that it's ready
is_ready_event = Event()
# Start the wait function inside of a thread
t = ThreadPoolExecutor().submit(mail.wait_for_new_email, is_ready_event=is_ready_event)

# Wait for the wait function to be ready
is_ready_event.wait()

# Send the email (by signing up or similar)
send_email_sync(mail.email)

# Get the result from the wait function
result = t.result()

print(result)
```
You can check if a tempmail provides this feature by checking if the wait_for_new_email function has is_ready_event as an argument. I will add this to more functions on demand.

Another way to avoid being too slow is the start_length argument in some wait_for_new_email function. Some tempmails check for a new mail by checking if the inbox changed. In order to get the start_length, the inbox is checked once. If the email is received before this call is made, the email cannot be awaited. By using start_length as an argument, you can specify the start_length of the inbox:
```python
from temp_mails import Tempmail_id
from send_email import send_email_sync

mail = Tempmail_id()

# Get the old length of the inbox. If you are certain that this email is new, you can assume it's 0 and skip this step.
old_length = len(mail.get_inbox())

# Send the email
r = send_email_sync(mail.email)

# Wait for the mail using the old_length. Normally the old_length would be defined in this function call, after the email has been sent.
data = mail.wait_for_new_email(start_length=old_length)

print(data)
```

## Supported Unique Sites (119) (~107 working as of 23.08.2024)
- https://10minemail.com/ - semi-official
- https://10minutemail.com/ - unofficial
- https://internxt.com/temporary-email - unofficial, weird ratelimit
- https://www.minuteinbox.com/ - unofficial
- https://temp-mail.io/ - unofficial
- https://temp-mail.org/ - semi-official
- https://temp-mailbox.com/, https://dismailbox.com/ - unofficial
- https://10minutesemail.net/ - unofficial
- https://etempmail.net/ - unofficial
- https://www.disposablemail.com/ - unofficial
- https://www.emailondeck.com/ - unofficial
- https://1secmail.com/, https://www.tempemailpro.com/ (uses 1secmail) - official
- https://www.mohmal.com/en/inbox - unofficial
- https://www.fakemail.net/ - unofficial
- https://tempmail.email/ - unofficial
- https://tempmail.plus/ - unofficial
- https://generator.email/ - unofficial
- https://cryptogmail.com/ - unofficial
- https://mail.tm/ - official/semi-official
- https://temp-inbox.com/ - unofficial
- https://mailhole.de/ - unofficial
- https://tmailor.com/ - unofficial, ~5 emails/IP
- https://tmail.ai/ - unofficial
- https://cloudtempmail.com/ - unofficial
- https://luxusmail.org/ - unofficial
- https://muellmail.com/ - unofficial
- https://www.eztempmail.com/ - unofficial
- https://tempail.com/ - unofficial
- https://tempmail.ninja/ - unofficial
- https://upxmail.com/ - unofficial
- https://www.trash-mail.com/ - unofficial
- https://tempemailfree.com/ - unofficial
- https://tempr.email/ - unofficial
- https://tempmail.net/ - unofficial
- https://www.guerrillamail.com/ - semi-official
- https://tm-mail.com/ - unofficial
- https://tempmail.lol/ - official
- https://yopmail.com/ - unofficial, you need to do manual captcha once
- https://etempmail.com/ - unofficial
- https://tmail.gg/ - unofficial
- https://mailtemp.uk/ - unofficial
- https://mostakbile.com/ - unofficial
- https://tempmails.net/ - unofficial
- https://temp-mail.gg/ - unofficial
- https://maillog.org/ - unofficial
- https://temp-mail.id/ - unofficial
- https://zemail.me/ - unofficial
- https://tempmailso.com/ - unofficial
- https://mail-temp.com/ - unofficial
- https://www.fakemailgenerator.com/ - unofficial
- https://correotemporal.org/ - unofficial
- https://www.byom.de/ - unofficial
- https://moakt.com/ - unofficial
- https://inboxes.com/ - semi-official
- https://dropmail.me/ - semi-official
- https://gmailcity.com/ - unofficial
- https://mailgolem.com/ - unofficial
- https://anonymmail.net/ - unofficial
- https://emailfake.com/ - unofficial
- https://disposableemail.co/ - unofficial
- https://temp-inbox.me/ - unofficial
- https://www.tempo-mail.com/ - unofficial
- https://www.txen.de/ - unofficial
- https://tempm.com/ - unofficial
- https://www.trashmail.de/ - semi-official
- https://incognitomail.co/ - unofficial
- https://10minutemail.one/ - unofficial
- https://mail.gw/ - official/semi-official
- https://email10min.com/ - unofficial
- https://10-minutemail.net - unofficial
- https://lroid.com/ - unofficial, same domain as haribu.net
- https://www.10minuteemails.com/ - unofficial
- https://tmpmail.co/ - unofficial
- https://mailsac.com/ - unofficial
- https://www.fumail.co/ - unofficial
- https://tempomail.top/ - unofficial
- https://mail.td/ - unofficial
- https://www.mintemail.com/ - unofficial
- https://tmail.io/, https://tmail.io/temporary-disposable-gmail - unofficial
- https://segamail.com/ - unofficial
- https://www.mail7.io/ - unofficial
- https://mail4qa.com/ - unofficial
- https://treemail.pro/ - unofficial
- https://inboxkitten.com/ - unofficial
- https://www.tempmailinbox.com/ - unofficial
- https://harakirimail.com/ - unofficial
- https://mailnesia.com/ - unofficial
- https://mailper.com/ - unofficial
- https://www.mailforspam.com/ - unofficial
- https://tempemail.co/ - unofficial
- https://www.tempinbox.xyz/ - unofficial
- https://www.eyepaste.com/ - unofficial
- https://email-fake.com/ - unofficial
- https://www.mailinator.com/ - semi-official
- https://expressinboxhub.com/ - unofficial
- https://burnermailbox.com/ - unofficial
- https://tempemailgen.com/ - unofficial
- https://priyo.email/ - unofficial
- https://tempp-mails.com/ - unofficial
- https://fmail.sbs/ - unofficial
- https://trashmail.ws/ - unofficial
- https://temp-email.info/ - unofficial
- https://www.mailtemp.net/ - unofficial
- https://haribu.net/ - unofficial, same domain as lroid.com
- https://tempmailbox.net - unofficial
- https://tempmailer.net/ - unofficial
- https://tempmail.cc/ - unofficial

> unofficial = we use no official API, because the website does not offer one (at least for free)\
> semi-official = website hat an official API, but we don't use it, often because it is using RapidAPI, broken or requires an API key\
> official = we use the websites official API (RapidAPI or not)\
> captcha = requires you to go onto the website and solve a captcha/verify your browser on the same IP. After that it should work for some requests/minutes. You may need to manually add a captcha response. In some cases, it just does not work anymore, I won't remove the script though as the "knowledge" could still be interesting.


### In Progress
- None


### Sites which worked at some point
- https://tempmail.adguard.com/ - unofficial, captcha
- https://tempmailbeast.com/ - unofficial, doesn't provide service anymore?
- https://tempmail.gg/ - unofficial, offline
- https://tempmailers.com/ - unofficial, offline/suspended
- https://schutz-mail.de/ - unofficial, offline
- https://maildax.com/ - unofficial, captcha
- https://www.temils.com/ - unofficial, offline
- https://www.minutemailbox.com/ - unofficial, broken
- https://fakermail.com/ - unofficial, offline
- http://mailcatch.com/ - unofficial, offline
- https://rainmail.xyz/ - unofficial, offline
- https://www.crazymailing.com/ - unofficial, offline
- https://getnada.cc/ - official, broken
- https://wp-temp-mail.com/ - unofficial, offline
- https://temp-mailbox.net/ - unofficial, offline


### Websites I won't add
- Every website which requires an account/api key in order to use it
- Every website which only forwards emails to a real email
- https://sandvpn.com/ - website is obfuscated like shit - maybe
- https://www.tempmail.us.com/ - 1 email/IP, uses cpanel
- https://www.linshi-email.com/ - chinese, weird ratelimit - maybe
- https://itselftools.com/tempmail - uses firebase/firestore, which i do not know anything about nor how to work with. - maybe
- https://www.throwawaymail.com/en - down
- https://maildrop.cc/ - cf
- https://gettempmail.com/ - captcha/cf
- https://temp-mail.us/en/ - down
- https://10minute-mail.org/ - captcha/cf
- https://tempumail.com/mailbox - captcha
- https://tempmailo.com/ - captcha/cf
- https://one-off.email/ - broken
- https://www.autolikerlive.com/temp-mail - down
- https://tempmail.altmails.com/ - down
- https://www.another-temp-mail.com/ - broken
- https://maildim.com/ - down
- https://tempmaily.com/ - broken
- https://tempmail.quest/ - captcha/cf
- https://emailsilo.net/ - captcha
- https://tempmail.altmails.com/ - down
- https://inboxesapp.com/ - acc/token based, not possible to design user friendly
- https://www.dispostable.com/ - captcha
- https://www.emailnator.com/ - captcha/cf, rapid api
- https://smailpro.com/ - captcha, rapid api
- https://mytemp-mail.com/ - captcha
- https://www.mailmenot.io/ - down
- https://temprmail.com/ - broken
- https://www.no-spammers.com/ - captcha (easy tho)
