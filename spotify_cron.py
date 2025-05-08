#!/usr/bin/env python3
"""Starts and stops spotify playback."""

import json
import argparse
import requests

# Spotify API endpoints
SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

PLAYLISTS = {
    "motivation": "bHKpcAmWTyWmYMgC4fUncQ",
    "anime": "vhnLQn1DSQu7WMYhGwGb3A",
    "lofi": "hHrhTpKBQEWRjpAgyrDd6A",
    "Rétro": "k1LZKFBVQ7qVC9kg2EvT-g",
    "pop": "wzhmBK9UQEWw75DsMJiguQ",
    "classique": "mk1XVMHUTySjVIP06K9p_w",
    "métal": "wZsTLEEoRdGNuxu0G824mw",
}


def start_playlist(access_token, playlist_uri):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # TODO Check if it's necessary.
    # res = requests.put(
    #     "https://api.spotify.com/v1/me/player/shuffle?state=true",
    #     headers=headers,
    #     timeout=10,
    # )

    data = {"context_uri": playlist_uri}
    res = requests.put(
        f"{SPOTIFY_API_BASE_URL}/me/player/play",
        headers=headers,
        data=json.dumps(data),
        timeout=10,
    )
    if res.status_code == 200:
        print("Playlist started.")
    else:
        print(f"Play action failed with status {res.status_code} : {res.content}")
        exit(1)


def stop_playback(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    res = requests.put(
        f"{SPOTIFY_API_BASE_URL}/me/player/pause", headers=headers, timeout=10
    )
    if res.status_code == 200:
        print("Playback stopped.")
    else:
        print(f"Failed to stop playback. status {res.status_code} : {res.content}")
        exit(1)


with open("creds.json", "r", encoding="ASCII") as f:
    creds = json.load(f)


def execute_action(args: argparse.Namespace):
    match args.action:
        case "play":
            if args.playlist is None:
                print("[playlist] is required with action=play.")
                exit(1)
            if args.playlist not in PLAYLISTS:
                print(f"Playlist {args.playlist} does not exist.")
                exit(2)
            playlist_uri = "spotify:playlist:" + PLAYLISTS[args.playlist]
            start_playlist(creds["access_token"], playlist_uri)
        case "stop":
            stop_playback(creds["access_token"])
            # Stop
        case _:
            print("Invalid argument")
            exit(1)


parser = argparse.ArgumentParser(
    prog="spotify cron", description="Starts playlists and stops spotify"
)
parser.add_argument("action")
parser.add_argument("playlist", default=None, nargs="?")

execute_action(parser.parse_args())
