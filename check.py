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

min_delta = -40
logging.basicConfig( level=logging.INFO )

last_hashrate = 0
not_match_times = 0

def restart_miner(msg):
    global last_hashrate
    global not_match_times
    last_hashrate = 0
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
        delta = hashrate - last_hashrate
        logging.info('Speed = %.2f Mh/s, delta = %.2f', hashrate, delta)
        last_hashrate = hashrate
        if delta < min_delta:
            restart_miner('Hashrate decreased too much. Restart miner')
    elif re.search(r'error', output, re.IGNORECASE):
        restart_miner('Miner has errors. Restart miner')
    else:
        not_match_times += 1
        if not_match_times > 5:
            restart_miner('Did not read hashrate for consective 5 times. Restart miner')
    time.sleep(60)
