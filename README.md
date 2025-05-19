# temp-mails

#### A basic wrapper around almost all temp mail sites on google, aiming to provide an almost identical api for every site.

The main purpose of this is to provide an easy way to use different temp mail services with almost the same python api, meaning little refactoring is needed.\
If there are any issues, create an issue, i cant test every email for every change I or the host makes since this library supports all temp mail providers which I could find on google (see below) which work and are not captcha protected.
## Installation
While every python3 version _should_ hypothetically work, python 3.12 is best
```bash
pip install temp-mails
```
### Requirements
```bash
pip install requests beautifulsoup4 lxml websocket-client==1.7.0
```
Note that you may need to uninstall all websocket packages in order for websocket-client to function properly

## Usage

Create an email on the site https://10minemail.com/
```python
from temp_mails import Tenminemail_com
from send_email import send_email_sync

# Generate a random email address
# It is generally recommended to let the site determine a random email address, as custom ones often require additional requests.
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

The wrapper api for each email host is very similar, so little refactoring is needed in order to change the email host. However, the email data may change in format or similar. One email host could just return a string with the html content of the email, another one could return a dict with subject, content etc.\
Also note that only some hosts support user defined names/domains. It is generally recommended to let the site determine a random email address, as custom ones often require additional requests.\
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

## Supported Working Unique Sites
State as of 19.05.2025 (~76 sites)

- https://10minemail.com/ - semi-official
- https://10minutemail.com/ - unofficial
- https://10minutemail.one/ - unofficial
- https://10minutesemail.net/ - unofficial
- https://anonymmail.net/ - unofficial
- https://burnermailbox.com/ - unofficial
- https://byom.de/ - unofficial
- https://correotemporal.org/ - unofficial
- https://cryptogmail.com/ - unofficial
- https://disposablemail.com/ - unofficial
- https://dropmail.me/ - semi-official
- https://email-fake.com/ - unofficial
- https://emailfake.com/ - unofficial
- https://emailondeck.com/ - unofficial
- https://etempmail.com/ - unofficial
- https://eyepaste.com/ - unofficial
- https://eztempmail.com/ - unofficial
- https://fakemail.net/ - unofficial
- https://fakemailgenerator.com/ - unofficial
- https://fumail.co/ - unofficial
- https://generator.email/ - unofficial
- https://guerrillamail.com/ - semi-official
- https://harakirimail.com/ - unofficial
- https://inboxes.com/ - semi-official
- https://incognitomail.co/ - unofficial
- https://internxt.com/temporary-email - unofficial (= mail.tm)
- https://mail-temp.com/ - unofficial
- https://mail.gw/ - official/semi-official
- https://mail.td/ - unofficial
- https://mail.tm/ - official/semi-official
- https://maildax.com/ - unofficial
- https://mailforspam.com/ - unofficial
- https://mailhole.de/ - unofficial
- https://mailinator.com/ - semi-official
- https://mailnesia.com/ - unofficial
- https://mailper.com/ - unofficial
- https://mailsac.com/ - unofficial
- https://mailtemp.uk/ - unofficial
- https://mintemail.com/ - unofficial
- https://minuteinbox.com/ - unofficial
- https://moakt.com/ - unofficial
- https://mohmal.com/ - unofficial
- https://mostakbile.com/ - unofficial
- https://muellmail.com/ - unofficial
- https://noopmail.org/ - unofficial
- https://priyo.email/ - unofficial
- https://rainmail.xyz/ - unofficial
- https://temp-inbox.com/ - unofficial
- https://temp-mail.gg/ - unofficial
- https://temp-mail.id/ - unofficial
- https://temp-mail.io/ - unofficial
- https://temp-mail.org/ - semi-official
- https://tempail.com/ - unofficial
- https://tempemail.co/ - unofficial
- https://tempemailfree.com/ - unofficial
- https://tempinbox.xyz/ - unofficial
- https://tempm.com/ - unofficial
- https://tempmail.cc/ - unofficial
- https://tempmail.email/ - unofficial (= mail.tm)
- https://tempmail.lol/ - official
- https://tempmail.ninja/ - unofficial
- https://tempmail.plus/ - unofficial
- https://tempmailbox.net - unofficial
- https://tempomail.top/ - unofficial
- https://temporarymail.com/ - unofficial
- https://tempr.email/ - unofficial
- https://tm-mail.com/ - unofficial
- https://tmail.gg/ - unofficial
- https://tmail.io/, https://tmail.io/temporary-disposable-gmail - unofficial
- https://tmailor.com/ - unofficial, ~5 emails/IP
- https://tmpmail.co/ - unofficial
- https://trashmail.de/ - semi-official
- https://trashmail.ws/ - unofficial
- https://txen.de/ - unofficial
- https://yopmail.com/ - unofficial, you need to do manual captcha once
- https://zemail.me/ - unofficial

> unofficial = we use no official API, because the website does not offer one (at least for free)\
> semi-official = website hat an official API, but we don't use it, often because it is using RapidAPI, broken or requires an API key\
> official = we use the websites official API (RapidAPI or not)\
> captcha = requires you to go onto the website and solve a captcha/verify your browser on the same IP. After that it should work for some requests/minutes. You may need to manually add a captcha response. This is only supported for some sites, because it's too much effort.

### In Progress
- maybe some new sites


### Sites which worked at some point
State as of 19.05.2025 (~49 sites)

- https://1secmail.com/ - official - OFF
- https://10-minutemail.net - unofficial - CAP/CF
- https://10minuteemails.com/ - unofficial - BS
- https://cloudtempmail.com/ - unofficial, CAP/CF
- https://crazymailing.com/ - unofficial - CAP/CF
- https://email10min.com/ - unofficial - NE
- https://email-free.online/ - unofficial - OFF
- https://etempmail.net/ - unofficial - CAP/CF
- https://expressinboxhub.com/ - CAP
- https://fakermail.com/ - unofficial - NE
- https://fmail.sbs/ - unofficial - OFF
- https://getnada.cc - semi-official - NE/OFF (= email-free.online)
- https://gmailcity.com/ - unofficial - OFF
- https://haribu.net/ - unofficial - NE
- https://inboxkitten.com/ - unofficial - NE
- https://lroid.com/ - unofficial - NE (= haribu.net)
- https://luxusmail.org/ - unofficial - CAP/CF
- https://mail4qa.com/ - unofficial - NE
- https://mail7.io/ - unofficial - OFF
- http://mailcatch.com/ - unofficial - NE
- https://mailgolem.com/ - unofficial - NE
- https://maillog.org/ - unofficial - OFF
- https://mailtemp.net/ - unofficial - NE
- https://minutemailbox.com/ - unofficial - BS
- https://schutz-mail.de/ - unofficial - OFF
- https://segamail.com/ - unofficial - BS
- https://temils.com/ - unofficial - OFF
- https://temp-email.info/ - unofficial - CAP
- https://temp-inbox.me/ - unofficial - CAP/CF
- https://temp-mailbox.net/ - unofficial - NE
- https://tempemailgen.com/ - unofficial - CAP/CF
- https://tempmail.adguard.com/ - unofficial - CAP
- https://tempmail.gg/ - unofficial - NE
- https://tempmail.guru/ - unkown - OFF
- https://tempmail.net/ - unofficial - NE
- https://tempmailbeast.com/ - unofficial - OFF
- https://tempmailer.net/ - unofficial - OFF
- https://tempmailers.com/ - unofficial - OFF
- https://tempmailinbox.com/ - unofficial - OFF
- https://tempmails.net/ - unofficial - NE
- https://tempmailso.com/ - unofficial - OFF
- https://tempo-mail.com/ - unofficial - OFF
- https://tempp-mails.com/ - unofficial - CAP/CF
- https://temprmail.com/ - broken - OFF
- https://tmail.ai/ - unofficial - OFF
- https://trash-mail.com/ - unofficial - OFF
- https://treemail.pro/ - unofficial - OFF
- https://upxmail.com/ - unofficial - OFF
- https://wp-temp-mail.com/ - OFF

> NE = Is online, but receives no emails\
> BS = Site is broken\
> CAP/CF = Captcha in combination with cloudflare\
> CAP = Captcha\
> OFF = Complete site is down/does not provide temp mail service\

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
- https://www.no-spammers.com/ - captcha (easy tho)
- https://www.emailgenerator.org/ - captcha
