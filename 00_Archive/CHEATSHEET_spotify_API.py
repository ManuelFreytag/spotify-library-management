# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 17:14:57 2017

@author: Manuel
"""

#Request

#1) Get general information about songs
client_credentials_manager = SpotifyClientCredentials(**credentials)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#2) Get account infomration based information -> need for a token
token = util.prompt_for_user_token(username, scope, **credentials)
if token:
    sp = spotipy.Spotify(auth=token)

