import json

with open("benchmark_results.json", "r") as f:
    data = json.loads(f.read())

#sort by website
websites = {}
for website in data:
    avg = 0
    for domain in data[website]:
        avg+=data[website][domain]
    if avg > 0:
        avg = avg/len(data[website].keys())
        websites[website] = avg

sorted_times = {k: v for k, v in sorted(websites.items(), key=lambda item: item[1])}
print(json.dumps(sorted_times, indent=4))

# sort by domain
domains = {}    
for website in data:
    avg = 0
    for domain in data[website]:
        domains[domain] = data[website][domain]

sorted_times = {k: v for k, v in sorted(domains.items(), key=lambda item: item[1])} 
print(json.dumps(sorted_times, indent=4))