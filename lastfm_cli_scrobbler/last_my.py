#!/usr/bin/python
"""Last.fm CLI scrobbler implementation"""

from os.path import exists, isdir, expanduser
from glob import glob
from getpass import getpass
from time import time
from hashlib import md5
from optparse import OptionParser
from yaml import safe_load as yaml_load, dump as yaml_dump
from requests import post
from mutagen import File as MutagenFile


def make_string(lst, prefix):
    """Signature strings and url paramaters dicts"""
    lst_len = len(lst)
    prefixed_lst = sorted(list(zip(
        [f'{prefix}[{i}]' for i in range(lst_len)],
        lst
    )))
    prefixed_lst_filtered = list(filter(lambda x: x[1], prefixed_lst))
    prefixed_dict = dict(prefixed_lst_filtered)
    return (
        "".join(map("".join, prefixed_lst_filtered)),
        prefixed_dict
    )


def main():
    """CLI entrypoint function"""

    # Parsing command-line arguments
    parser = OptionParser(usage="Usage: %prog [FILES]")
    _, args = parser.parse_args()

    # Checking credentials and loading data if exists
    credentials_fn = expanduser('~/.lastfm_scrobbler')
    logged_in = False

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
        while not logged_in:
            username = input('[?] Enter your username: ')
            password = getpass('[?] Enter your password: ')
            print(
                '[!] Please create an API account: '
                'https://www.last.fm/api/account/create')
            api_key = getpass('[?] Enter your API key: ')
            secret = getpass('[?] Enter your API secret: ')

            api_sig = md5(bytes(
                f'api_key{api_key}'
                f'methodauth.getmobilesessionpassword{password}'
                f'username{username}{secret}', encoding='utf8')
            ).hexdigest()
            session_url = 'https://ws.audioscrobbler.com/2.0/'
            params = {
                'method': 'auth.getmobilesession', 'format': 'json',
                'api_key': api_key, 'api_sig': api_sig, 'password': password,
                'username': username
            }
            response = post(session_url, data=params, timeout=30).json()

            if 'error' in response:
                print('[x] Error:', response['message'])
                print('[!] Making another attempt...')
            else:
                logged_in = True
                session_key = response['session']['key']
                creds['api_key'] = api_key
                creds['secret'] = secret
                creds['session_key'] = session_key
                with open(credentials_fn, 'wt', encoding='utf8') as file:
                    yaml_dump(creds, file)
                print('[v] Session key was obtained successfully\n')

    items = args if args else glob('*')
    files = filter(lambda x: not isdir(x), items)
    tracks_info = {}
    cum_length = 0
    timestamp_now = int(time())

    for file in files:
        filetype = MutagenFile(file, easy=True)
        if not filetype:
            continue

        artist, albumartist, track, album = filetype.get('artist', [None])[0],\
            filetype.get('albumartist', [None])[0],\
            filetype.get('title', [None])[0],\
            filetype.get('album', [None])[0]
        length = int(filetype.info.length)
        cum_length += length
        timestamp = str(timestamp_now - cum_length)
        tracks_info.update({
            timestamp: {
                'file': file, 'album': album, 'track': track,
                'artist': artist, 'albumartist': albumartist
            }
        })

    # Preparing tracks info for scrobbling
    tracks = []
    artists = []
    albums = []
    albumartists = []
    timestamps = []

    for timestamp, track_info in tracks_info.items():
        track = track_info['track']
        artist = track_info['artist']
        albumartist = track_info['albumartist']
        album = track_info['album']

        if not artist or not track:
            print('Skipping file:', track_info['file'])
            continue
        if not albumartist:
            albumartist = artist

        tracks.append(track)
        artists.append(artist)
        albumartists.append(albumartist)
        albums.append(album)
        timestamps.append(timestamp)

    artists_sig, artists_url = make_string(artists, 'artist')
    tracks_sig, tracks_url = make_string(tracks, 'track')
    albums_sig, albums_url = make_string(albums, 'album')
    albumartists_sig, albumartists_url = make_string(
        albumartists, 'albumartist')
    timestamps_sig, timestamps_url = make_string(timestamps, 'timestamp')

    api_sig = md5(bytes(''.join([
        albums_sig, albumartists_sig, "api_key", creds[
            'api_key'], artists_sig, "methodtrack.scrobblesk", creds['session_key'],
        timestamps_sig, tracks_sig, creds['secret']]), encoding='utf8')
    ).hexdigest()

    # Parameters init and scrobbling
    params = {
        'api_key': creds['api_key'], 'api_sig': api_sig, 'sk': creds['session_key'],
        'method': 'track.scrobble', 'format': 'json'
    }
    params.update(albums_url)
    params.update(artists_url)
    params.update(albumartists_url)
    params.update(timestamps_url)
    params.update(tracks_url)

    response = post('https://ws.audioscrobbler.com/2.0/',
                    data=params, timeout=30)
    result = response.json()

    if 'scrobbles' in result:
        print('Scrobbling report:')
        scrobbles = result['scrobbles']['scrobble']
        if not isinstance(scrobbles, list):
            scrobbles = [scrobbles]

        for scrobble in scrobbles:
            track = tracks_info[str(scrobble['timestamp'])]
            status = 'x' if scrobble['ignoredMessage']['code'] == '1' else '✔'
            print(f'[{status}] {track["artist"]} - {track["track"]}')

    elif 'error' in result:
        print('Error:', result['message'])


if __name__ == '__main__':
    main()
