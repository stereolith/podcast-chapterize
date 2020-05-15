# KA³-chapterize CLI

CLI für die Kapitelerstellung bei mpeg7-transkribierten Audiodaten. Optional: Schreiben von Kapitelmarken in m4a-Dateien.

Das Tool hat einige dependencies und kann am besten über einen Docker Contianer genutzt werden, welcher alle notwenigen dependencies enthält. Alternativ ist auch eine manuelle Installation möglich.

## Docker Install (Recommended)

### Requirements

- [Docker](https://docs.docker.com/get-docker/) (optional: Docker Desktop)

__If using Docker Desktop:__ By Default, Docker Desktop allocates only 2GB of RAM to the Docker daemon. This needs to be increased to at least 7GB.

### Install (Linux and OSX)

1. Download bash script file [run_ka3_chapterize_docker.sh](run_ka3_chapterize_docker.sh): `curl https://raw.githubusercontent.com/stereolith/podcast-chapterize/ka3-cli/run_ka3_chapterize_docker.sh --output run_ka3_chapterize_docker.sh`
2. Make file executable: `chmod +x run_ka3_chapterize_docker.sh`

### Usage

    ./run_ka3_chapterize_docker.sh [-a AUDIO] transcript output

- `-a AUDIO` path to audio file to add chapter markers to (any codec/ format that ffmpeg can process is permitted)
- `transcript` path to mpeg7 transcript file
- `output`  path to save output file(s) to

## Mamual Install

### Requirements

- Python 3.7
- Java (min. Java SE 6.0)
- pip3 (python package manager)
- git
- build-essential (g++ and make)
- python3-dev

### Install

Clone Repository and switch to ka3-cli branch:

    git clone https://github.com/stereolith/podcast-chapterize.git && cd podcast-chapterize && git checkout ka3-cli

Install python dependencies:

    pip3 install -r requirements-ka3.txt

### Usage

KA³ chapterize CLI usage:

    python3 ka3_chapterize.py [-h] [-a AUDIO] transcript output

- `-h` prints help
- `-a AUDIO` path to audio file to add chapter markers to (any codec/ format that ffmpeg can process is permitted)
- `transcript` path to mpeg7 transcript file
- `output`  path to save output file(s) to

## Ouptut Files

- plain text file with chapter start times and chapter titles
- _if audio file is given:_ m4a audio file with chapter markers