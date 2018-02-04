#!/usr/bin/python
"""
periodically check the output of ethminer service with journalctl.
If the hashrate drops more than 40M, or if it stops responding,
use systemctl to restart miner service
"""
import subprocess
import re
import time
import logging
import os
import urllib
import urllib2
import json
import threading
import nvtune_clock
import nvtune_power


logging.basicConfig( level=logging.INFO )

def count_gpu():
    output = subprocess.check_output(['lspci'])
    pattern = re.compile(r'VGA.*NVIDIA')
    gpu_count = 0
    for line in output.split('\n'):
        if pattern.search(line):
            gpu_count += 1
    return gpu_count

def check_gpus():
    '''
    check gpu status every 60 seconds.
    if temperatur or power is too high, reboot system.
    '''
    logging.info('GPU monitor starts')
    gpu_count = count_gpu()
    logging.info('Total found {} GPUs'.format(gpu_count))
    while True:
        output = subprocess.check_output(['nvidia-smi', 
                                        '--query-gpu=pci.bus_id,power.draw,clocks.current.memory,temperature.gpu', 
                                        '--format=csv,noheader,nounits'])
        #00000000:01:00.0, 109.31, 4353, 61
        #00000000:02:00.0, 111.24, 4353, 74
        #00000000:04:00.0, 114.56, 4353, 65
        #00000000:07:00.0, 109.66, 4353, 78
        #00000000:08:00.0, 109.40, 4353, 67
        #00000000:09:00.0, 108.94, 4353, 64
        lines = output.split('\n')
        running_gpu_count = 0
        for line in lines:
            vals = line.split(', ')
            if len(vals) != 4:
                continue
            logging.info(line)
            if float(vals[2]) < 3000:
                logging.warning('Memory clock too low. Not mining at all?')
                logging.warning(vals)
            if float(vals[1]) > 120:
                logging.error('Power consumption too high, reboot')
                logging.error(vals)
                os.system('reboot')
            if int(vals[3]) > 90:
                logging.error('CPU too hot, reboot')
                logging.error(vals)
                os.system('reboot')
            else:
                running_gpu_count += 1
        if running_gpu_count < gpu_count:
            logging.error('Some GPU is dead. Only see {} of {} GPUs. Reboot'.format(running_gpu_count, gpu_count))
            os.system('reboot')
        
        time.sleep(60)

def check_hashrate():
    '''
    check and report hashrate every 30 seconds.
    '''
    logging.info('Hashrate monitor starts.')
    hd_serial_number = hd_sn()
    target_rate = count_gpu() * 29
    miss = 0
    last_output = ""
    while True:
        output = subprocess.check_output(['journalctl', '-n', '1', '--quiet', '-u', 'miner'])
        logging.info(output)
        if output == last_output:
            logging.warning('log is not updated!')
            miss += 1
        else:
            match = re.search(r'Speed\s+([0-9\.]+)', output)
            if match:
                hashrate = float(match.group(1))
                post_hashrate(hd_serial_number, hashrate)
                if hashrate >= target_rate:
                    miss = 0
            else:
                logging.warning('Did not find hashrate.')
                miss += 1
        if miss > 5:
            restart_miner('hash rate is too low or missing! restart miner')
        last_output = output
        time.sleep(30)

def restart_miner(msg, delay=30):
    logging.error(msg)
    subprocess.call(['systemctl', 'stop', 'miner'])
    time.sleep(delay)
    subprocess.call(['systemctl', 'start', 'miner'])

def hd_sn():
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

def post_hashrate(hd, rate):
    config = json.load(open('config.json'))
    data = urllib.urlencode({'hd': hd, 'hashrate': rate})
    req = urllib2.Request(config['server'], data)
    try:
        response = urllib2.urlopen(req)
        the_page = response.read()
    except Exception as e:
        logging.warning('post hashrate failed. Exception: %s', e)

if __name__ == "__main__":
    logging.info('sleep 60 seconds to wait for lighdm')
    time.sleep(60)
    
    logging.info('tune GPU')
    nvtune_power.tune()
    time.sleep(5)
    nvtune_clock.tune()
    time.sleep(5)
    logging.info('start miner')
    subprocess.call(['systemctl', 'start', 'miner'])
    time.sleep(60)

    logging.info('Start monitoring')

    gpu_monitor = threading.Thread(target=check_gpus)
    gpu_monitor.start()

    hashrate_monitor = threading.Thread(target=check_hashrate)
    hashrate_monitor.start()
    
    
