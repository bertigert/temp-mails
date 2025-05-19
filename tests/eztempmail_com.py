from string import ascii_lowercase
from random import choices, choice

from temp_mails import Eztempmail_com as Mail
from send_email import send_email_sync

name, domain = "".join(choices(ascii_lowercase, k=6)), choice(Mail.get_valid_domains())

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