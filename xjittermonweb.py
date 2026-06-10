#!/usr/bin/python3
"""Real-time Network Latency and Jitter Monitor.

This script measures TCP handshake latency to a specified target host and port,
calculates jitter based on the absolute variance between consecutive measurements,
and displays real-time telemetry both on a Matplotlib graph and the CLI terminal.
"""

import socket
import sys
import time
import statistics
import argparse
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration
MAX_POINTS = 50  # Number of data points visible on the chart timeline at once

# Data storage structures
times = deque(maxlen=MAX_POINTS)
latency_data = deque(maxlen=MAX_POINTS)
jitter_data = deque(maxlen=MAX_POINTS)

# Fixed-size deques for rolling window calculations
lat_10 = deque(maxlen=10)
lat_50 = deque(maxlen=50)
jit_10 = deque(maxlen=10)
jit_50 = deque(maxlen=50)

# Full comprehensive historical logs
all_latencies = []
all_jitters = []

# Initialization state variables
prev_latency = None
start_timestamp = time.time()
sample_count = 0

def get_tcp_latency(host, port=80, timeout=2):
    """Measures the network TCP handshake latency to a destination endpoint.

    Args:
        host (str): The destination IP address or domain name.
        port (int): The target TCP port number.
        timeout (int): Socket connection timeout window in seconds.

    Returns:
        float: Calculated connection latency in milliseconds (ms),
               or None if the connection times out or fails.
    """
    start_time = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return (time.perf_counter() - start_time) * 1000  # Convert to ms
    except (socket.timeout, ConnectionRefusedError, socket.gaierror):
        return None

def update_chart(frame):
    """Core animation update loop execution driver.

    Queries the target endpoint, performs statistical math operations across
    specified historical thresholds, logs data to CLI, and redraws the graph.
    """
    global prev_latency, sample_count
    
    latency = get_tcp_latency(args.host, args.port, timeout=max(2.0, args.interval))
    current_time = time.time() - start_timestamp
    
    if latency is not None:
        sample_count += 1
        times.append(current_time)
        latency_data.append(latency)
        all_latencies.append(latency)
        lat_10.append(latency)
        lat_50.append(latency)
        
        # Calculate current Jitter metrics
        if prev_latency is not None:
            jitter = abs(latency - prev_latency)
            jitter_data.append(jitter)
            all_jitters.append(jitter)
            jit_10.append(jitter)
            jit_50.append(jitter)
        else:
            jitter_data.append(0)
            all_jitters.append(0)
            jit_10.append(0)
            jit_50.append(0)
            
        prev_latency = latency
    else:
        print(f"[{time.strftime('%H:%M:%S')}] Connection failed or timed out.")
        return line_lat, line_jit

    # Render data lines
    line_lat.set_data(times, latency_data)
    line_jit.set_data(times, jitter_data)
    
    # Process Latency calculations
    avg_lat_all = statistics.mean(all_latencies)
    avg_lat_50 = statistics.mean(lat_50)
    avg_lat_10 = statistics.mean(lat_10)
    max_lat_all = max(all_latencies)
    max_lat_50 = max(lat_50)
    max_lat_10 = max(lat_10)
    
    # Process Jitter calculations
    avg_jit_all = statistics.mean(all_jitters)
    avg_jit_50 = statistics.mean(jit_50)
    avg_jit_10 = statistics.mean(jit_10)
    max_jit_all = max(all_jitters)
    max_jit_50 = max(jit_50)
    max_jit_10 = max(jit_10)
    
    # Build text history snippets
    last_3_lat = list(latency_data)[-3:]
    last_3_jit = list(jitter_data)[-3:]
    lat_history_str = " | ".join(f"{x:.1f}" for x in last_3_lat)
    jit_history_str = " | ".join(f"{x:.1f}" for x in last_3_jit)
    
    # Update graphical chart card text matrices
    text_lat.set_text(
        f"Latency (10 | 50 | All)\n"
        f"Avg: [{avg_lat_10:.1f} | {avg_lat_50:.1f} | {avg_lat_all:.1f}]\n"
        f"Max: [{max_lat_10:.1f} | {max_lat_50:.1f} | {max_lat_all:.1f}]\n"
        f"Recent: [{lat_history_str}]"
    )
    text_jit.set_text(
        f"Jitter (10 | 50 | All)\n"
        f"Avg: [{avg_jit_10:.1f} | {avg_jit_50:.1f} | {avg_jit_all:.1f}]\n"
        f"Max: [{max_jit_10:.1f} | {max_jit_50:.1f} | {max_jit_all:.1f}]\n"
        f"Recent: [{jit_history_str}]"
    )
    
    # Print clean live telemetry line out into terminal
    print(f"Sample #{sample_count:<4} | "
          f"Lat: {latency:.1f}ms (Avg10/50/All: {avg_lat_10:.1f}/{avg_lat_50:.1f}/{avg_lat_all:.1f}ms) "
          f"(Max10/50/All: {max_lat_10:.1f}/{max_lat_50:.1f}/{max_lat_all:.1f}ms) | "
          f"Jit: {jitter_data[-1]:.1f}ms (Avg10/50/All: {avg_jit_10:.1f}/{avg_jit_50:.1f}/{avg_jit_all:.1f}ms) "
          f"(Max10/50/All: {max_jit_10:.1f}/{max_jit_50:.1f}/{max_jit_all:.1f}ms)")

    # Bound maximum horizon baseline tracking bars
    hline_lat.set_ydata([max_lat_all, max_lat_all])
    hline_jit.set_ydata([max_jit_all, max_jit_all])
    
    # Reposition dynamic graph boundary parameters
    ax1.set_xlim(min(times), max(times) + (args.interval * 0.5))
    
    window_max_lat = max(latency_data) if latency_data else 10
    window_max_jit = max(jitter_data) if jitter_data else 10
    
    ax1.set_ylim(0, max(window_max_lat, max_lat_all) * 1.35)
    ax2.set_ylim(0, max(window_max_jit, max_jit_all) * 1.35)
    
    return line_lat, line_jit, text_lat, text_jit, hline_lat, hline_jit

if __name__ == "__main__":
    # Setup argparse environment
    parser = argparse.ArgumentParser(
        description="Real-time graphical network monitor for TCP latency and jitter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python script.py google.com
  python script.py 1.1.1.1 --port 443 --interval 0.5
  python script.py corporate-router.local -p 8080 -i 5"""
    )
    
    parser.add_argument("host", nargs="?", default="google.com",
                        help="Target domain name or IP address to test (default: google.com)")
    parser.add_argument("-p", "--port", type=int, default=80,
                        help="Target TCP port number (default: 80)")
    parser.add_argument("-i", "--interval", type=float, default=2.0,
                        help="Sampling time interval in seconds (default: 2.0)")

    args = parser.parse_args()
    interval_ms = int(args.interval * 1000)

    print(f"Starting Network Monitor UI for {args.host}:{args.port}...\n"
          f"Sampling Interval: {args.interval} seconds\n"
          f"Format inside text blocks maps to: [ Last 10 | Last 50 | All-Time History ]\n"
          f"---------------------------------------------------------------------------")

    # Layout Initialization Setup
    fig, ax1 = plt.subplots(figsize=(12, 6.5))
    ax2 = ax1.twinx()

    # Latency Canvas Design Styling
    ax1.set_xlabel("Elapsed Time (seconds)", color="black")
    ax1.set_ylabel("TCP Latency (ms)", color="blue")
    line_lat, = ax1.plot([], [], label="Latency", color="blue", linewidth=2)
    hline_lat = ax1.axhline(0, color="blue", linestyle=":", alpha=0.4, label="Max Latency")
    ax1.tick_params(axis='y', labelcolor="blue")
    ax1.grid(True, linestyle="--", alpha=0.3)

    # Jitter Canvas Design Styling
    ax2.set_ylabel("Jitter (ms)", color="darkorange")
    line_jit, = ax2.plot([], [], label="Jitter", color="darkorange", linewidth=1.5, linestyle="-.")
    hline_jit = ax2.axhline(0, color="darkorange", linestyle=":", alpha=0.4, label="Max Jitter")
    ax2.tick_params(axis='y', labelcolor="darkorange")

    # Static Position Coordinates Configuration for Text Metric Boxes
    text_lat = ax1.text(0.02, 0.95, "", transform=ax1.transAxes, color="blue", 
                         fontsize=9, family="monospace", fontweight="bold", va="top",
                         bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="blue"))
    
    text_jit = ax2.text(0.98, 0.95, "", transform=ax2.transAxes, color="darkorange", 
                         fontsize=9, family="monospace", fontweight="bold", va="top", ha="right",
                         bbox=dict(boxstyle="round", facecolor="white", alpha=0.85, edgecolor="darkorange"))

    # Layout compilation adjustments
    fig.suptitle(f"Real-time Network Monitor -> {args.host}:{args.port}", fontsize=12, fontweight="bold")
    fig.tight_layout()

    # Launch GUI Event Execution Pipeline Loop
    ani = FuncAnimation(fig, update_chart, interval=interval_ms, cache_frame_data=False)
    
    plt.show()

