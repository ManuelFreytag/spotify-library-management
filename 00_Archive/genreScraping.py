# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 17:26:48 2017

@author: Manuel
"""
import os
import pandas as pa
rootdir = 'C:/Users/Manuel/OneDrive/Project_Datascience/Python/04_Projects/Spotify_API/Archive/Genres'
expdir = 'C:/Users/Manuel/OneDrive/Project_Datascience/Python/04_Projects/Spotify_API/Archive/GenresPrep'

paths = []
for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        paths.append({"path":os.path.join(subdir, file), "file":file})
        
max_levels = 0
data_sets = []

#First part: Parse the relevant information (tier, genre)
for file in paths:
    #1) read the file out
    data = pa.read_csv(file["path"], header = None)
    
    #force lowercase
    data[0] = [x.lower() for x in data[0].values]
        
    #2) count number of ** and create tier column
    counts = []
    new_values = []
    for x in data[0]:
        tmp = x
        #count the tier
        counts.append(tmp.count("*"))
        
        tmp = tmp[tmp.find("[")+2:tmp.find("]")]
        
        if(x.find("|") != -1):
            tmp = tmp[tmp.find("|")+1:]
            
        new_values.append(tmp)
            
    data["tier"] = counts
    data[0] = new_values
    
    #delete all rows with not at least one *
    data = data[data["tier"] != 0]
    
    #get max levels
    if(max_levels < max(data["tier"])):
        max_levels = max(data["tier"])
    
    data_sets.append(data)
        
final_data = pa.DataFrame(columns = data_sets[0].columns)

#Second part: Create new attribute indicating all super-genres!
for i, data in enumerate(data_sets):
    tmp_data = data.copy()
    #get overall super genre
    super_genre = paths[i]["file"][:-4]
    
    #create first column for super genres
    tmp_data[0] = [super_genre]*len(data)
    
    #add a new line for each super genre
    
    tmp_super = [super_genre]*len(data)
    #starting as 1
    it = 1
    while(it < max_levels):
        last_super = ""
        for j, x in enumerate(data["tier"]):
            if(x > it):
                #last value that successfully checked the test
                tmp_super[j] = last_super["name"]
                #update the last value as well as!
                tmp_super[last_super["iterat"]] = last_super["name"]
            else:
                last_super = {"name":data[0].iloc[j], "iterat":j}
                
        tmp_data[it] = tmp_super

        it += 1
    
    #Add the original genre in the last column
    tmp_data["genre"] = data.iloc[:,0].values
    
    #export
    final_data = final_data.append(tmp_data, ignore_index = True)
    final_data = final_data.append(pa.DataFrame(data = [[super_genre]*len(final_data.columns)], index = [0], columns = final_data.columns), ignore_index = True)
        
    exp_path = os.path.join((expdir), paths[i]["file"])
    tmp_data.to_csv(exp_path, encoding = "utf8", sep = ";")
    
    
#add a new line for each upper genre!
    
final_data.index = range(len(final_data))

del final_data["tier"]

final_data.to_csv('C:/Users/Manuel/OneDrive/Project_Datascience/Python/04_Projects/Spotify_API/Data/genres.csv', encoding = "utf8", sep = ";")