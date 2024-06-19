from temp_mails import Dropmail_me as Mail
from send_email import send_email_sync

mail = Mail()
print(mail.email)
assert mail.email != "", "Mail name empty"

r = send_email_sync(mail.email)
assert r.ok, "Failed to send email"
d1 = mail.wait_for_new_email()
print(d1)

r = send_email_sync(mail.email)
assert r.ok, "Failed to send email"
d2 = mail.wait_for_new_email()
print(d2)

assert d1["id"] != d2["id"], "Email IDs are the same"

d3 = mail.get_mail_content(mail_id=d1["id"])
print(d3)
assert d3 != None, "Failed to get email content"