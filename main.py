#!venv/bin/python3

import re
import subprocess
import json

from typing import List
from loguru import logger
from pymonad.maybe import Maybe, Just, Nothing
from pydantic import parse_obj_as, ValidationError

from models.lsblk import LsblkRoot, BlockDevice
from models.smartctl import SmartctlRoot, Device
from models.zpool import ZpoolStatus, ZpoolList
from models.wireguard import WireguardStatus, WireguardPeer, WireguardPeerTransfer


def run_cmd(cmd: str, allowed_ret_codes: List[int] = [0]):
    # convert str to List[str]
    cmd_list = list()
    cmd_tmp = cmd.split(' ')
    for word in cmd_tmp:
        if word:
            cmd_list.append(word)

    # invoke command
    try:
        result = subprocess.run(cmd_list, capture_output=True)

        # check return code
        valid = False
        for arc in allowed_ret_codes:
            if arc == result.returncode:
                valid = True

        if not valid:
            logger.error(f"Process \"{cmd}\" failed with error: {result.stderr.decode()}")
            return None

        return result

    except subprocess.CalledProcessError as ex:
        logger.error(ex)
        return None
    except Exception as ex:
        logger.error(ex)
        return None


def get_disks_info():
    # (lsblk) get all block devices
    lsblk_json = run_cmd("lsblk --json --output NAME,TYPE,MOUNTPOINTS --tree")
    if not lsblk_json:
        return None

    # fill models with json
    try:
        lsblk_data = LsblkRoot.model_validate(json.loads(lsblk_json.stdout.decode()))
    except ValidationError as ex:
        logger.error(f"Validation the lsblk failed. Exception: {ex}")
        return None
    except Exception as ex:
        logger.error(ex)
        return None

    # filter block devices to find only physical disks
    disks: List[BlockDevice] = list()
    for bd in lsblk_data.blockdevices:
        if bd.type == "disk":
            disks.append(bd)
            print(bd.children)

    # (hdparm) get power mode but avoid to wake up the drives
    # it is also possible to use smartctl, but it requires to know device type to avoid wake up
    # (e.g. USB drives are problematic)
    power_modes = dict()
    for d in disks:
        power_mode = "null"

        hdparm_raw = run_cmd(f"hdparm -C /dev/{d.name}")
        if hdparm_raw:
            r_power_mode = r"^ drive state is:\s+(\w+)"

            for line in hdparm_raw.stdout.decode().split('\n'):
                if match := re.match(r_power_mode, line):
                    power_mode = match.group(1)

        power_modes[f"/dev/{d.name}"] = power_mode

    # get health from all of the physical disks
    smarts: List[SmartctlRoot] = list()
    for d in disks:
        smartctl_json = run_cmd(f"smartctl -i -a --json /dev/{d.name}", [0, 4, 64, 68, 128]) # -d sat
        if not smartctl_json:
            continue

        try:
            smartctl_data = SmartctlRoot.model_validate(json.loads(smartctl_json.stdout.decode()))
            smarts.append(smartctl_data)
        except ValidationError as ex:
            logger.error(f"Validation the smartctl failed with /dev/{d.name} disk. Exception: {ex}")
            return None
        except Exception as ex:
            logger.error(ex)
            return None

    return [json.loads(s.model_dump_json()) for s in smarts]


def get_zpool_status():
    zpool_raw = run_cmd("zpool status")

    p_pool =  r"^  pool:\s+([\w_\-\.]+)"
    p_state = r"^ state:\s+(\w+)"

    statuses: List[ZpoolStatus] = list()

    pool = None
    state = None

    for line in zpool_raw.stdout.decode().split('\n'):
        # "pool"
        if match := re.match(p_pool,  line):
            # if pool is already set, save the last round (and start a new one)
            if pool:
                statuses.append(ZpoolStatus(
                    pool,
                    state
                ))
                pool = None

            pool = match.group(1)

        # "state"
        if match := re.match(p_state, line):
            state = match.group(1)

    statuses.append(ZpoolStatus(
        pool,
        state
    ))

    return [json.loads(s.model_dump_json()) for s in statuses]

def get_zpool_list():
    zpool_raw = run_cmd("zpool list")

    p_group_part =  r"([^\s]+)\s+"
    p_groups = rf'^{p_group_part * 10}([^\s]+)$'

    for line in zpool_raw.stdout.decode().split('\n'):
        if match := re.match(p_groups, line):
            if match.group(1) == 'NAME':
                continue

            # create list of groups and replace '-' with None
            data = [None if g == '-' else g for g in match.groups()]
            # unpack list to the constructor
            result = ZpoolList(*data)

            return json.loads(result.model_dump_json())


def get_wireguard_info():
    wg_raw = run_cmd("wg")

    # interface part
    p_interface = r"^interface:\s+([^\s]+)"

    # peer part
    p_peer             = r"^peer:\s+([^\s]+)"
    p_endpoint         = r"^  endpoint:\s+([^\s]+)"
    p_allowed_ips      = r"^  allowed ips:\s+([^\s]+)"
    p_latest_handshake = r"^  latest handshake:\s+([^\n]+)"
    p_transfer         = r"^  transfer:\s+([^\n]+)\s+received,\s+([^\n]+)\s+sent"

    statuses: List[WireguardStatus] = list()
    interface = None

    peers: List[WireguardPeer] = list()
    peer = None
    endpoint = None
    allowed_ips = None
    latest_handshake = None
    transfer = None

    # helper function
    def save_reset_peer():
        nonlocal peer
        nonlocal endpoint
        nonlocal allowed_ips
        nonlocal latest_handshake
        nonlocal transfer

        peers.append(WireguardPeer(
            peer,
            endpoint,
            allowed_ips,
            latest_handshake,
            transfer
        ))

        peer = None
        endpoint = None
        allowed_ips = None
        latest_handshake = None
        transfer = None

    # helper function
    def save_reset_status():
        nonlocal interface
        nonlocal peers

        statuses.append(WireguardStatus(
            interface,
            peers
        ))

        interface = None
        peers = list()

    # let's parse the "wg" output
    for line in wg_raw.stdout.decode().split('\n'):
        # "interface"
        if match := re.match(p_interface,  line):
            # if interface is already set, save the last interface with all peers (and start a new one)
            if interface:
                # save last peer and reset
                save_reset_peer()

                # save last interface and reset (with peers)
                save_reset_status()

            interface = match.group(1)

        # "peer"
        if match := re.match(p_peer,  line):
            # if peer is already set, save the last round (and start a new one)
            if peer:
                # save last peer and reset
                save_reset_peer()

            peer = match.group(1)

        # "allowed ips"
        if match := re.match(p_allowed_ips, line):
            allowed_ips = match.group(1)

        # "latest handshake"
        if match := re.match(p_latest_handshake, line):
            latest_handshake = match.group(1)

        # "endpoint"
        if match := re.match(p_endpoint, line):
            endpoint = match.group(1)

        # "transfer"
        if match := re.match(p_transfer, line):
            transfer = WireguardPeerTransfer(
                match.group(1),
                match.group(2)
            )

    # save the last section
    save_reset_peer()
    save_reset_status()

    return [json.loads(s.model_dump_json()) for s in statuses]

def system_reboot():
    run_cmd("reboot")

def system_shutdown():
    run_cmd("shutdown -P now")

# TODO nebude lepsi tento balik? unattended-upgrades
def system_update():
    run_cmd("apt update && apt upgrade -y")


#print(get_disks_info())
print(get_zpool_list())
#print(get_zpool_status())
#print(get_wireguard_info())


