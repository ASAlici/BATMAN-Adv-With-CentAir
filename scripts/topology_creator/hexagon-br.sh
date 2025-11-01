#!/bin/bash
screen qemu-system-x86_64 -drive file=Ubuntu1.qcow2,format=qcow2,snapshot=on -enable-kvm -m 512M \
    -netdev tap,id=mynet0,ifname=tap0,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet0,mac=02:ba:de:af:fd:00 \
    -netdev tap,id=mynet1,ifname=node0,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet1,mac=02:ba:de:af:fe:00
screen qemu-system-x86_64 -drive file=Ubuntu1.qcow2,format=qcow2,snapshot=on -enable-kvm -m 512M \
    -netdev tap,id=mynet0,ifname=tap1,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet0,mac=02:ba:de:af:fd:01 \
    -netdev tap,id=mynet1,ifname=node1,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet1,mac=02:ba:de:af:fe:01
screen qemu-system-x86_64 -drive file=Ubuntu1.qcow2,format=qcow2,snapshot=on -enable-kvm -m 512M \
    -netdev tap,id=mynet0,ifname=tap3,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet0,mac=02:ba:de:af:fd:03 \
    -netdev tap,id=mynet1,ifname=node3,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet1,mac=02:ba:de:af:fe:03
screen qemu-system-x86_64 -drive file=Ubuntu1.qcow2,format=qcow2,snapshot=on -enable-kvm -m 512M \
    -netdev tap,id=mynet0,ifname=tap4,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet0,mac=02:ba:de:af:fd:04 \
    -netdev tap,id=mynet1,ifname=node4,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet1,mac=02:ba:de:af:fe:04
screen qemu-system-x86_64 -drive file=Ubuntu1.qcow2,format=qcow2,snapshot=on -enable-kvm -m 512M \
    -netdev tap,id=mynet0,ifname=tap2,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet0,mac=02:ba:de:af:fd:02 \
    -netdev tap,id=mynet1,ifname=node2,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet1,mac=02:ba:de:af:fe:02
screen qemu-system-x86_64 -drive file=Ubuntu1.qcow2,format=qcow2,snapshot=on -enable-kvm -m 512M \
    -netdev tap,id=mynet0,ifname=tap5,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet0,mac=02:ba:de:af:fd:05 \
    -netdev tap,id=mynet1,ifname=node5,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet1,mac=02:ba:de:af:fe:05
screen qemu-system-x86_64 -drive file=Ubuntu1.qcow2,format=qcow2,snapshot=on -enable-kvm -m 512M \
    -netdev tap,id=mynet0,ifname=tap6,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet0,mac=02:ba:de:af:fd:06 \
    -netdev tap,id=mynet1,ifname=node6,script=no,downscript=no \
    -device virtio-net-pci,netdev=mynet1,mac=02:ba:de:af:fe:06
