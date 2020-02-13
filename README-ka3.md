# KA³-chapterize CLI

CLI für dei Kapitelerstellung bei mpeg7-transkribierten Audiodaten.

## Requirements

- python3
- python3-pip (python package manager)

## Install

Clone Repository and switch to ka3-cli branch:

    git clone https://github.com/stereolith/podcast-chapterize.git && cd podcast-chapterize && git checkout ka3-cli

Install python dependencies:

    pip3 install -r requirements-ka3.txt

## Usage

KA³ chapterize CLI usage:

    python3 ka3_chapterize.py [-h] transcript ouptut

- `-h` prints help
- `transcript` path to mpeg7 transcript file
- `output`  path to put output file(s)

## Ouptut

- plain text file with chapter start times and chapter titles