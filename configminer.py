#!/usr/bin/env python
"""
Init configure.
config is read from config.json, except ip is read from a server.
homepath needs to have a bin folder that has ethmine
"""
import urllib2
import subprocess
import re
import os
import sys
import json
import logging
logging.basicConfig(format='%(asctime)s %(message)s', filename='/var/log/setip.log', level=logging.INFO)

import gen_xorg

def get_config():
    return json.load(open('config.json'))

def get_hd_sn():
    output = subprocess.check_output(['ls', '/dev/disk/by-id'])
    pattern = re.compile(r'ata.*_([A-Z\d]+)')
    match = pattern.match(output)
    if match:
        serial_number = match.group(1)
        logging.info('hd serial number = {0}'.format(serial_number))
        return serial_number
    else:
        logging.error('Cannot get hd serial number. output = {0}'.format(output))
        return 0

def update_netplan(ip):
    config = """
network:
    version: 2
    renderer: networkd
    ethernets:
        id0:
            match: 
                driver: alx
            addresses: [{}/24]
            gateway4: 192.168.1.254
            nameservers:
                search: [itestu.com]
                addresses: [192.168.1.254, 8.8.8.8]
    """.format(ip)
    cfg_file = open('/etc/netplan/01-netcfg.yaml', 'w')
    cfg_file.write(config)
    cfg_file.close()
    logging.info('netplan file is updated.')

def change_static_ip():
    hd_serial = get_hd_sn()
    iphost = get_iphost(hd_serial)
    if iphost > 0:
        update_netplan('192.168.1.{}'.format(iphost))
        return iphost
    else:
        logging.warning('cannot get a valid ip host number from the server')
        return 0

def change_hostname(hostname):
    hostname_file = open('/etc/hostname', 'w')
    hostname_file.write('{}\n'.format(hostname))
    hostname_file.close()
    hostname_file = open('/etc/hosts', 'a')
    hostname_file.write('\n127.0.0.1 {}\n'.format(hostname))
    hostname_file.close()
    subprocess.check_call(['hostname', hostname])

def setup_services(miner, config):
    config['miner'] = miner
    miner_service = """
    [Unit]
        Description=Ethereum Miner
        After=network.target
        Requires=checkminer.service

    [Service]
        ExecStart={ethminer} --farm-recheck 3000 -U -S {poolserver1} -FS {poolserver2} -O {account}.{miner}/{email}
        Restart=always
        User={user}
        Group={group}
        Environment=TERM=xterm-256color

    [Install]
        WantedBy=multi-user.target
    """.format(**config)
    service_file = open('/etc/systemd/system/miner.service', 'w')
    service_file.write(miner_service)
    service_file.close()


    checkminer_service = """
    [Unit]
        Description=Tune then start Ethereum Miner, and check
        After=network.target

    [Service]
        ExecStart=/usr/bin/python check.py
        WorkingDirectory={path}
        Restart=always
        User=root
        Group=root
        Environment=TERM=xterm-256color

    [Install]
        WantedBy=multi-user.target
    """.format(**config)

    service_file = open('/etc/systemd/system/checkminer.service', 'w')
    service_file.write(checkminer_service)
    service_file.close()

    subprocess.check_call(['systemctl', 'daemon-reload'])
    subprocess.check_call(['systemctl', 'disable', 'miner'])
    subprocess.check_call(['systemctl', 'enable', 'checkminer'])

def get_iphost(hd_serial_number):
    """
    get ip host from the server
    """
    config = get_config()
    api_url = config['server']
    req = urllib2.Request(api_url + "/" + hd_serial_number, data=None)
    connection = urllib2.urlopen(req)
    body = connection.read()
    iphost = body
    logging.info('got ip host = %s', iphost)
    return int(iphost)

def main():
    config = get_config()
    iphost = change_static_ip()
    if iphost != 0:
        miner = "miner{0}".format(iphost)
    else:
        miner = 'miner0'
    change_hostname(miner)
    gen_xorg.gen_conf()
    setup_services(miner, config)

    done_file = open('/done', 'w')
    done_file.write(miner)
    done_file.close()
    logging.warning('reboot system')
    os.system('reboot')


if __name__ == "__main__":
    config = get_config()
    hd_sn = get_hd_sn()
    if hd_sn == config['skipSN']:
        sys.exit(0)
    if os.path.exists('/done'):
        logging.info('done file found. Exist init setup')
        sys.exit(0)
    else:
        main()
    