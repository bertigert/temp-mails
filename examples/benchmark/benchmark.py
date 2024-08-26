from datetime import datetime
import json
from time import time, sleep
from threading import Thread

import temp_mails
from send_email import send_email_sync


def tprint(*args):
    """tprint anything with a timestamp"""
    print(f"[{datetime.now():%H:%M:%S}]", *args)

mail_classes = []
for mail_class in temp_mails.__all_providers__:    
    exec(f"mail_classes.append(temp_mails.{mail_class})")


def benchmark(t, mail_class, debug=False):
    try:
        tprint(f"Benchmarking {mail_class.__name__}")
        mail = mail_class()
        t.domain = mail.domain

        start = time()
        if debug: tprint(f"Email: {mail.email}, requesting email")
        
        r = send_email_sync(mail.email) # you need your own function which returns an object with "ok" as a boolean attribute

        if not r.ok:
            tprint("[ERROR] Failed to send verification email, trying again")
            sleep(2)
            benchmark(mail_class)
            return

        if debug: tprint(f"Requested verification email for {mail_class.__name__}, waiting for email")

        email = mail.wait_for_new_email()

        end = time()-start if email else 999
        times[mail_class.__name__] = (end, mail.domain)
        tprint(f"{mail_class.__name__} received email in {end:.2f} seconds ({len(times)}/{len(mail_classes)})")
    
    except Exception as e:
        tprint(f"{mail_class.__name__} encountered an error, please debug", e)
        try:
            times[mail_class.__name__] = (999999, mail.domain) # error is worse than timeout thus its further down
        except: # if no mail
            times[mail_class.__name__] = (999999, "None")
        return

times = {}
threads = []

for mail_class in mail_classes:
    
    # blacklist
    black_list = {
        "Internxt_com": "Hard Ratelimit",
        "Minutemailbox_com": "Server broken",
        "Temils_com": "Offline",
        "Tempmail_gg": "Offline",
        "Yopmail_com": "Captcha",
        "Fakermail_com": "Offline",
        "Mailcatch_com": "Offline",
        "Rainmail_xyz": "Offline",
        "Crazymailing_com": "Offline",
        "Adguard_com": "Captcha",
        "Tempmailbeast_com": "No service anymore",
        "Tempmailers_com": "Offline",
        "Schutzmail_de": "Offline",
        "Maildax_com": "Captcha",
        "Getnada_cc": "Broken",
        "Wptempmail_com": "Offline"
    }
    if mail_class.__name__ in black_list:
        tprint(f"Not testing {mail_class.__name__} because: {black_list[mail_class.__name__]}")
        continue

    #whitelist
    # if mail_class.__name__ not in ["Zemail_me"]:
    #     continue

    t = Thread(target=benchmark)#, args=[t, mail_class])
    t.__setattr__("_args", [t, mail_class])
    t.name = mail_class.__name__
    t.domain = None
    t.start_time = time()
    t.daemon = True
    t.start()
    threads.append(t)
    sleep(1)

# to debug if something is stuck
force_stop_time = 70
all_dead = False
while not all_dead:
    t: Thread
    all_dead = True
    for t in threads:
        t.join(1)
        if t.is_alive():
            time_alive = time()-t.start_time 
            
            if time_alive > force_stop_time: # hard n second limit for each tempmail, if the time is bigger than that, the thread gets skipped
                if not t.name in times: 
                    tprint("Force stopped", t.name) # force stopping doesnt actually kill the thread, it just removes it from this alive check, errors can still happen in the thread
                    try:
                        times[t.name] = (9999999, str(t.domain))
                    except:
                        times[t.name] = (9999999, "None")
                        # tprint("ERROR HERE", t.name)
            else:
                tprint(f"{t.name} still alive ({time_alive:.0f}/{force_stop_time} seconds)")
                all_dead = False

sorted_times = {k: v for k, v in sorted(times.items(), key=lambda item: item[1][0])}

max_name_length = max([len(name) for name in sorted_times.keys()])
max_domain_length = max([len(domain) for _, domain in sorted_times.values()])
max_num_length = len(str(len(sorted_times)))+2 # + []

print("\nResults\n-------\n")
with open("benchmark_results.json", "r") as f:
    data = json.loads(f.read())
for (name, (t, domain)), i in zip(sorted_times.items(), range(1, len(sorted_times)+1)):
    
    
    if t != 999999: # ignore errors
        weighted_t = force_stop_time if t > force_stop_time else t
        if not name in data:
            data[name] = {domain: weighted_t}
        else:
            if domain in data[name]:
                data[name][domain] = (data[name][domain]+weighted_t)/2
            else:
                data[name][domain] = weighted_t

    if t == 999:
        print(f"{f"[{i}]":<{max_num_length}} {f"{name} ({domain})":<{max_name_length+max_domain_length}} -> Timeout, check if host is online")
    elif t == 999999:
        print(f"{f"[{i}]":<{max_num_length}} {f"{name} ({domain})":<{max_name_length+max_domain_length}} -> Error, please debug")
    elif t == 9999999:
        print(f"{f"[{i}]":<{max_num_length}} {f"{name} ({domain})":<{max_name_length+max_domain_length}} -> Force Stop, check if host is online")
    else:
        print(f"{f"[{i}]":<{max_num_length}} {f"{name} ({domain})":<{max_name_length+max_domain_length}} -> {t:.2f} seconds")

with open("benchmark_results.json", "w") as f:
    f.write(json.dumps(data, indent=4))

print("\nNOTE: This benchmark is a very generic benchmark. Some tempmails have different domains which can be very different in speed. Some tempmails take longer than others to create an email, this is not taken into account. Some tempmails are too responsive and need specific usage of the wait_for_new_email function, see https://github.com/bertigert/temp-mails#some-additional-information")
