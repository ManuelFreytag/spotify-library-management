# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 11:24:27 2017

@author: manuf
"""

import spotipy
from spotipy import util
from spotipy import oauth2
import pandas as pd
import csv

def getData(credentials, username, saved = True, deselect = []):
    """
    Get data for all songs at least in one playlist of the user
    
    saved:  If saved is True, return data for all saved tracks, otherwise data from all tracks in a playlist
    """
    #ANNOATIONS:
    #1) RETURN FORMAT
    #   Spotify returns all results in the json format.
    #   However, spotipy already casts the return into a dictionary -> very convenient.
    #
    #2) NUMBER OF REQUESTS TO SERVER
    #   Spotify limits the number of requests to the server for each client
    #   Therefore, this app bundles requests in a bin with size 50 (max)
    
    #get permission for indepth information
    client_credentials_manager = oauth2.SpotifyClientCredentials(**credentials)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    sp.trace = False


    #get user token
    if(saved == True):
        scope = 'user-library-read'
    else:
        scope = " "
        
    token = util.prompt_for_user_token(username, scope, **credentials, redirect_uri = "http://127.0.0.1/callback")
    
    if token:
        spu = spotipy.Spotify(auth=token)
        spu.trace = False
    else:
        raise Warning("Can't get access token for", username)
    
        
    if(saved == True):
        tURIS = getTrackInfo(sp, spu)
    else:
        pURIS = getUrisPlaylists2(spu, deselect)
        tURIS = getTrackInfo(sp, spu, pURIS)
    
    genreDF = getArtistGenre(sp, tURIS)    
    trackFeaturesDF = getTrackMetaData(sp, tURIS)
    
    #join data together
    data = pd.DataFrame(tURIS)
    data = data.set_index("tid")
    data = pd.concat([data,genreDF,trackFeaturesDF], axis = 1)
    
    return data

#def getUrisPlaylists(credentials, username, deselect):
#    """
#    Helper function to gather all playlistURIS
#    ___________________________________________________________________________
#    credentials:    Valid credentials to allow access to the spotify api
#    username:       List containing the track URIS and artist URIS in dictionary form
#    deselect:       List of names for playlists that should not be selected
#    ___________________________________________________________________________
#    """
#    
#    token = util.prompt_for_user_token(username, " ", **credentials, redirect_uri = "http://127.0.0.1/callback")
#    uris = []
#    
#    if token:
#        spu = spotipy.Spotify(auth=token)
#        spu.trace = False
#
#        results = spu.current_user_playlists(limit=50)
#        #select all uris except for the explicitly deselected
#        uris = [x["uri"] for x in results["items"] if deselect.count(x["name"]) == 0]
#    else:
#        raise Warning("Can't get access token for", username)
#        
#    return uris

def getUrisPlaylists2(spu, deselect):
    """
    Helper function to gather all playlistURIS
    ___________________________________________________________________________
    credentials:    Valid credentials to allow access to the spotify api
    username:       List containing the track URIS and artist URIS in dictionary form
    deselect:       List of names for playlists that should not be selected
    ___________________________________________________________________________
    """
    
    results = spu.current_user_playlists(limit=50)
    uris = []
    uris = [x["uri"] for x in results["items"] if deselect.count(x["name"]) == 0]

    return uris
    


def getTrackInfo(sp, spu, uris = None):
    """
    Helper function to gather all track IDS, artist IDs, track titles and artist names
    ___________________________________________________________________________
    sp:     spotify object with valid credentials
    uris:   List of playlist URIS to get the songs of (if None get saved tracks)
    _________________________________________________________________________
    """
    
    if(uris is None):
        result = [spu.current_user_saved_tracks(limit = 50)]
        while(True):
            #limit is 50, therefore we select the maximum to minimize the number of requests
            ret = spu.current_user_saved_tracks(limit = 50, offset = 50*len(result))
            if(len(ret["items"]) > 0):
                result += [ret]
            else:
                break


    else:
        #Get the playlist information
        result = []
        for i, uri in enumerate(uris):
            username = uri.split(":")[2]
            playlist_id = uri.split(':')[4]
            results = sp.user_playlist(username, playlist_id)
            result.append(results["tracks"])
            

    tids, URIS = [],[]

    #check if unique entry, if not then don't add
    for results in result:
        for x in results["items"]:  
            if x["track"]["uri"] not in tids and ((x["track"]["uri"].split(":")[1] != "local")): #if its a local track do not use it
                #GET ADDED AT DATE
                addDate = x["added_at"]
                #GET TRACK ID
                tid = x["track"]["uri"]
                #GET TRACK NAME
                tname = x["track"]["name"]
                #GET ARTIST URI
                aid = x["track"]["artists"][0]["uri"]
                #GET ARTIST NAME
                aname = x["track"]["artists"][0]["name"]
            
                URIS.append({"addDate": addDate,
                             "tid" : tid,
                             "tname" : tname,
                             "aid" : aid,
                             "aname" : aname})
                #add for future tracking
                tids.append(tid)
            else:
                continue
    return URIS
    
def getArtistGenre(sp, URIS):
    """
    Helper function to retreive a list of genres associated with each track / artist
    
    ___________________________________________________________________________
    sp:         Spotify object with valid credential authentification
    URIS:       List containing the track URIS and artist URIS in dictionary form
    ___________________________________________________________________________
    """
    
    #GET ARTIST GENRES (in 50 packages)
    aids = [x["aid"] for x in URIS]
    rest = len(aids)
    genres = []
    i = 0
    
    while(rest > 0):
        if rest > 50:
            artists = sp.artists(aids[(i*50):((i+1)*50)])
            genres.extend([x["genres"] for x in artists["artists"]])
            rest -= 50
            i += 1
        else:
            artists = sp.artists(aids[(i*50):(i*50+rest)])
            genres.extend([x["genres"] for x in artists["artists"]])
            rest -= 50
            
    data = splitArtistGenres(genres, URIS)
    
    return data

def splitArtistGenres(genres, URIS):
    """
    Helper function to create a dataframe containing duplicate free columns for each
    and indicating in boolean whether the track is associated with the respective genres
    
    ___________________________________________________________________________
    genres:     List of lists containing all genres associated with a song
    URIS:       List containing the tack URIS and artist URIS in dictionary form
    ___________________________________________________________________________
    
    """
    #get list of track ids
    tids = [x["tid"] for x in URIS]
    
    #get duplicate free list of genres
    genre_list = []
    [genre_list.extend(x) for x in genres]
    genre_list = list(set(genre_list))
    genre_list.sort()
    
    #create dataframe
    data = pd.DataFrame(data = [[0]*len(genre_list)]*len(URIS), 
                                columns = genre_list, 
                                index = [x["tid"] for x in URIS])
    
    #fill the dataframe based on the genres
    for i, x in enumerate(genres):
        for genre in x:
            data.loc[tids[i],genre] = 1
    
    return data

def getTrackMetaData(sp, URIS):
    """
    Helper function to retreive all meta data of the track ids
    ___________________________________________________________________________
    sp:         Spotify object with valid credentials
    URIS:       List containing the tack URIS and artist URIS in dictionary form
    ___________________________________________________________________________
    """
    tids = [x["tid"] for x in URIS]
    
    rest = len(tids)
    metaAttributes = []
    i = 0
    
    while(rest > 0):
        if rest > 50:
            features = sp.audio_features(tids[(i*50):((i+1)*50)])
        else:
            features = sp.audio_features(tids[(i*50):(i*50+rest)])
              
        metaAttributes.extend(features)
        rest -= 50
        i += 1 
        
    data = decomposeMetData(metaAttributes)    
    
    return data

def decomposeMetData(metaAttributes):
    values = []
    
    for x in metaAttributes:
        n_values = [values for key, values in x.items()]
        values.append(n_values)
    
    data = pd.DataFrame(data = values, 
                 columns = list(metaAttributes[0].keys()), 
                 index = [x["uri"] for x in metaAttributes])

    #remove unnecessary attributes
    unnAttr = ["type","id","track_href","analysis_url", "uri"]
    
    for i in unnAttr:
        del data[i]
        
    return data

#TESTING
if __name__ == "__main__":
    with open("Data/CREDENTIALS.csv","r") as csvfile: 
        imp = csv.reader(csvfile, delimiter = ";")
        
        credentials = {}
        for rows in imp:
            credentials[rows[0]] = rows[1]
    
    print(credentials)
    deselect = ["Hörbücher"]
    username = "manu.freytag@web.de"
    
    results = getUrisPlaylists(credentials, username, deselect)
    
#TODO    
#Get advanced feature analysis
#sp.audio_analysis(tids)
#Create features based on the audio_analysis