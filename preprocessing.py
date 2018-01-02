# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:07:14 2017

@author: Manuel
"""

import dataImport
import pandas as pa

def preprocessing(data, specificity = 1):
    """
    - This function is primarily is used to decrease the genre specificity with minimizing
      the loss of information by generalization.
    
    - We are mapping every known genre based on https://en.wikipedia.org/wiki/List_of_popular_music_genres
    
    - As spotify is using multiple niche genres that complicate a mapping to a super-genre
    - Therefore, this function tries to recognise similar genres trying to find word-similarities
    
    ___________________________________________________________________________
    Input:
        
    data:           Starting data in form of a pandas DataFrame
    
    specificity:    The degree to which genres should be distinguished.
                    Degrees can vary between 0 and 4.
                    This value depends on the playlist content
                    A high degree can lead to overfitting!
                    Standard value is 1.
    ___________________________________________________________________________
          
    """
    
    
    #only import text files if the application is newly restarted -> data not in cache
    #TODO: Remove the country adjective part
    try:
        dtype = "Pandas.core.frame.DataFrame"
        if(set([type(genres), type(country_adjectives)]) == dtype):
            pass
    except NameError:
        genres = pa.read_csv("Data/genres.csv", sep = ";")
        counrtry_adjectives = pa.read_csv("Data/country_adjective.csv")
          
        
        
    #get copy of all data
    tmp_data = data.copy()
        
    #REMOVE ALL NOT GENRE ATTRIBUTES (Save seperately)
    data_ngenre = tmp_data.loc[:,"time_signature":].copy()
    tmp_data = tmp_data.drop(data_ngenre.columns, axis = 1)
        
    #Generate the initial data
    genre_ub = list(genres[str(specificity)].values)
    genre_comp = list(set(genre_ub)) #list of unique genre names in the comprised version
    init_data = [[0]*len(genre_comp)]*len(data.index)
    missing = list(data.columns) #all genres of spotify
    
    init_data, missing = adaptSpecificity(init_data, tmp_data, genres, specificity)
    
    changes = True
    
    while(missing != []  and changes == True):
        print(1)
        #PARSE ALL NAMES ACCORDINGLY
        all_genres = list(tmp_data.columns)
        all_genres.extend(list(genres["genre"].values))
        
        genre_parsing_dicc = reduceSpotifyGenreNaming(missing, all_genres)
        
        #reduce all columns of the dataframe that have already been allocated
        tmp_data = tmp_data.loc[:,missing].copy()
        
        #rename all other names according to the parsing dic
        tmp_data = tmp_data.rename(index=str, columns=genre_parsing_dicc)
        print(tmp_data.columns)
        
        #Repeate process
        init_data, missing2 = adaptSpecificity(init_data, tmp_data, genres, specificity)
        
        #check if we made progress, if not set changes to "false"
        if(len(missing) == len(missing2)):
            changes = False
        else:
            missing = missing2.copy()

        
    #ADD ALL NOT GENRE ATTRIBUTES
    data_genre = pa.DataFrame(init_data, columns = genre_comp)
    new_data = pa.concat([data_genre, data_ngenre], axis = 1)
    
    
    #Estimate specificity (number of songs, number of genres)
    #TODO:
    
    return new_data, missing

def reduceSpotifyGenreNaming(missing, all_genres):
    """
    This helper function is trying to parse knwon genres from unknown genres
    It follows the "long to short" principle.
    To reduce the risk of ambigiousy each genre is only allowed to inplace one other genre.
    """
    not_missing = all_genres.copy()
    [not_missing.remove(x) for x in missing]
    
    #get the length of all known genres
    not_missing = [(x, len(x)) for x in not_missing]

    #order not missing by descending
    not_missing.sort(key = lambda not_missing2:not_missing2[1], reverse = True)
    
    old_missing = missing.copy()
    new_missing = {}
    
    #try to parse to find the not missing genre inside of a missing. Start from long to short
    for x in not_missing:
        to_remove = []
        for y in old_missing:
            if(y.rfind(x[0]) != -1):
                #create dictionary entry to identify the "synonyme"
                #to prevent id problems, only one id is allowed to be parsed
                if(to_remove == []):
                    new_missing[y] = x[0]
                else:
                    new_missing[y] = y
                #remember to remove
                to_remove.append(y)

        #parse and remove if found
        [old_missing.remove(y) for y in to_remove]
        
    #add all remaining old_missing to the new_missing
    for x in old_missing:
        new_missing[x] = x
        
    return new_missing

#TODO: Parse not only based on known spotify genres but also on known overall genres

def adaptSpecificity(init_data, old_data, genres, specificity):
    #Check
    genre_spot = list(old_data.columns)
    genre_sub = list(genres["genre"].values)
    genre_ub = list(genres[str(specificity)].values)
    genre_comp = list(set(genre_ub)) #list of unique genre names in the comprised version
    
    data_values = [list(x) for x in old_data.values]
    missing_new = []
    
    tmp_data = init_data.copy()
    
    #fill the new data
    for i, row in enumerate(data_values):
        for j, x in enumerate(row):
            if(x == 1):
                try:
                    #get the reduced index that has to be incremented by 1
                    index = genre_comp.index(genre_ub[genre_sub.index(genre_spot[j])])
                    test = tmp_data[i].copy()
                    test[index] += 1
                    tmp_data[i] = test.copy()
                except ValueError:
                    missing_new.append(genre_spot[j])
    
    
    return tmp_data, set(missing_new)

def read_prep_data():
    return None

    
##import data
#genres
#country_adjectives

if __name__ == "__main__":
    data = pa.read_csv("data.csv", sep = ";")
#    data = preprocessing(data)
    
    
    try:
        dtype = "Pandas.core.frame.DataFrame"
        if(set([type(genres), type(country_adjectives)]) == dtype):
            pass
    except NameError:
        genres = pa.read_csv("Data/genres.csv", sep = ";")
        counrtry_adjectives = pa.read_csv("Data/country_adjective.csv")
        
    tmp_data, missing = preprocessing(data)
    print(data.values)
    print(sum(sum(tmp_data.loc[:,:"cajun"].values)))
    print(sum(sum(data.loc[:,"acid jazz":"zapstep"].values)))
    print(missing)
    tmp_data.to_csv("test.csv")
    
    #compare the sum of all genre attributes of old and new data
    #-> Loss by genre inconsistency
    

#get list of genres that have been unable to allocate
#Remove all country adjectives (one word behind it & word in country DB) and reiterate


#get list of genres that have been unable to allocate
#search for genres as sub-names from bottom up and reiterate

#if still genres left, return genre loss in % of songs*genres ("forced generalization)

#normalize values per song to get the degree of involvedness

#Remove songs that have not been able to allocate to at least one genre
# -> print out
#remove all columns with only 0s