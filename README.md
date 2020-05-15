# podcast-chapterize 

This project aims to automatically provide longform audio podcast episodes with chapter markers. This is achieved with statistical natrual language processing algorithms that try to subdivide transcribed podcast episodes into topically cohesive parts.

[work in progress]

## Requirements
### CLI:
* Python 3.6+
* ffmpeg
* [MP4Box](https://gpac.wp.imt.fr/2015/07/29/gpac-build-mp4box-only-all-platforms/)
* matplotlib ([intall via package manager](https://matplotlib.org/3.1.1/users/installing.html#linux-using-your-package-manager))
* Java
* Python module requirements (installable via `pip3 install -r requirements.txt`)

### Web interface:
* node.js
* npm

## Usage
This program can be used in the command line or as an HTTP API with a web interface.

### CLI
Usage: `python3 main.py [subcommand] [options] ...`

* Help: `python3 main.py --help`
* Subcommand help: `python3 main.py [subcommand] --help`
* Possible subcommands:
    * `python3 main.py run`: Start chapterization process from podcast RSS feed URL
    * `python3 main.py transcribe`: Transcribe podcast episode from RSS feed URL
    * `python3 main.py chapterize`: Chapterize transcript

### Web interface

_API_:

* Create python3 venv: `python3 -m venv venv`
* Activate venv: `source venv/bin/activate`
* (optional) Set environment variables for IP address and Port in the ´.flaskenv´ file
* start API server with `flask run`

_Frontend_:

* Serve frontend files 'web/client/dist' on web server


__If the server is not running on the same machine:__

1. specify API host in web/client/.env
2. cd into 'web/client'
3. install dependencies with `npm install`
4. build files with `npm run build`
5. serve built files from (web/client/dist) on web server

