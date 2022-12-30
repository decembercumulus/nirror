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

import asyncio

import uvicorn
from blacksheep import Application, file, not_found
from nirlibs import nir_server, database, download

app = Application()


@app.route("/")
async def route_index():
    return await nir_server.unfortune()


@app.route("/nix-cache-info")
async def route_priority():
    return file(
        value=await nir_server.server_info(),
        content_type="text/x-nix-cache-info"
    )


@app.route("/nar/<filename>")
async def route_narbin(filename):
    try:
        return file(
            value=await download.read_nar_from_disk(filename),
            content_type="application/x-nix-nar"
        )
    except Exception:
        not_found()


@app.route("/<storepath>.narinfo")
async def route_narinfo(storepath):
    exp_res = await database.read_narinfo(storepath)
    if exp_res:
        return file(value=exp_res,
                    content_type="text/x-nix-narinfo")
    else:
        asyncio.get_event_loop().create_task(
            download.user_requested(storepath))
    not_found()


async def configure_background_tasks(app):
    asyncio.get_event_loop().create_task(
        nir_server.server_loop())

if __name__ == '__main__':

    app.on_start += configure_background_tasks
    uvicorn.run(
        app=f"{__name__}:app",
        host="0.0.0.0",
        port=nir_server.localhost_port())
