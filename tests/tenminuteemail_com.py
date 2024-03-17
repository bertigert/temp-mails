from temp_mails import Tenminuteemail_com as Mail

mail = Mail()
assert mail.email != "", "Mail name empty"
assert mail.get_inbox() == [], "Inbox not empty"
print(mail.email)

d1 = mail.wait_for_new_email()
print(d1)
d2 = mail.wait_for_new_email()
print(d2)

assert d1["id"] != d2["id"], "Email IDs are the same"

assert len(mail.get_inbox()) == 2, "Inbox length wrong"