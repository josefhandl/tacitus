
# Tacitus

REST API for NAS systems for obtaining diagnostic and disk health information.

Features:
Disk info: S.M.A.R.T. health status, temperature, name, model, serial number...
ZFS: zpool health, capacity info, fragmentation
WireGuard: available interfaces, connected peers


```
# list all drives includes ssds, loop, drive volumes
'lsblk --json --output NAME,TYPE,MOUNTPOINTS --tree'

# check the hdd status but prevent from wake up
hdparm -C /dev/sda
'smartctl -i -a --json -n standby -d sat /dev/sda'

# TODO check /dev/disk/by-id to match the right drive instead of the /dev/sdx mountpoint

# TODO check hdd vs ssd + smart
'sudo smartctl -a /dev/nvme0 --json'
```
