# Nirror
Nirror is an easy-to-use server designed to mirror cache.nixos.org without the use the `nix-copy` or any parts of the nix package manager.

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

Install deps
> (nix_cache) \$ pip install -r requirements.txt
#### Run
Edit `config.json` if you are not going to use port `8080` or unstable channel for nixpkgs.

Start Server
> (nix_cache) \$ python3.8 webserver.py

### via Docker
#### Build image
- !! DOCKER: Edit `config.json` if you are not going to mirror the unstable channel.!!

Build Docker Image
> docker build --tag nirror .

Tag version number to image
> \$ docker tag nirror:latest nirror:[anything_you_like]

Remove useless tags
> \$ docker rmi nirror:latest
#### Run image
> \$ docker run --publish [your-port]:8080 nirror

### Publish
- Setting up a reverse proxy in NGINX or Caddy.

## TBD / Technical Limitations
### User Petitions
- Cache nixpkgs if requested but not avaliable. This is not yet implemented.

### Error Fallback
- The handler for program exception is incomplete right now.
- For server hosts, return 301 to `cache.nixos.org` whenever HTTP 4xx or 5xx happens.
- For users, use the mirror as `nix.settings.substituters`(Nix 22.05 or later).

### Tests
- Haven't written yet lol, please open a pull request to help me.

### SQLite (NAR.XZ file size limit)
- The maximum size to store a blob object in SQLite3 is 1.5 Gigabytes only. FILENAME.nar.xz will not be stored if it is too large.

## Licence
Copyright 2022 I. Tam (Ka-yiu Tam) <tamik@duck.com>
