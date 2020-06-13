# Last.fm CLI Scrobbler

This is a simple Last.fm command-line scrobbler written in Python.

## Installation

```bash
$ pip install git+https://github.com/maximtrp/lastfm-cli-scrobbler.git
```

Or you may clone this repo and install it using:

```bash
$ pip install .
```

## Usage 

After the installation, two commands will be available: `scrobble` (my own API implementation) and `scrobble2` (`pylast` API implementation).

```bash
$ scrobble -h
Usage: scrobble [FILES]

Options:
  -h, --help  show this help message and exit
```

Pylast-based version is probably more stable, but my own implementation of Last.fm API returns the full log (and shows a cross instead of a check if a track was ignored):

```bash
$ scrobble {01..04}*.flac
Scrobbling report:
[✔] Shuttle358 - Ash
[✔] Shuttle358 - Chessa
[✔] Shuttle358 - Blast
[✔] Shuttle358 - Duh
```
