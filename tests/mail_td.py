from random import choices, choice
from string import ascii_lowercase

from temp_mails import Mail_td as Mail
from send_email import send_email_sync

valid_domains = Mail.get_valid_domains(dynamic_recovery=True)
new_url = None
if len(valid_domains) == 2 and type(valid_domains[1] == list):
    new_url = valid_domains[0]
    print("Script url was outdated, updated it manually: New url:", new_url)
    valid_domains = valid_domains[1]
    

name, domain = "".join(choices(ascii_lowercase, k=6)), choice(valid_domains)

if new_url:
    mail = Mail(name=name, domain=domain, url=new_url)
else:
    mail = Mail(name=name, domain=domain)

print(mail.email)
assert mail.email != "", "Mail name empty"
assert mail.email == f"{name}@{domain}", "Mail does not match the used mail"


d0 = mail.get_inbox()
print(d0)
assert len(d0) == 0, "Inbox not empty"

r = send_email_sync(mail.email)
assert r.ok, "Failed to send email"
d1 = mail.wait_for_new_email()
print(d1)

r = send_email_sync(mail.email)
assert r.ok, "Failed to send email"
d2 = mail.wait_for_new_email()
print(d2)

assert d1["id"] != d2["id"], "Email IDs are the same"

assert len(mail.get_inbox()) == 2, "Inbox length wrong"

d3 = mail.get_mail_content(mail_id=d1["id"])
print(d3)
assert d3 != None, "Failed to get email content"