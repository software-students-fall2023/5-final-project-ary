from flask import Flask, render_template, request, redirect, url_for, make_response
from dotenv import load_dotenv
import os
import pymongo
import datetime
from bson.objectid import ObjectId
import sys
import os
import subprocess

# instantiate the app
app = Flask(__name__)

load_dotenv()  # take environment variables from .env.

# turn on debugging if in development mode
if os.getenv('FLASK_ENV', 'development') == 'development':
    # turn on debugging, if in development
    app.debug = True # debug mnode
# connect to the database

cxn = pymongo.MongoClient(os.getenv('MONGO_URI'), serverSelectionTimeoutMS=5000)
try:
    # verify the connection works by pinging the database
    cxn.admin.command('ping') # The ping command is cheap and does not require auth.
    db = cxn[os.getenv('MONGO_DBNAME')] # store a reference to the database
    print(' *', 'Connected to MongoDB!') # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(' *', "Failed to connect to MongoDB at", os.getenv('MONGO_URI'))
    print('Database connection error:', e) # debug



@app.route('/')
def login():
    return render_template('login.html')
    

@app.route('/main_page')
def main_page():
    return render_template('main_page.html')


if __name__ == "__main__":
    PORT = os.getenv('PORT', 5001) # use the PORT environment variable, or default to 5000
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    app.run(port=PORT)
