from temp_mails import Segamail_com as Mail
from send_email import send_email_sync

mail = Mail()
print(mail.email)

d0 = mail.get_inbox()
assert len(d0) == 0, "Inbox not empty"
print(d0)

r = send_email_sync(mail.email)
assert r.ok, "Failed to send email"
d1 = mail.wait_for_new_email(start_length=0)
print(d1)

r = send_email_sync(mail.email)
assert r.ok, "Failed to send email"
d2 = mail.wait_for_new_email(start_length=1)
print(d2)

assert d1["id"] != d2["id"], "Email IDs are the same"

assert len(mail.get_inbox()) == 2, "Inbox length wrong"