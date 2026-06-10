#!/usr/bin/python3

import os
import sys
import subprocess
import time
import re
import statistics
from collections import deque

def get_ping_latency(host):
    try:
        param = '-n' if os.name == 'nt' else '-c'
        command = ['ping', param, '1', host]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        
        match = re.search(r'time[=<](\d+\.?\d*)', output)
        return float(match.group(1)) if match else None
    except Exception:
        return None

def monitor_jitter(host, interval=1):
    history = []
    last_10 = deque(maxlen=10)
    last_50 = deque(maxlen=50)
    prev_latency = None
    
    print(f"Monitoring ping-jitter for: {host}")
    print(f"{'Sample':<8} | {'Latency':<10} | {'Jitter':<10} | {'Avg (10)':<10} | {'Avg (50)':<10} | {'Full Avg':<10}")
    print("-" * 75)

    try:
        while True:
            latency = get_ping_latency(host)
            if latency is not None:
                if prev_latency is not None:
                    jitter = abs(latency - prev_latency)
                    history.append(jitter)
                    last_10.append(jitter)
                    last_50.append(jitter)
                    
                    print(f"{len(history):<8} | {latency:<10.2f} | {jitter:<10.2f} | "
                          f"{statistics.mean(last_10):<10.2f} | "
                          f"{statistics.mean(last_50):<10.2f} | "
                          f"{statistics.mean(history):<10.2f}")
                prev_latency = latency
            else:
                print("Request timed out.")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    # Check if an argument was provided, otherwise default to Google DNS
    target_host = sys.argv[1] if len(sys.argv) > 1 else "8.8.8.8"
    monitor_jitter(target_host)
