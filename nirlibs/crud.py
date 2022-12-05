# Copyright 2022 I. Tam (Ka-yiu Tam) <tamik@duck.com>,
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
"""Library for reducing verbose code in performing dbms actions"""
import os
from logging import info as ggol
from time import time as epoch

import aiosqlite
from . import fetch

workingdir = os.path.abspath(f"{__file__}/../../storage.db")


async def initialise(db_dir=workingdir) -> None:
    """Initialise database if not exist in file directory"""
    async with aiosqlite.connect(db_dir) as dbcon:
        await dbcon.execute("CREATE TABLE IF NOT EXISTS nar("
            "storepath TEXT NOT NULL,"
            "narinfo BLOB NOT NULL,"
            "narname TEXT NOT NULL UNIQUE,"
            "contents BLOB NOT NULL,"
            "created INTEGER,"
            "accessed INTEGER)")
        await dbcon.execute("CREATE TABLE IF NOT EXISTS user_petition("
            "storepath TEXT NOT NULL,"
            "accessed INTEGER NOT NULL)")
        await dbcon.execute("CREATE TABLE IF NOT EXISTS deviants("
            "storepath TEXT NOT NULL,"
            "accessed INTEGER NOT NULL)")
        await dbcon.commit()
        ggol("Database Initialised.")


async def collect_petition(storepath, db_dir=workingdir):
    """Save user requests if cache is not store in database"""
    async with aiosqlite.connect(db_dir) as dbcon:
        await dbcon.execute(
            sql="INSERT OR IGNORE INTO "
                "user_petition(storepath, accessed) "
                "VALUES(?,?)",
            parameters=(storepath, epoch())
        )
        await dbcon.commit()


@fetch.return_none_if_error
async def count_petition(db_dir=workingdir):
    """
    Return a list most requested cache that is unpresent in local database
    """
    async with aiosqlite.connect(db_dir) as dbcon:
        with await dbcon.execute(
            sql="SELECT storepath, COUNT(accessed) "
                "FROM user_petition "
                "GROUP BY storepath") as dbcur:
            return await dbcur.fetchall()


async def if_cache_exists(storepath, db_dir=workingdir):
    """Return True if storepath exists"""
    async with aiosqlite.connect(db_dir) as dbcon:
        async with dbcon.execute(
            sql="SELECT 1 FROM nar WHERE storepath = ?",parameters=(storepath,)) as bcur:
            return (await bcur.fetchone()) is not None


async def update_cache_date(storepath, db_dir=workingdir):
    """Returns True if Cache is present local, and the creation date is updated"""
    if await if_cache_exists(storepath):
        async with aiosqlite.connect(db_dir) as dbcon:
            await dbcon.execute(
                sql="UPDATE nar SET created = ? where storepath = ?",
                parameters=(epoch(), storepath))
            ggol("StorePath %s in DB updated.", storepath)
            return True
    return False


async def download_cache(storepath, this_session, db_dir=workingdir):
    """Insert blob for nar.xzs"""
    if await update_cache_date(storepath):
        return None
    async with aiosqlite.connect(db_dir) as dbcon:
        cur_narinfo = (await fetch.narinfo(this_session, storepath))
        if int(cur_narinfo[-1]) > 1400000000:
            return None
        await dbcon.execute(
            sql="INSERT OR IGNORE INTO "
                "nar(storepath, narinfo, narname, contents, created) "
                "VALUES(?,?,?,?,?)",
            parameters=(
                storepath,
                cur_narinfo[0],
                cur_narinfo[-2],
                await fetch.narbin(this_session, cur_narinfo[-2]),
                epoch()
            ))
        await dbcon.commit()
    ggol("New StorePath %s downloaded.", storepath)


async def recycle_unused(days, db_dir=workingdir) -> None:
    """Recycle unused packages older than given days"""
    async with aiosqlite.connect(db_dir) as dbcon:
        await dbcon.execute(
            sql="DELETE FROM nar WHERE created < ? OR accessed < ?",
            parameters=(epoch() - 86400 * days, epoch() - 86400 * days))
        await dbcon.execute(
            sql="DELETE FROM user_petition WHERE accessed < ?",
            parameters=(epoch() - 86400 * days,))
        await dbcon.commit()
    ggol("Recycled unused cache for last %s day(s).", days)


@fetch.return_none_if_error
async def read_binary_cache(narname, db_dir=workingdir) -> bytes or None:
    """Given nar.xz fileman, return local stored cache"""
    async with aiosqlite.connect(db_dir) as dbcon:
        async with dbcon.execute(
            sql="SELECT contents FROM nar WHERE narname = ?",
            parameters=(narname,)) as bcur:
            return (await bcur.fetchone())[0]


@fetch.return_none_if_error
async def read_narinfo(store_path, db_dir=workingdir) -> bytes or None:
    """Given StorePath fil, return narinfo"""
    async with aiosqlite.connect(db_dir) as dbcon:
        async with dbcon.execute(
            sql="SELECT narinfo FROM nar where storepath = ?",
            parameters=(store_path,)) as ncur:
            return (await ncur.fetchone())[0]
