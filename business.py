from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from app import users
import hashlib

def signup(email, username, password):

    result        = None
    error_message = None

    password = hashlib.md5(password.encode())

    hash_password = password.hexdigest()

    result_dict = {
        "email"     : email,
        "username"  : username,
        "password"  : hash_password
    }

    # print(result_dict)

    try:
        
        response = users.insert_one(result_dict)
    
        # print(response)

    except:
        
        error_message = "Oops! Something went wrong. Try again"
    
    
def login(email, password):

    result        = None
    error_message = None

    password = hashlib.md5(password.encode())

    hash_password = password.hexdigest()

    response = users.find_one({"email" : email})
    
    # print(response)
    
    # print(response["password"])

    if(hash_password == response["password"]):
        
        result = True
    else:
        error_message = "The password that you've entered is incorrect"        

    return result, error_message
    
