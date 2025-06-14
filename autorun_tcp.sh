#!/bin/bash

# Nama sesi screen
SUB_SESSION="sub"
PUB_SESSION="pub"
DATA_SESSION="nav"
MAP_SESSION="map"

# Mengaktifkan lingkungan Conda
source /home/alihasanash/miniconda3/bin/activate moos

# Menjalankan tcp_sub.py di dalam sesi screen "sub"
screen -dmS $SUB_SESSION bash -c "python3 ~/tcp_moos/tcp_sub.py; exec bash"

# Menjalankan tcp_pub.py di dalam sesi screen "pub"
screen -dmS $PUB_SESSION bash -c "python3 ~/tcp_moos/tcp_pub.py; exec bash"

echo "TCP Process Activated"
