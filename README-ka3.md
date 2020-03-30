# KA³-chapterize CLI

CLI für dei Kapitelerstellung bei mpeg7-transkribierten Audiodaten. Optional: Schreiben von Kapitelmarken in m4a-Dateien.

## Requirements

- Python 3.7
- Java
- pip (python package manager)

## Install

Clone Repository and switch to ka3-cli branch:

    git clone https://github.com/stereolith/podcast-chapterize.git && cd podcast-chapterize && git checkout ka3-cli

Install python dependencies:

    pip3 install -r requirements-ka3.txt

## Usage

KA³ chapterize CLI usage:

    python3 ka3_chapterize.py [-h] [-a AUDIO] transcript ouptut

- `-h` prints help
- `-a AUDIO` path to audio file to add chapter markers to (any codec/ format that ffmpeg can process is permitted)
- `transcript` path to mpeg7 transcript file
- `output`  path to save output file(s) to

## Ouptut Files

- plain text file with chapter start times and chapter titles
- _if audio file is given:_ m4a audio file with chapter markers