"""
Library for downloading stuffs asynchronously"""

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
import asyncio
import logging
import traceback

from io import BytesIO
from lzma import LZMAFile

import aiofiles
import aiohttp

try:
    from . import database
except ImportError:
    import database


def retry(func_name):
    """Retry until success"""
    # pylint: disable=broad-except
    async def wrapper(*arg, **kwargs):
        while True:
            try:
                return await func_name(*arg, **kwargs)
            except Exception:
                print(traceback.format_exc())
                logging.warning("Exception occured, retrying.")
                await asyncio.sleep(2.5)
                continue
    return wrapper


async def socket_download(session, url) -> bytes:
    """download items from the given url
    url ==> downloaded bytes from the url"""
    async with session.get(url) as resp:
        logging.warn("downloading " + url)
        return await resp.read()


async def save_nar_to_disk(narinfo, session):
    filename = narinfo.decode("utf-8").split("\n")[1].split("nar/")[-1]
    uri = os.path.abspath(
        f"{__file__}/../../../userdata/nar/{filename}"
    )
    src = await socket_download(
        session, f"https://cache.nixos.org/nar/{filename}"
    )
    async with aiofiles.open(uri, mode="w+b") as files:
        await files.write(src)


async def read_nar_from_disk(filename):
    """read files from dir"""
    uri = os.path.abspath(
        f"{__file__}/../../../userdata/nar/{filename}"
    )
    async with aiofiles.open(uri, mode="rb") as file:
        return await file.read()


async def get_lastest_packages(channel: str) -> list:
    """Channel ==> list of nix storepaths"""
    channel_url = f"https://channels.nixos.org/{channel}/store-paths.xz"
    async with aiohttp.ClientSession() as session:
        raw_storepath = await socket_download(session, channel_url)
    try:
        with LZMAFile(BytesIO(raw_storepath)) as fid:
            return list(map(lambda line: line[11:43].decode("utf-8"), fid))
    except Exception:
        logging.warn("Channel not available!")
        return []


async def get_nixcache_narinfo(storepaths: list) -> dict:
    """
    list of storepath ==> dict of {storepath: narinfo in bytes, ...}"""
    _tasks = []
    async with aiohttp.ClientSession() as session:
        for each in storepaths:
            url = f"https://cache.nixos.org/{each}.narinfo"
            _tasks.append(asyncio.ensure_future(
                socket_download(session=session, url=url)))
        return dict(zip(storepaths, await asyncio.gather(*_tasks)))


async def get_nix_binary(storepaths: list):
    """storepaths ==> nar/{files}"""
    _tasks = []
    async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=900)) as session:
        temp_storepaths = await get_nixcache_narinfo(storepaths)
        for key_storepath, value_narinfo in temp_storepaths.items():
            _tasks.append(asyncio.ensure_future(
                save_nar_to_disk(value_narinfo, session)
            ))
            _tasks.append(asyncio.ensure_future(
                database.save_narinfo(key_storepath, value_narinfo)
            ))
        await asyncio.gather(*_tasks)
    return True


async def check_upstrean_exist(storepath: str):
    try:
        url = f"https://cache.nixos.org/{storepath}.narinfo"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return resp.status == 200
    except Exception:
        return False


async def user_requested(storepath: str):
    if await check_upstrean_exist(storepath):
        await get_nix_binary([storepath])
        return True
    return False
