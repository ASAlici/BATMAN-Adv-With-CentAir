#!/usr/bin/env python3

import threading
import time
import subprocess
import csv
import os
import argparse
import netifaces
import datetime

filename = ""
csv_file = None
csv_writer = None
duration=60
task_finished = threading.Event()


def get_interface_ip(interface_name):
    try:
        # Get all addresses for the interface
        addresses = netifaces.ifaddresses(interface_name)
        
        # Get IPv4 address (AF_INET = 2)
        ipv4_info = addresses.get(netifaces.AF_INET)
        if ipv4_info:
            return ipv4_info[0]['addr']
        return None
    except ValueError:
        print(f"Interface {interface_name} not found")
        return None

def cleanup():
    global csv_file
    if csv_file and not csv_file.closed:
        csv_file.close()
        print(f"\nClosed file: {filename}")

def periodic_task():
    global csv_writer, csv_file, duration
    last_total = None
    timestamp = 0
    
    while timestamp<(duration+1):
        try:
            process = subprocess.Popen(
                ['batctl', 's'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            stdout_stat, _ = process.communicate()
            
            if process.returncode != 0:
                print(f"batctl command failed: {stdout_stat}")
                time.sleep(1)
                continue
            
            stat_dict = make_dict(stdout_stat)
            
            # Check if collision key exists
            if 'collision' not in stat_dict:
                print("Warning: 'collision' not found in batctl output")
                time.sleep(1)
                continue
            
            current_total = stat_dict['collision']
            
            if last_total is not None:
                diff = current_total - last_total
                row = {'Time': f'{timestamp}:{timestamp+1}', 'Collisions': diff}
                csv_writer.writerow(row)
                csv_file.flush()  # Ensure data is written
            
            last_total = current_total
            timestamp += 1
            
        except Exception as e:
            print(f"Error in periodic_task: {e}")
        
        time.sleep(1)
    task_finished.set()
    print(f"Data collection completed after {duration} seconds")

def make_dict(stdout_stat):
    data_dict = {}
    for line in stdout_stat.strip().split('\n'):
        if ':' in line:
            key, value = line.strip().split(':', 1)
            key = key.strip()
            value = value.strip()
            try:
                data_dict[key] = int(value)
            except ValueError:
                data_dict[key] = value
    return data_dict

parser = argparse.ArgumentParser(description='Collect collision statistics')


# Optional arguments
parser.add_argument('-t', '--time', type=int, default=60, help='Test duration as seconds')
args = parser.parse_args()


duration=args.time

ip_addr=get_interface_ip('bat0')
filename = f"coll_stats_{ip_addr}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"



# Remove existing file
if os.path.isfile(filename):
    os.remove(filename)

# Open CSV file once
try:
    csv_file = open(filename, 'w', newline='')
    fieldnames = ['Time', 'Collisions']
    csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    csv_writer.writeheader()
    print(f"Started collecting data to {filename}")
    
    # Start the periodic task
    timer_thread = threading.Thread(target=periodic_task)
    timer_thread.daemon = True
    timer_thread.start()
    
    task_finished.wait()
        
except KeyboardInterrupt:
    print("Stopping...")
except Exception as e:
    print(f"Error: {e}")
finally:
    cleanup()