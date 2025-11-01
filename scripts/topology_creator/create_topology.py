#!/usr/bin/env python3

import json
import os 
import argparse
import subprocess
import sys

def get_current_user():
    user = os.environ.get('USER')
    print(f"Username'im bu imis: {user}")
    return user

def read_json_file(filename):
    with open(filename,'r') as f:
        config_file=json.load(f)
    return config_file

def bridge_and_taps(config_file,user):
    
    mesh_nodes=config_file.get("mesh_nodes",[])
    bridge_name=config_file.get("bridge_name","")
    #user=get_current_user()

    subprocess.run(["ip", "link", "add", bridge_name, "type", "bridge"])
    subprocess.run(["ip", "link", "add", "host"+bridge_name, "type", "bridge"])

    for node in mesh_nodes:
        subprocess.run(["ip", "tuntap", "add", "dev", node['name'], "mode", "tap", "user", user])
        subprocess.run(["ip", "link", "set", node['name'], "up"])

        subprocess.run(["ip", "tuntap", "add", "dev", "tap" + node['name'][4:], "mode", "tap", "user", user], check=False)
        #subprocess.run(["ip", "addr", "add", f"192.168.102.1{node['name'][4:]}/24", "dev", "tap" + node['name'][4:] ], check=True)
        subprocess.run(["ip", "link", "set", "tap" + node['name'][4:], "up"], check=False)
        
        subprocess.run(["ip", "link", "set", node['name'], "master", bridge_name])
        subprocess.run(["ip", "link", "set", "tap" + node['name'][4:], "master", "host"+bridge_name])
    
    subprocess.run(["ip", "addr", "add", "192.168.102.1/24", "dev", "host"+bridge_name])
    subprocess.run(["ip", "link", "set", bridge_name, "up"])
    subprocess.run(["ip", "link", "set", "host"+bridge_name, "up"])
    #subprocess.run(["ip", "addr", "replace", "192.168.251.1/24", "dev", bridge_name])

def create_nft_script(config_file,user):
    mesh_nodes=config_file.get("mesh_nodes",[])
    bridge_name=config_file.get("bridge_name","")

    filename=bridge_name+".nft"
    
    with open(filename,'w') as file:
        file.write("#!/usr/sbin/nft -f"+"\n")
        file.write("flush ruleset bridge"+"\n")
        file.write("table bridge filter {"+"\n")
        file.write("chain FORWARD {"+"\n")
        file.write("type filter hook forward priority -200; policy accept;"+"\n")
        
        for node in mesh_nodes:
            for link in node["links"]:
                if(link["quality"]>=100):
                    file.write(f'iifname "{node["name"]}" oifname "{link["whom"]}" accept'+"\n")
                else:
                    file.write(f'iifname "{node["name"]}" oifname "{link["whom"]}" numgen random mod 100 < {link["quality"]} accept'+"\n")

        
        file.write(f'meta obrname "{bridge_name}" drop\n')
        file.write("}\n")
        file.write("}\n")

    subprocess.run(["chmod","+x", filename])
    subprocess.run([f"./{filename}"])

def create_qemu_bash_script(config_file,user):
    mesh_nodes=config_file.get("mesh_nodes",[])
    bridge_name=config_file.get("bridge_name","")

    filename=bridge_name+".sh"
    
    with open(filename,'w') as file:
        file.write("#!/bin/bash"+"\n")
                
        for node in mesh_nodes:
            node_name=node["name"]
            two_digit=""
            if(len(node_name)<6):
                two_digit="0"+node_name[4]
            elif(len(node_name)==6):
                two_digit=node_name[4:6]
            two_digit=(hex(int(two_digit)).split('x')[-1]).zfill(2)
            macnode_address="02:ba:de:af:fe:"+two_digit
            tap_name="tap"+node_name[4:]
            mactap_address="02:ba:de:af:fd:"+two_digit
            file.write(f"""screen qemu-system-x86_64 -drive file=Ubuntu1.qcow2,format=qcow2,snapshot=on -enable-kvm -m 512M \\
    -netdev tap,id=mynet0,ifname={tap_name},script=no,downscript=no \\
    -device virtio-net-pci,netdev=mynet0,mac={mactap_address} \\
    -netdev tap,id=mynet1,ifname={node_name},script=no,downscript=no \\
    -device virtio-net-pci,netdev=mynet1,mac={macnode_address}\n""")
    

    subprocess.run(['chown', f'{user}:{user}', filename], check=False)
    subprocess.run(["chmod","+x", filename])

def clean_everything(config_file):
    mesh_nodes=config_file.get("mesh_nodes",[])
    bridge_name=config_file.get("bridge_name","")

    subprocess.run(["nft", "flush", "ruleset", "bridge"], check=False)

    if(bridge_name=="" or mesh_nodes==[]):
        print("I could not read anything meaningful!")
        return 1

    for node in mesh_nodes:
        subprocess.run(['ip', 'link', 'set', node['name'], 'nomaster'])
        subprocess.run(['ip', 'link', 'set', node['name'], 'down'])
        subprocess.run(['ip', 'tuntap', 'del', 'dev', node['name'], 'mode', 'tap'])
        subprocess.run(['ip', 'tuntap', 'del', 'dev', "tap" + node['name'][4:], 'mode', 'tap'])

    subprocess.run(['ip', 'link', 'set', bridge_name, 'down'])
    subprocess.run(['ip', 'link', 'delete', bridge_name, 'type', 'bridge'])

    subprocess.run(['ip', 'link', 'set', "host"+bridge_name, 'down'])
    subprocess.run(['ip', 'link', 'delete', "host"+bridge_name, 'type', 'bridge'])
    
    os.remove(f"{bridge_name}.nft")
    os.remove(f"{bridge_name}.sh")
    #os.remove(f"{bridge_name}_hosts")
    os.remove("hosts")

    print("Everything is gone now... You are ready for fresh start.")


def create_hosts_file(config_file,user):
    mesh_nodes=config_file.get("mesh_nodes",[])
    bridge_name=config_file.get("bridge_name","")

    #filename=bridge_name+"_hosts"
    filename="hosts"
    with open(filename,'w') as file:
        for node in mesh_nodes:
            node_name=node["name"]
            two_digit=""
            if(len(node_name)<6):
                two_digit=node_name[4]
            elif(len(node_name)==6):
                two_digit=node_name[4:6]
            file.write(f"192.168.102.1{two_digit}\n")
    subprocess.run(['chown', f'{user}:{user}', filename], check=False)

def main():

    parser=argparse.ArgumentParser(description="Script to create testing environment for the BATMANNET")
    parser.add_argument("config_file", help="Configuration file to process")
    parser.add_argument("--kill", action='store_true')
    parser.add_argument("--create", action='store_true')

    args=parser.parse_args()

    config=read_json_file(args.config_file)
    user="ahmet"
    #config["alive"]==1 and 
    if(args.kill):
        clean_everything(config)

        config["alive"]=0
        with open(args.config_file,'w') as file:
            json.dump(config,file,indent=4)
    elif(args.create):
        
        bridge_and_taps(config,user)
        create_nft_script(config,user)
        create_qemu_bash_script(config,user)
        create_hosts_file(config,user)

        config["alive"]=1
        with open(args.config_file,'w') as file:
            json.dump(config,file,indent=4)


if __name__ == "__main__":
    # Check if running as root
    if os.geteuid() != 0:
        print("This script requires root privileges. Please run with sudo.")
        sys.exit(1)
    
    main()
