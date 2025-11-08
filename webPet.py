"""
    Miles Phillips
    Code Toolkit: Python & Spring 2025
    WebPet (5/9/25)
"""

import json
import time
from flask import Flask, redirect, url_for, request
from flask import render_template
from threading import Thread
#terminal input to run flask "python3 -m flask --app "file name" run"

app = Flask(__name__)

#this will stop the thread from starting on the opening page, load, or create page which results in crashing because there is no json file.
background_thread = False

#Opening Page
@app.route("/")
def opening_page():
     return render_template("opening_page.html")

#Create Pet
@app.route("/create", methods=["POST","GET"])
def create_pet():
    global current_pet_name
    if request.method == "POST":
        pet_name = request.form["pet_name"]
        dob_time = time.time()
        pet_info = {
               "name": pet_name,
               "hunger":100,
               "energy":100,
               "fun":100,
               "age":0,
               "DOB":dob_time,
               #"state": "idle" #states(idle, hungry, happy, sleepy)
        }
        with open(f"{pet_name}.json","w") as f:
             json.dump(pet_info, f)
        current_pet_name=pet_name
        return redirect(url_for("pet_dashboard", pet_name=pet_name))
    return render_template("create.html")

#Load Pet
@app.route("/load", methods=["POST","GET"])
def load_pet():
    global current_pet_name
    if request.method == "POST": #sets up form
        pet_name = request.form["pet_name"] #assigns pet_name to submission
        try:
            with open(f"{pet_name}.json", "r") as f:
                _ = json.load(f) #open the file just to check it exists
            current_pet_name=pet_name
            return redirect(url_for("pet_dashboard", pet_name=pet_name))
        except FileNotFoundError:
          return "Pet not found. Please reload and try again."
    return render_template("load.html") 
     
#Background Tasks
def background_task(pet_name):
    last_hunger=time.time()
    last_fun=time.time()
    last_energy=time.time()
    while True:
        current_time=time.time()
        updated=False
        with open(f"{pet_name}.json","r") as f:
            pet_info = json.load(f)
        if current_time-last_hunger>=5:
            pet_info["hunger"] = max(pet_info["hunger"]-3,0)
            #resets current hunger time to last hunger time
            last_hunger=current_time
            #resets loop for this stat
            updated=True
        if current_time-last_fun>=30:
            pet_info["fun"] = max(pet_info["fun"]-7,0)
            last_fun=current_time
            updated=True
        if current_time-last_energy>=60:
            pet_info["energy"] = max(pet_info["energy"]-4,0)
            last_energy=current_time
            updated=True
        if updated:
            print("updating")
            save_pet(pet_info)


#Pet Dashboard
@app.route("/pet/<pet_name>")
def pet_dashboard(pet_name):
    global background_thread
    try:
        with open(f"{pet_name}.json","r") as f:
            pet_info = json.load(f)
    except FileNotFoundError:
        return "Pet not found."
    #calculating time since creation and converting to days. +1 so it starts with 1 day old.
    current_time = time.time()
    pet_info["age"]=int((current_time-pet_info["DOB"])/86400+1)
    #because background_thread is set to false globally this will switch it on but only once
    if not background_thread:
        print("Thread Starting")
        thread = Thread(target=background_task, args=(pet_name,))
        thread.start()
        background_thread=True
    return render_template("pet_dashboard.html",pet=pet_info)
 

#Buttons for Pet Interaction
@app.route("/pet/<pet_name>/feed")
def feed(pet_name):
     with open(f"{pet_name}.json","r") as f:
            pet_info = json.load(f)
     pet_info["hunger"] = min(pet_info["hunger"]+25,100)
     pet_info["energy"] = max(pet_info["energy"]-15,0)
     pet_info["fun"] = max(pet_info["fun"]-10,0)
     save_pet(pet_info)
     return redirect(url_for("pet_dashboard",pet_name=pet_name))

@app.route("/pet/<pet_name>/play")
def play(pet_name):
     with open(f"{pet_name}.json","r") as f:
            pet_info = json.load(f)
     pet_info["energy"] = max(pet_info["energy"]-40,0)
     pet_info["hunger"] = max(pet_info["hunger"]-15,0)
     pet_info["fun"] = min(pet_info["fun"]+15,100)
     save_pet(pet_info)
     return redirect(url_for("pet_dashboard",pet_name=pet_name))

@app.route("/pet/<pet_name>/rest")
def rest(pet_name):
     with open(f"{pet_name}.json","r") as f:
            pet_info = json.load(f)
     pet_info["energy"] = min(pet_info["energy"]+100,100)
     pet_info["fun"] = max(pet_info["fun"]-35,0)
     save_pet(pet_info)
     return redirect(url_for("pet_dashboard",pet_name=pet_name))

#Function to save pet stats
def save_pet(pet_info):
    with open(f"{pet_info['name']}.json", "w") as f:
        json.dump(pet_info, f)

#this app will run with the javascript in the background to continue updating the values
@app.route("/pet/<pet_name>/stats")
def pet_stats(pet_name):
     with open(f"{pet_name}.json","r") as f:
            pet_info = json.load(f)
     return {
            "hunger": pet_info["hunger"],
            "energy": pet_info["energy"],
            "fun": pet_info["fun"]
        }

if __name__ == "__main__": 
     app.run(debug=True)
