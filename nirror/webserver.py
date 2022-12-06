# Copyright 2022 I. Tam (Ka-yiu Tam) <tamik@duck.com>
#
# This file is part of Nirror.
# Nirror is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version
#
# Nirror is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details
#
# You should have received a copy of the GNU General Public License along
# with Nirror. If not, see <https://www.gnu.org/licenses/>.

import os
import asyncio
import logging
import json

import uvicorn
import aiohttp
from blacksheep import Application, file, not_found
from nirlibs import crud, fetch

app = Application()

config = json.load(
    open(os.path.abspath(f'{__file__}/../../userdata/config.json'), encoding='utf-8'))


async def download_all_bin(session, channels=config['channel']):
    """Download everything given stated in the lastest StorePaths"""
    try:
        for channel in channels:
            for storepath in await fetch.store_paths(session, channel):
                await crud.download_cache(storepath, session)
    except Exception:
        pass


async def mirror_upstream(restart_minutes=15, recycle_period=90):
    """Start Syncing Upstream."""
    logging.basicConfig(level=logging.INFO)
    await crud.initialise()
    while True:
        async with aiohttp.ClientSession() as session:
            await crud.recycle_unused(recycle_period)
            await download_all_bin(session)
            await asyncio.sleep(restart_minutes * 60)
        await asyncio.sleep(restart_minutes * 60)


async def configure_background_tasks(app):
    asyncio.get_event_loop().create_task(
        mirror_upstream(
            restart_minutes=config['refresh_interval_mins'],
            recycle_period=config['remove_binary_days']))


@app.route("/nar/<narname>")
async def route_narbin(narname):
    return file(
        value=await crud.read_binary_cache(narname),
        content_type="application/x-nix-nar"
    )


@app.route("/<narinfo>.narinfo")
async def route_narinfo(narinfo):
    try:
        return file(
            value=await crud.read_narinfo(narinfo),
            content_type="text/x-nix-narinfo"
        )
    except:
        not_found()


@app.route("/")
async def route_index():
    return (" _______________ \n"
            "( Nirror works! )\n"
            " --------------- \n"
            "        o   ^__^\n"
            "         o  (==)\_______\n"
            "            (__)\       )\/\\\n"
            "                ||----w |\n"
            "                ||     ||\n")


if __name__ == '__main__':
    app.on_start += configure_background_tasks
    uvicorn.run(
        app=f"{__name__}:app",
        host="0.0.0.0",
        port=config['port'])
