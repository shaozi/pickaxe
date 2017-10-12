#!/bin/bash

MEM_OFFSET=1000

echo << EOL
mem +1400
Power	Rate
  90	46449029.6
  100	55574528
->110	59663974.4
  120	60333514.2
  130	58043382.1
EOL

echo "setting up 1070"

nvidia-smi -pm 1
echo "limit power"
nvidia-smi -i 0 -pl 110
nvidia-smi -i 1 -pl 110
nvidia-smi -i 2 -pl 115
nvidia-smi -i 3 -pl 110
nvidia-smi -i 4 -pl 110
nvidia-smi -i 5 -pl 110


for i in $(seq 0 5); do
  echo "setting memory over clock $i to +$MEM_OFFSET"
  DISPLAY=:0 XAUTHORITY=/var/run/lightdm/root/:0 nvidia-settings --assign "[gpu:$i]/GPUGraphicsClockOffset[3]=0" --assign "[gpu:$i]/GPUMemoryTransferRateOffset[3]=$MEM_OFFSET"
done
