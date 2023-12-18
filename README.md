
# Tacitus

REST API for NAS systems for obtaining diagnostic and disk health information.

Modules:
- **Drives**: S.M.A.R.T. health status, temperature, name, model, serial number...
- **ZFS**: zpool health, capacity info, fragmentation
- **WireGuard**: available interfaces, connected peers

## Prerequisites

**The following instructions are for Ubuntu (22.04.) If you use another distribution follow the instructions for yours.**

- Basic packages:  
`sudo apt install make python3 python3-pip python3-venv`

Each module has own prerequisites.

- **Drives** module:  
`sudo apt install hdparm smartmontools`

- **ZFS** module:  
`sudo apt install zfsutils-linux`

- **WireGuard** module:  
`sudo apt install wireguard wireguard-tools`

## Installation

TODO

```
cd api/wrappers
sudo make
```