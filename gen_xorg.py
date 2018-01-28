#!/usr/bin/env python
"""
There should be one Intel gpu on motherboard for regular display
and all other NVIDIA GPU for mining
"""
import subprocess
import re

pci_list = []
GPU_INFO = {
      'Intel': {'driver': 'intel', 'venderName': 'Intel'},
      'NVIDIA': {'driver': 'nvidia', 'venderName': 'NVIDIA Corporation'}
     }
pci_output = subprocess.check_output(['lspci'])
pattern = re.compile(r'^(\d+):(\d+)\.(\d+)\sVGA\s.+\s(NVIDIA|Intel)\s')
seq = 0
layout_string = 'Section "ServerLayout"\n\tIdentifier\t"Layout0"\n'
config = """
Section "Files"
EndSection

Section "InputDevice"
    Identifier     "Mouse0"
    Driver         "mouse"
    Option         "Protocol" "auto"
    Option         "Device" "/dev/psaux"
    Option         "Emulate3Buttons" "no"
    Option         "ZAxisMapping" "4 5"
EndSection

Section "InputDevice"
    Identifier     "Keyboard0"
    Driver         "kbd"
EndSection

Section "Monitor"
    Identifier     "Monitor0"
    VendorName     "Unknown"
    ModelName      "Unknown"
    HorizSync       28.0 - 33.0
    VertRefresh     43.0 - 72.0
    Option         "DPMS"
EndSection

"""

for line in pci_output.split('\n'):
    match = pattern.search(line)
    if match:
        addresses = [int(x) for x in [match.group(1), match.group(2), match.group(3)]]
        pci_list.append('PCI:%d:%d:%d' % tuple(addresses))
        vender = match.group(4)
	config += 'Section "Device"\n'
	config += '\tIdentifier\t"Device%d"\n' % seq
        config += '\tDriver\t"%s"\n' % GPU_INFO[vender]['driver']
        config += '\tVenderName\t"%s"\n' % GPU_INFO[vender]['venderName']
        config += '\tBusID\t"PCI:%d:%d:%d"\n' % tuple(addresses)
        if vender == 'NVIDIA':
            config += '\tOption\t"Coolbits" "31"\n'
            config += '\tOption\t"onnectedMonitor" "DFP-0"\n'
            config += '\tOption\t"ustomEDID" "DFP-0:/etc/X11/edid.bin"\n'
        config += 'EndSection\n\n'
        config += 'Section "Screen"\n'
        config += '\tIdentifier\t"Screen%d"\n' % seq
        config += '\tDevice\t"Device%d"\n' % seq
        if vender == 'Intel':
            config += '\tMonitor\t"Monitor%d"\n' % seq
            config += '\tDefaultDepth\t24\n'
            config += '\tSubSection\t"Display"\n'
            config += '\t\tDepth\t24\n'
            config += '\tEndSubSection\n'
        if vender == 'NVIDIA':
            config += '\tOption\t"UseDisplayDevice" "none"\n'
        config += 'EndSection\n\n'
        layout_string += '\tScreen\t%d "Screen%d" 0 0\n' % (seq, seq)
        seq += 1
 
            
layout_string += '\tInputDevice    "Mouse0" "CorePointer"\nEndSection\n\n'  

print layout_string
print config
