import random
import inspect
from threading import Event
from concurrent.futures import ThreadPoolExecutor

import temp_mails
from send_email import send_email_sync

"""
This script is for choosing a random email and implementing a universal wait_for_new_email function, usable for all sites.
"""


def choose_email():
    """Chooses a random email from all possible websites"""
    
    mail_class_str = random.choice(temp_mails._all_providers)
    
    print(f"Creating email on website {mail_class_str}")

    whitelisted_args = ("self", "name", "domain", "exclude", "password") # args which arent necessary, arguments like captcha are necessary
    mail_class = temp_mails.__getattribute__(mail_class_str)
    
    for arg in inspect.getfullargspec(mail_class).args:
        if not arg in whitelisted_args:
            return choose_email()
    
    return mail_class()

def wait_for_new_email(mail, send_email_func, return_content: bool=True, delay: int=2, timeout: int=60, start_length: int=0):
    """
    Waits for the mail\n
    Args\n
    mail - temp mail object
    send_email_func - the logic which sends the email, needs to have the full email string as an arg\n
    return_content - whether to return the content if it is not already in the basic data\n
    delay - delay between each check if its an arg\n
    timeout - timeout if its an arg\n
    start_length - optimization for some inboxes, see readme
    """
    
    possible_args = inspect.getfullargspec(mail.wait_for_new_email).args
    
    use_thread = False
    args = {}
    if "delay" in possible_args:
        args["delay"] = delay
    
    if "timeout" in possible_args:
        args["timeout"] = timeout

    if "start_length" in possible_args: 
        args["start_length"] = start_length

    # since this is often only an argument if it has some optimization to it we will leave it as default (which is True most of the time)
    # if "return_content" in possible_args: 
    #     args["return_content"] = return_content

    if "is_ready_event" in possible_args:
        use_thread = True
        is_ready_event = Event()
        args["is_ready_event"] = is_ready_event

        t = ThreadPoolExecutor().submit(mail.wait_for_new_email, **args)
    
    print("Final args:", args)

    if use_thread:        
        is_ready_event.wait()

    # logic for sending email here
    send_email_func(mail.email)

    if use_thread:
        data = t.result()
    else:
        data = mail.wait_for_new_email(**args)

    if not data or "content" in data or not return_content:
        return data
    
    print("Data before:", data)
    content = mail.get_mail_content(data["id"])    

    if type(content) == dict: # returns more than just the content, e.g. time
        return data | content
    else:
        data["content"] = content
        return data


for mail in temp_mails._all_providers:
    mail_class = temp_mails.__getattribute__(mail)
    if "get_valid_domains" in dir(mail_class):
        try:
            valid = mail_class.get_valid_domains()
            if len(valid) < 2:
                print("mail:", mail, valid)
        except:
            print(mail, "ERROR")
        
    else:
        print(mail, "has no get_valid_domains")
quit()

mail = choose_email()
print(mail.email)
email = wait_for_new_email(mail, send_email_sync)
print("Data after:", email)