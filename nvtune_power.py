#!/usr/bin/env python
"""
Use nvidia-smi and nvidia-settings to tune 1070
"""
import subprocess
import os
import time
import re
import logging
logging.basicConfig(level=logging.INFO)

def tune():
    """
    tune power
    """
    POWER_LIMIT = 110
    print """
    mem +1400
    Power	Rate
    90	46449029.6
    100	55574528
    ->110	59663974.4
    120	60333514.2
    130	58043382.1
    """
    logging.info("setting up 1070")

    subprocess.check_call(['nvidia-smi', '-pm',  '1'])
    time.sleep(10)
    subprocess.check_call(['nvidia-smi', '-pl', repr(POWER_LIMIT)])


if __name__ == "__main__":
    tune()