#!/usr/bin/env python
"""
Use nvidia-settings to tune 1070
"""
import subprocess
import os
import logging
logging.basicConfig(level=logging.INFO)


def tune():
    """
    set memory core and clock offset
    """
    mem_offset = 1100
    core_offset = 0

    logging.info("setting up 1070 memory clock")

    env = os.environ
    env['DISPLAY'] = ":0"
    env['XAUTHORITY'] = "/var/run/lightdm/root/:0"

    subprocess.check_call(['nvidia-settings',
                           '--assign',
                           "GPUGraphicsClockOffset[3]=%d" % (core_offset),
                           '--assign',
                           "GPUMemoryTransferRateOffset[3]=%d" % (mem_offset)],
                          env=env)

if __name__ == "__main__":
    tune()
