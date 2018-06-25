#!/usr/bin/env python

import json
from datetime import datetime

input = "http.json"

HASHMARK=5000

print("Reading {}..".format(input))
if HASHMARK>0:
    print("Each dot represents {} lines processed:".format(HASHMARK))

redir_to_http = []

# good certs
valid_cert = []
# bad certs
untrusted_cert = []
expired_cert = []
unmatched_cert = []
# other
hsts = []
errors = []

i = 0
total = 0
bad_certs = 0
today = datetime.today()
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

        total += 1

        terminal_scheme = j['data']['http']['response']['request']['url']['scheme']

        # example: reelflies.ca
        if terminal_scheme == "http":
            redir_to_http.append(host)
            continue

        # check the certificate
        not_after_str = j['data']['http']['response']['request']['tls_handshake']['server_certificates']['certificate']['parsed']['validity']['end']
        not_after = datetime.strptime(not_after_str, "%Y-%m-%dT%H:%M:%SZ")

        # is it expired?
        is_expired = datetime.today() > not_after
        if is_expired:
            expired_cert.append(host)

        # does it have a matching SAN/CN?
        is_not_matching = True
        if j['data']['http']['response']['request']['tls_handshake']['server_certificates']['validation'].get(
                'matches_domain'):
            is_not_matching = not j['data']['http']['response']['request']['tls_handshake']['server_certificates']['validation'][
                'matches_domain']
        if is_not_matching and not is_expired:
            unmatched_cert.append(host)

        # is it trusted?
        is_not_trusted = not j['data']['http']['response']['request']['tls_handshake']['server_certificates']['validation']['browser_trusted']
        # i _think_ that anything expired will also come back "not trusted"; excluding non-matching CN/SAN for safety as well
        # see https://github.com/zmap/zgrab/issues/323
        if is_not_trusted and not (is_expired or is_not_matching):
            untrusted_cert.append(host)

        if is_expired or is_not_matching or is_not_trusted:
            bad_certs += 1
        else:
            valid_cert.append(host)

        # also check hsts
        headers = j['data']['http']['response'].get('headers')
        if headers and headers.get('strict_transport_security'):
            hsts.append(host)
print("Done reading file.")

print("Of the {} total hosts we could connect to on TCP 443, {} ({}%) had valid certificates while {} ({}%) did not. {} ({}%) redirected back to HTTP".format(
    total, len(valid_cert), round(len(valid_cert)/total*100,2),
           bad_certs, round(bad_certs/total*100,2),
           len(redir_to_http), round(len(redir_to_http)/total*100,2)
))

print("Of the {} bad certs, {} did not have a matching SAN ({}%), {} ({}%) were expired, and {} ({}%) were untrusted".format(
    bad_certs, len(unmatched_cert), round(len(unmatched_cert)/bad_certs*100,2),
               len(expired_cert), round(len(expired_cert)/bad_certs*100,2),
               len(untrusted_cert), round(len(untrusted_cert)/bad_certs*100,2),
))

print("Of the {} hosts loaded over HTTPS, {} ({}%) sent HSTS headers".format(
    total, len(hsts), round(len(hsts)/total*100,2)
))


