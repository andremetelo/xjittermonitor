#!/usr/bin/python3

import socket
import sys
import time
import statistics
from collections import deque

def get_tcp_latency(host, port=80, timeout=2):
    """Measures TCP handshake latency."""
    start_time = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (time.perf_counter() - start_time) * 1000  # Convert to ms
    except (socket.timeout, ConnectionRefusedError, socket.gaierror):
        return None

def monitor_jitter(host, port=80, interval=1):
    history = []
    last_10 = deque(maxlen=10)
    last_50 = deque(maxlen=50)
    prev_latency = None
    
    print(f"Monitoring Web-TCP jitter for {host}:{port}")
    print(f"{'Sample':<8} | {'Latency':<10} | {'Jitter':<10} | {'Avg (10)':<10} | {'Avg (50)':<10} | {'Full Avg':<10}")
    print("-" * 75)

    try:
        while True:
            latency = get_tcp_latency(host, port)
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
                print("Connection failed/timed out.")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    # Usage: python script.py <host> <port>
    target_host = sys.argv[1] if len(sys.argv) > 1 else "google.com"
    target_port = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    monitor_jitter(target_host, target_port)