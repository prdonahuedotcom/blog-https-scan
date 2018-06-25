#!/usr/bin/env python

import json

input = "all.json"
http_output = "http.csv"
error_output = "errors.csv"

HASHMARK=50

print("Reading {}..".format(input))
if HASHMARK>0:
    print("Each dot represents {} lines processed:".format(HASHMARK))

http = {}
https = []
hsts = []
errors = []

i = 0

with open(input, 'r') as f:
    for line in f:
        i += 1
        if i % HASHMARK == 0:
            print(".", end='', flush=True)
        j = json.loads(line)

        host = j['domain']
        ip = j['ip']

        if j.get('error'):
            errors.append(host)
            continue

        terminal_scheme = j['data']['http']['response']['request']['url']['scheme']

        if terminal_scheme == "https":
            https.append(host)
            # also check hsts
            headers = j['data']['http']['response'].get('headers')
            if headers and headers.get('strict_transport_security'):
                hsts.append(host)
        else:
            http[host] = ip
print("Done reading file.")

with open(http_output, 'w') as out:
    for h in http:
        out.write("{},{}\n".format(http[h], h))

total = len(https) + len(http)
print("Of the {} total hosts we could connect to on TCP 80, {} ({}%) redirected to HTTPS while {} ({}%) did not.".format(
    total, len(https), round(len(https)/total*100,2), len(http), round(len(http)/total*100,2)
))

print("Of the {} hosts loaded over HTTPS, {} ({}%) sent HSTS headers".format(
    len(https), len(hsts), round(len(hsts)/len(https)*100,2)
))
pass
