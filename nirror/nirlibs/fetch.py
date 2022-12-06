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

"""Dumb HTTP GET library returns HTTP contents as vars given by passed uri"""
import logging
import lzma
from io import BytesIO


def return_none_if_error(func_name):
    """Wrap Errors to NoneType for Async Functions"""
    async def wrapper(*arg, **kwargs):
        try:
            return await func_name(*arg, **kwargs)
        except Exception as funcexp:
            logging.info(funcexp)
            return None
    return wrapper


async def store_paths(session, channel="nixpkgs-unstable") -> bytes:
    """Given nix channel, returns store-paths.xz for parsing in self_eval
    >>> store_paths(channel="nixpkgs-unstable")
    ['zpzsq1f1f1ijkbfl07cf59lzn61rdps2', ... ,'zzzdw12w3xa3qpfwayw2qgqxdzxybjy6']
    """
    logging.info("Downloading latest StorePaths.")
    async with session.get(f"https://channels.nixos.org/{channel}/store-paths.xz") as spresp:
        with lzma.LZMAFile(BytesIO(await spresp.read())) as fid:
            return list(map(lambda line: line[11:43].decode("utf-8"), fid))


async def narinfo(session, storepath) -> bytes:
    """Given StorePath, return narinfo from cache.nixos.org
    >>> narinfo("znkb90vjdg99k2sxki7gzh9qhy7k1sr6")
    (b'StorePath: /nix/store/znk ... URL: nar/ ... ',
    "15gwhakpd7kxb2xa0p24xqdz2h7x53m1w4yhm2hig7gsmpgvwhix.nar.xz")
    """
    async with session.get(f"https://cache.nixos.org/{storepath}.narinfo") as narresp:
        return (
            await narresp.read(),
            (await narresp.read()).decode("utf-8").split("\n")[1].split("nar/")[-1],
            (await narresp.read()).decode("utf-8").split("\n")[4].split("FileSize: ")[-1]
        )


async def narbin(session, filename_nar_xz) -> bytes:
    """Given sha256 file hash, return nar binary cache."""
    async with session.get(f"https://cache.nixos.org/nar/{filename_nar_xz}") as bresp:
        return await bresp.read()
