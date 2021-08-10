from app import users, rooms
import hashlib
import random
import math
import time

def signup(username, password):

    result = None

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
        
        result = {

            "message"       : "Oops! Something went wrong. Try again",
            "status_code"   :  400
    
        }


        error_message = ""

        # print(error_message)

    return result
    
    
def login(username, password):

    result = None

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

            result = {

                "message"       : "The password that you've entered is incorrect",
                "status_code"   :  400
            
            }

    except:


        result = {

            "message"       : "User not found! Create a New Account",
            "status_code"   :  404
        
        }

    return result
    

def create_room(room_name, username):

    result = None
    pin = ""

    digits = [i for i in range(0, 10)]

    for i in range(6):

        index = math.floor(random.random() * 10)

        pin += str(digits[index])

    # print(pin)

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
        "room_pin"    : int(pin),
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

        result = {

            "message"      : "Room Created Successfully",
            "user_id"      : user_id,
            "room_id"      : room_id,
            "room_name"    : room_name,
            "status_code"  : 200,
            "room_pin"     : room_pin,
            "created_by"   : created_by,
            "created_at"   : created_at
        
        }

    except:

        result = {
            
            "message"     : "Oops! Something went wrong. Try again",
            "status_code" : 400

        }
        

    return result

def enter_room(name, user_room_pin):

    result = None
    db_room_pin = None
    room_id     = None
    room_name   = None
    created_by  = None
    created_at  = None

    # print(user_room_pin)

    # print(type(user_room_pin))

    try:

        room = rooms.find_one({"room_pin" : int(user_room_pin)})
    
        # print(room)

        db_room_pin = room["room_pin"]
        room_id     = room["room_id"]
        room_name   = room["room_name"]
        created_by  = room["created_by"]
        created_at  = room["created_at"]

    except:

        result = {

            "message"       : "Oops! Something went wrong. Try again",
            "status_code"   :  400
        
        }


    if(int(user_room_pin) == db_room_pin):

        if(str(name) == str(created_by)):

            acc_type = "admin"

        else:

            acc_type = "user"
    
        result = {

            "message"     : "Participant Entered Room Successfully",
            "status_code" : 200,
            "room_id"     : room_id, 
            "room_name"   : room_name, 
            "created_by"  : created_by, 
            "created_at"  : created_at,
            "acc_type"    : acc_type

        }
        
    else:

        result = {

            "message"       : "The pin that you've entered is incorrect",
            "status_code"   :  400
        
        }



    return result

