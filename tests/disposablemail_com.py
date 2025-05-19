from temp_mails import Disposablemail_com as Mail
from send_email import send_email_sync

mail = Mail()
assert mail.email != "", "Mail name empty"
print(mail.email)
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