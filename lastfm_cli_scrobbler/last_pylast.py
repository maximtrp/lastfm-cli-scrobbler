#!/usr/bin/python
"""Last.fm CLI scrobbler implementation based on pylast"""

from glob import glob
from os.path import exists, isdir, expanduser
from time import time
from optparse import OptionParser
from getpass import getpass
from yaml import safe_load as yaml_load, dump as yaml_dump
from mutagen import File as MutagenFile
from pylast import LastFMNetwork, md5


def main():
    """CLI entrypoint function"""

    # Parsing command-line arguments
    parser = OptionParser(usage="Usage: %prog [FILES]")
    _, args = parser.parse_args()

    # Checking credentials and loading data if exists
    credentials_fn = expanduser('~/.lastfm_scrobbler')

    if exists(credentials_fn):
        with open(credentials_fn, encoding='utf8') as file:
            creds = yaml_load(file) or {}
    else:
        creds = {}

    creds_ready = set([
        'username', 'secret', 'api_key', 'session_key'
    ]).issubset(creds)

    if not creds_ready:
        print('[x] Auth keys not found')
        print(
            '[!] Please create an API account:',
            'https://www.last.fm/api/account/create'
        )
        username = input('[?] Enter your username: ')
        password = getpass('[?] Enter your password: ')
        api_key = getpass('[?] Enter your API key: ')
        secret = getpass('[?] Enter your API secret: ')
        password_hash = md5(password)
        session_key = None
    else:
        username = creds['username']
        session_key = creds['session_key']
        api_key = creds['api_key']
        secret = creds['secret']
        password_hash = None

    try:
        network = LastFMNetwork(
            api_key=api_key, api_secret=secret,
            username=username, session_key=session_key,
            password_hash=password_hash
        )

    except Exception as exc:
        print('[x] Auth unsuccessful:', str(exc))
        exit(1)

    creds['api_key'] = api_key
    creds['secret'] = secret
    creds['session_key'] = network.session_key
    creds['username'] = username

    with open(credentials_fn, 'wt', encoding='utf8') as file:
        yaml_dump(creds, file)

    print('[✔] Auth successful')

    items = args if args else glob('*')
    files = filter(lambda x: not isdir(x), items)
    tracks = []
    cum_length = 0
    timestamp_now = int(time())

    for file in files:
        filetype = MutagenFile(file, easy=True)
        if not filetype:
            continue

        artist = filetype.get('artist', [None])[0]
        album_artist = filetype.get('albumartist', [None])[0]
        title = filetype.get('title', [None])[0]
        album = filetype.get('album', [None])[0]

        if not artist or not title:
            print('[x] Skipping file:', file)
            continue

        duration = int(filetype.info.length)
        cum_length += duration
        timestamp = str(timestamp_now - cum_length)
        tracks.append({
            'artist': artist,
            'album_artist': album_artist,
            'title': title,
            'album': album,
            'duration': duration,
            'timestamp': timestamp
        })

    try:
        network.scrobble_many(tracks)
        print('[✔] Scrobbling successful')
    except Exception as exc:
        print('[x] Scrobbling unsuccessful:', str(exc))


if __name__ == '__main__':
    main()
