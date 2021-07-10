from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from app import users
import hashlib

def signup(username, password):

    result        = None
    error_message = None

    password = hashlib.md5(password.encode())

    hash_password = password.hexdigest()

    result_dict = {
        "username"  : username,
        "password"  : hash_password
    }

    # print(result_dict)

    try:
        
        response = users.insert_one(result_dict)
    
        # print(response)

    except:
        
        error_message = "Oops! Something went wrong. Try again"
    
    
def login(username, password):

    result        = None
    error_message = None

    password = hashlib.md5(password.encode())

    hash_password = password.hexdigest()

    try:

        response = users.find_one({"username" : username})
    
        print(response)
        
        print(response["password"])

        if(hash_password == response["password"]):
        
            result = True
        
        else:

            error_message = "The password that you've entered is incorrect" 

    except:

        error_message = "User not found! Create a New Account "

    return result, error_message
    
