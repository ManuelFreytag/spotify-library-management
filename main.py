# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 18:34:43 2017

@author: Manuel
"""
import dataImport
import importlib
import csv
from login import login

importlib.reload(dataImport)

def main():
    credentials = login()
    
    deselect = ["Hörbücher"]
    username = "manu.freytag@web.de"
    
    data = dataImport.getData(credentials,username, saved = True)
    #data = dataImport.getData(credentials,username, saved = False, deselect = deselect)
    
    return data
    

data = main()
data.to_csv("data.csv", sep = ";", decimal = ",")
    

#Data exploration
#1) number of songs without genre
#2) number of songs that share not a single genre with anyone else
    
# -> Outlier detection?!

#Data preprocessing
#Merge attributes based on knowledge base (pop, hiphop, rock, etc.)

#Analysis etc.