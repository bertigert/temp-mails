from random import choices, choice
from string import ascii_lowercase
from threading import Event
from concurrent.futures import ThreadPoolExecutor

from temp_mails import Fakemailgenerator_com as Mail
from send_email import send_email_sync

name, domain = "".join(choices(ascii_lowercase, k=6)), choice(Mail.get_valid_domains())
mail = Mail(name=name, domain=domain)
print(mail.email)
assert mail.email != "", "Mail name empty"
assert mail.email == f"{name}@{domain}", "Mail does not match the used mail"

d0 = mail.get_inbox()
print(d0)
assert len(d0) == 0, "Inbox not empty"

is_ready_event = Event()
t = ThreadPoolExecutor().submit(mail.wait_for_new_email, is_ready_event=is_ready_event)
is_ready_event.wait()
r = send_email_sync(mail.email)
assert r.ok, "Failed to send email"
d1 = t.result()
print(d1)


is_ready_event = Event()
t = ThreadPoolExecutor().submit(mail.wait_for_new_email, is_ready_event=is_ready_event)
is_ready_event.wait()
r = send_email_sync(mail.email)
assert r.ok, "Failed to send email"
d2 = t.result()
print(d2)

assert d1["id"] != d2["id"], "Email IDs are the same"
assert len(mail.get_inbox()) == 2, "Inbox length wrong"

d3 = mail.get_mail_content(mail_id=d1["id"])
print(d3)
assert d3 != None, "Failed to get email content"