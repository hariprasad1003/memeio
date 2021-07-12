from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from app import users, rooms
import hashlib
import random
import math
import time
import rsa

def signup(username, password):

    result        = None
    error_message = None

    password = hashlib.md5(password.encode())

    hash_password = password.hexdigest()

    user = users.find().limit(1).sort([('$natural',-1)])

    # print(user)

    user_id = 0

    for user_details in user:
        last_user_id = user_details["user_id"]

    user_id = last_user_id + 1

    # print(user_id)

    result_dict = {

        "user_id"   : user_id,
        "username"  : username,
        "password"  : hash_password
    
    }

    # print(result_dict)

    try:
        
        response = users.insert_one(result_dict)
    
        # print(response)

        result = {

            "message"       : "Account Created Succesfully",
            "status_code"   :  200
    
        }

        # print(result)

    except:
        
        error_message = "Oops! Something went wrong. Try again"

        # print(error_message)
    
    
def login(username, password):

    result        = None
    error_message = None

    password = hashlib.md5(password.encode())

    hash_password = password.hexdigest()

    try:

        response = users.find_one({"username" : username})
    
        # print(response)
        
        if(hash_password == response["password"]):
        
            result = {

                "message"       : "User Loggedin Succesfully",
                "status_code"   :  200
            
            }
        
        else:

            error_message = "The password that you've entered is incorrect" 

    except:

        error_message = "User not found! Create a New Account "

    return result, error_message
    

def create_room(room_name, username):

    result        = None
    error_message = None
    pin = ""

    digits = [i for i in range(0, 10)]

    for i in range(6):

        index = math.floor(random.random() * 10)

        pin += str(digits[index])

    # print(pin)

    pub_key, priv_Key = rsa.newkeys(512)

    encrypted_pin = rsa.encrypt(pin.encode(), pub_key)

    user = users.find({ "username" : username })

    # print(user)

    for user_details in user:
        user_id  = user_details["user_id"]

    room = rooms.find().limit(1).sort([('$natural',-1)])

    # print(room)

    room_id = 0

    for room_details in room:

        last_room_id = room_details["room_id"]

    room_id = last_room_id + 1

    date_time = time.ctime()
    
    result_dict = {

        "user_id"     : user_id,
        "room_id"     : room_id,
        "room_name"   : room_name,
        "room_pin"    : encrypted_pin,
        "created_by"  : username,
        "created_at"  : date_time
    
    }

    # print(result_dict)

    try:
        
        response = rooms.insert_one(result_dict)

        # print(response)

        room = rooms.find({ "room_id" : room_id })

        room_obj = []

        for room_details in room:

            user_id     = room_details["user_id"]
            room_id     = room_details["room_id"]
            room_name   = room_details["room_name"]
            room_pin    = room_details["room_pin"]
            created_by  = room_details["created_by"]
            created_at  = room_details["created_at"]

        decrypted_pin =  rsa.decrypt(room_pin, priv_Key).decode()

        result = {

            "message"      : "Room Created Successfully",
            "user_id"      : user_id,
            "room_id"      : room_id,
            "room_name"    : room_name,
            "status_code"  : 200,
            "room_pin"     : decrypted_pin,
            "created_by"   : created_by,
            "created_at"   : created_at
        
        }

    except:
        
        error_message = "Oops! Something went wrong. Try again"

    return result, error_message