from .._model_base.router import BaseRouter
from ...utilities.terminal import run_cmd
import re
from typing import List
from .input_models import WireguardPeer, WireguardPeerTransfer, WireguardStatus
from .output_models import WireguardResult
import json


class Wireguard(BaseRouter):
    PREFIX = "/wireguard"

    async def get_root(self) -> WireguardResult:
        """
        Returns Wireguard status.
        """
        wg_raw = run_cmd("api/wrappers/w_wg")

        # interface part
        p_interface = r"^interface:\s+([^\s]+)"

        # peer part
        # fmt: off
        p_peer             = r"^peer:\s+([^\s]+)"
        p_endpoint         = r"^  endpoint:\s+([^\s]+)"
        p_allowed_ips      = r"^  allowed ips:\s+([^\s]+)"
        p_latest_handshake = r"^  latest handshake:\s+([^\n]+)"
        p_transfer         = r"^  transfer:\s+([^\n]+)\s+received,\s+([^\n]+)\s+sent"
        # fmt: on

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

            peers.append(WireguardPeer(peer, endpoint, allowed_ips, latest_handshake, transfer))

            peer = None
            endpoint = None
            allowed_ips = None
            latest_handshake = None
            transfer = None

        # helper function
        def save_reset_status():
            nonlocal interface
            nonlocal peers

            statuses.append(WireguardStatus(interface, peers))

            interface = None
            peers = list()

        # let's parse the "wg" output
        for line in wg_raw.stdout.decode().split("\n"):
            # "interface"
            if match := re.match(p_interface, line):
                # if interface is already set, save the last interface with all peers (and start a new one)
                if interface:
                    # save last peer and reset
                    save_reset_peer()

                    # save last interface and reset (with peers)
                    save_reset_status()

                interface = match.group(1)

            # "peer"
            if match := re.match(p_peer, line):
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
                transfer = WireguardPeerTransfer(match.group(1), match.group(2))

        # save the last section
        save_reset_peer()
        save_reset_status()

        return {"result": [json.loads(s.model_dump_json()) for s in statuses]}


router = Wireguard()
