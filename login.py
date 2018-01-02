# -*- coding: utf-8 -*-
"""
Created on Fri Dec 22 22:25:07 2017

@author: Manuel
"""

import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def login():
    """
    You know the password! Just think about rf+1# =P
    Implementation is quick and dirty
    """
    #1) ask for password
    password = str.encode(input("please provide your password: \n"))

    #retreive consistent salt (in byte form)
    with open("Data/salt.txt","rb") as f:
        for row in f:
            salt = row
    
    #2) create encoder
    kdf = PBKDF2HMAC(
         algorithm=hashes.SHA256(),
         length=32,
         salt=salt,
         iterations=100000,
         backend=default_backend()
    )
    
    #3) create custom key with fixed salt and fixed password
    key = base64.urlsafe_b64encode(kdf.derive(password))
    f = Fernet(key)

    #the 
    with open("Data/CRYPTCREDENTIALS.csv","r") as csvfile: 
        for row in csvfile:
            cryptcreds = row.split(",")

    #The decoder needs the valuess in byte format and returns it in byte format as well
    credentials = {"client_id":f.decrypt(str.encode(cryptcreds[0])).decode(),
                   "client_secret":f.decrypt(str.encode(cryptcreds[1])).decode()}
    #The encrypted credentials are saved as text, therefore we need to encode and decode
    return credentials