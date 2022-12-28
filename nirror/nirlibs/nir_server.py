"""start syncing binary cache here"""

# Copyright 2022 decembercumulus (I. Tam) <tamik@duck.com>
#
# This file is part of Nirror.
#
# Nirror is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version
#
# Nirror is distributed in the hope that it will be u Ka-yiu Tamseful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details
#
# You should have received a copy of the GNU General Public License along
# with Nirror. If not, see <https://www.gnu.org/licenses/>.

import os
import json
import asyncio

try:
    from . import database, download, cowsay
except ImportError:
    import database
    import download
    import cowsay

cfg_dir = os.path.abspath(f"{__file__}/../../../userdata/config.json")


@database.ignore
async def create_config():
    """create config if not exists"""
    to_be_saved = {
        "port": 8080,
        "channel": ["nixpkgs-unstable"],
        "refresh_interval_mins": 15,
        "remove_binary_days": 90,
        "priority": 4
    }
    os.makedirs(
        name=os.path.abspath(f"{__file__}/../../../userdata/nar/"),
        exist_ok=True
    )
    if not os.path.isfile(cfg_dir):
        with open(cfg_dir, "w+") as outfile:
            outfile.write(to_be_saved)
    return True


async def get_new_pkgs(channels: list):
    """return a list of nixpkgs to be downloaded"""
    all_upstream_packages = []
    for this_ch in channels:
        all_upstream_packages += \
            (await download.get_lastest_packages(this_ch))
    return list(
        set(all_upstream_packages)
        - set(await database.storepaths_in_db())
    )


async def server_info(priority=40):
    """return nix-cache-info"""
    return (b'StoreDir: /nix/store\n'
            b'WantMassQuery: 1\n'
            b'Priority: %i\n' % priority)


async def unfortune():
    """cowsay"""
    return cowsay.cowsay()


def localhost_port():
    configs = json.load(open(cfg_dir))
    return configs["port"]


async def server_loop():
    """start server here"""
    await create_config()
    await database.create_db()
    configs = json.load(open(cfg_dir))
    while True:
        await database.dump_old(configs["remove_binary_days"])
        await download.get_nix_binary(
            (await get_new_pkgs(configs['channel']))[0:114])
        await asyncio.sleep(configs["refresh_interval_mins"] * 60)
