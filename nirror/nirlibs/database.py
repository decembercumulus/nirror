"""database operations"""

# Copyright 2022 decembercumulus (I. Tam) <tamik@duck.com>
#
# This file is part of Nirror.
#
# Nirror is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version
#
# Nirror is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details
#
# You should have received a copy of the GNU General Public License along
# with Nirror. If not, see <https://www.gnu.org/licenses/>.

import os
import time

import aiosqlite


sqlite_path = os.path.abspath(f"{__file__}/../../../userdata/storage.db")
nar_dir = os.path.abspath(f"{__file__}/../../../userdata/nar/")


def nar_path(nar_filename):
    os.path.abspath(
        f"{__file__}/../../../userdata/nar/{nar_filename}")


def ignore(func_name):
    """Ignore the error"""
    # pylint: disable=broad-except
    async def wrapper(*arg, **kwargs):
        try:
            return await func_name(*arg, **kwargs)
        except Exception as error:
            print(error)
            return None
    return wrapper


def retry_oper_err(func_name):
    """Retry until success"""
    async def wrapper(*arg, **kwargs):
        while True:
            try:
                return await func_name(*arg, **kwargs)
            except aiosqlite.OperationalError:
                continue
    return wrapper


@retry_oper_err
async def create_db():
    async with aiosqlite.connect(sqlite_path) as conn:
        await conn.execute(
            "CREATE TABLE IF NOT EXISTS narinfo("
            "storepath TEXT NOT NULL UNIQUE,"
            "narinfo BLOB NOT NULL,"
            "used INTEGER NOT NULL)"
        )


@retry_oper_err
async def save_narinfo(storepath, narinfo):
    """download.get_nixcache_narinfo(channels)
    ==> SQLite"""
    async with aiosqlite.connect(sqlite_path) as conn:
        await conn.execute(
            sql="INSERT OR REPLACE INTO "
                "narinfo(storepath, narinfo, used)"
                "VALUES(?,?,?)",
            parameters=(storepath, narinfo, time.time())
        )
        await conn.commit()
    return True


@retry_oper_err
async def update_access_date(storepath: str):
    """update timestamp of storepath used"""
    async with aiosqlite.connect(sqlite_path) as conn:
        await conn.execute(
            sql="UPDATE narinfo SET used = ? WHERE storepath = ?",
            parameters=(time.time(), storepath)
        )
        await conn.commit()
        return True


@retry_oper_err
async def read_narinfo(storepath: str):
    """return narinfo from given storepath"""
    async with aiosqlite.connect(sqlite_path) as conn:
        await update_access_date(storepath)
        async with conn.execute(
            sql="SELECT narinfo FROM narinfo WHERE storepath = ?",
                parameters=(storepath,)) as raw_result:
            res = await raw_result.fetchone()
    try:
        filepath = \
            nar_path(res[0].decode("utf-8").split("\n")[1].split("nar/")[-1])
        if os.path.exists(filepath):
            return res[0]
        else:
            os.remove(filepath)
            return None
    except TypeError:
        return None


def rm(path2rm):
    if os.path.exists(path2rm):
        os.remove(path2rm)
        return True
    return False


@ignore
async def dump_old(days: int):
    """remove old nars after x days"""
    async with aiosqlite.connect(sqlite_path) as conn:
        async with conn.execute(
            sql="SELECT narinfo FROM narinfo WHERE used < ?",
                parameters=(time.time() - 86400 * days,)) as tuple_list:
            temp_res = await tuple_list.fetchall()
        for tupled_narinfo in temp_res:
            rm(nar_path(
                tupled_narinfo[0].
                decode("utf-8").split("\n")[1].split("nar/")[-1]))
            await conn.execute(
                sql="DELETE FROM narinfo WHERE narinfo = ?",
                parameters=tupled_narinfo
            )
            await conn.commit()
    return True


async def storepaths_in_db():
    async with aiosqlite.connect(sqlite_path) as conn:
        async with conn.execute(
                sql="SELECT storepath FROM narinfo") as q_res:
            return list(map(
                lambda x: x[0],
                await q_res.fetchall()
            ))
