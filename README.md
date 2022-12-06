# Nirror
Nirror allows everyone to setup a cache.nixos.org mirror easily, without the use the `nix-copy` or any parts of the nix package manager.

Unlike any other "nix caching projects", Nirror help to you to setup a **FULL MIRROR** instead of a "Reverse Proxy with Caching" like NGINX.

It is easy to use as well, hosts simply run `webserver.py`..... and voila, a fully working nixos binary cache mirror is born.
## Requirements
- Python 3.8 with pip
- Linux or Unix-like Systems (Optional, Uvicorn)

## Deployment

### via Anaconda

#### Setup
Create Python3.8 environment
> (base) \$ conda create -n "nixcache" python=3.8

Activate environment
> (base) \$ conda activate nix_cache

Install requirements
> (nix_cache) \$ pip install -r requirements.txt

#### Config and Run
Edit `config.json` if you need to change the port, channel or the refresh interval.

Start Server
> (nix_cache) \$ python3.8 nirror/webserver.py

## Bugs / Feature Requests
See Issues.