#!/usr/bin/env python

import json

lookups = "lookups.json"
www_lookups = "www-lookups.json"
output = "hosts.csv"

hosts = {}
www_hosts = {}

def populate_hosts_from_zdns(filename, d):
    print("Reading {}..".format(filename))
    with open(filename, 'r') as f:
        for line in f:
            j = json.loads(line)

            name = j['name']
            ip = None
            if j.get('data') and j.get('data').get('ipv4_addresses'):
                ip = j['data']['ipv4_addresses'][0]
            d[name] = ip


def augment_hosts_with_www(hosts, www_hosts):
    missing = 0

    for host in hosts:
        if hosts[host]:
            continue

        missing += 1

        www = "www." + host
        if www_hosts.get(www):
            # print("Found {} as {} on {}".format(host, www, www_hosts[www]))
            del hosts[host]
            hosts[www] = www_hosts[www]

    return missing


def write_output_file(hosts, filename):
    missing = 0
    with open(filename, 'w') as f:

        for host in hosts:
            if hosts[host]:
                f.write("{},{}\n".format(hosts[host], host))
            else:
                missing += 1

    return missing

populate_hosts_from_zdns(lookups, hosts)
populate_hosts_from_zdns(www_lookups, www_hosts)

missing = augment_hosts_with_www(hosts, www_hosts)
still_missing = write_output_file(hosts, output)

print("reduced {} missing hosts to {} by using 'www' lookup".format(missing,still_missing))