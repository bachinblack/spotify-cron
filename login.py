#!/usr/bin/env python3
"""Uses OAuth to retrieve an access_token for the required account."""

import webbrowser
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import base64
import requests

REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "user-modify-playback-state"

# Spotify API endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"


with open("client_creds.json", "r", encoding="ASCII") as f:
    client_creds = json.load(f)

CLIENT_ID = client_creds["id"]
CLIENT_SECRET = client_creds["secret"]
AUTH_URL = f"{SPOTIFY_AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}"

# Open the authorization URL in the default web browser
webbrowser.open(AUTH_URL)


# Create a local server to handle the redirect
class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        query_params = parse_qs(query)
        if "code" in query_params:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"Authorization successful. You can close this window now."
            )
            self.server.auth_code = query_params["code"][0]
            self.server.done = True
        else:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"Authorization failed.")
        self.server.done = True


class AuthHttpServer(HTTPServer):
    done = False
    auth_code = None


with AuthHttpServer(("localhost", 8888), CallbackHandler) as server:
    while not server.done:
        server.handle_request()


def get_access_token(auth_code):
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
    return response.json().get("access_token")


access_token = get_access_token(server.auth_code)

with open("creds.json", "w", encoding="ASCII") as f:
    json.dump({"access_token": access_token}, f)
