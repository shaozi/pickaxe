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

min_delta = -40
logging.basicConfig( level=logging.INFO )

max_hashrate = 0
not_match_times = 0
gpu_count = 0

def check_gpus():
    global gpu_count
    output = subprocess.check_output(['nvidia-smi', '--query-gpu=pci.bus_id,power.draw,clocks.current.memory,temperature.gpu', '--format=csv,noheader,nounits'])
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
        if float(vals[1]) < 100 or int(vals[3]) < 60:
            logging.error(vals)
        else:
            running_gpu_count += 1
    if gpu_count != 0 and running_gpu_count < gpu_count:
        logging.error('%s gpu is dead. reload', gpu_count - running_gpu_count)
        os.system('reboot')
    else:
        gpu_count = running_gpu_count
 
def restart_miner(msg):
    global max_hashrate
    global not_match_times
    max_hashrate = 0
    not_match_times = 0
    subprocess.call(['systemctl', 'restart', 'miner'])
    logging.error(msg)

while True:
    output = subprocess.check_output(['journalctl', '-n', '1', '--quiet', '-u', 'miner'])
    logging.info(output)
    match = re.search(r'Speed\s([0-9\.]+)', output)
    if match:
        not_match_times = 0
        hashrate = float(match.group(1))
        delta = hashrate - max_hashrate
        logging.info('Speed = %.2f Mh/s, delta = %.2f', hashrate, delta)
        if hashrate > max_hashrate:
            max_hashrate = hashrate
        if delta < min_delta:
            restart_miner('Hashrate decreased too much. Restart miner')
    elif re.search(r'error', output, re.IGNORECASE):
        restart_miner('Miner has errors. Restart miner')
    else:
        not_match_times += 1
        if not_match_times > 5:
            restart_miner('Did not read hashrate for consective 5 times. Restart miner')
    check_gpus()
    time.sleep(60)
