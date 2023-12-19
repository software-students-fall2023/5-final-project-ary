from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, send_file
from dotenv import load_dotenv
import os
import pymongo
import datetime
from bson.objectid import ObjectId
from datetime import datetime
from gridfs import GridFS
import mimetypes

# instantiate the app
app = Flask(__name__)
app.config['SECRET_KEY'] = '123'

app.debug = True

load_dotenv()  # take environment variables from .env.

mongo_db_name = os.getenv('MONGO_DBNAME')
if not mongo_db_name:
    raise RuntimeError("MONGO_DBNAME environment variable is not set")
    
client = pymongo.MongoClient(os.getenv('MONGO_URI'), serverSelectionTimeoutMS=5000)
db = client[mongo_db_name]

try:
    # verify the connection works by pinging the database
    client.admin.command('ping') # The ping command is cheap and does not require auth.
    db = client[os.getenv('MONGO_DBNAME')] # store a reference to the database
    print(' *', 'Connected to MongoDB!') # if we get here, the connection worked!
except Exception as e:
    # the ping command failed, so the connection is not available.
    print(' *', "Failed to connect to MongoDB at", os.getenv('MONGO_URI'))
    print('Database connection error:', e) # debug

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/some_route')
def some_route():
    data = db.your_collection.find()
    return "Data retrieved"

@app.route('/')
def direct_to_login():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = db.users.find_one({'username': username})
        if user is None:
            flash('Username not found! Please register your account!', 'danger')
        elif user is not None and user['password'] != password:
            flash('Incorrect password! Please try again!')
        else:
            return redirect(url_for('main_page', user_id = user['_id']))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = db.users.find_one({'username': username})

        if existing_user:
            flash('Username already exists. Please choose a different one.')
        else:
            db.users.insert_one({'username': username, 'password': password})
            flash('Registration successful! You can now log in.')
            return redirect(url_for('login'))

    return render_template('register.html')

def get_username(user_id):
    return db.users.find_one({'_id': ObjectId(user_id)})['username']

@app.route('/image/<string:file_id>')
def get_image(file_id):
    fs = GridFS(db)
    file_data = fs.get(ObjectId(file_id))

    if file_data:
        mimetype, encoding = mimetypes.guess_type(file_data.filename)
        response = send_file(file_data , mimetype=mimetype)
        return response

    # Return a placeholder image or handle the case where the image is not found
    return 'Image not found', 404

@app.route('/main_page/<user_id>')
def main_page(user_id):
    # db.items.insert_one({"name":"frog", "desc":"this is a frog"})
    items = db.items.find({}).sort("createdAt", -1)
    return render_template('main_page.html', items=items, user_id=user_id, get_username=get_username)

@app.route('/personal_collections/<user_id>', methods=['GET','POST'])
def my_collections(user_id):
    items = db.items.find({"user_id": user_id}).sort("createdAt", -1)

    return render_template('personal_collections.html', items=items, user_id=user_id)

@app.route('/upload/<user_id>', methods=['GET','POST'])
def upload(user_id):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            fs = GridFS(db)
            file_id = fs.put(file, filename=file.filename)
            item_name = request.form['name']
            item_desc = request.form['description']
            item = {
                "name":item_name,
                "desc":item_desc,
                "user_id":user_id,
                "file_id":file_id,
                "createdAt": datetime.utcnow(),
            }
            db.items.insert_one(item)
            return redirect(url_for('my_collections', user_id=user_id))

        flash('Invalid file format. Allowed formats: png, jpg, jpeg, gif', 'danger')

    return render_template('upload.html', user_id=user_id)
    
@app.route('/update/<user_id>/<item_id>', methods=['GET', 'POST'])
def update(user_id, item_id):
    if request.method == 'POST':
        file = request.files.get('file')
        item_name = request.form.get('name')
        item_desc = request.form.get('description')

        update_data = {"name": item_name, "desc": item_desc}
        
        if file and allowed_file(file.filename):
            fs = GridFS(db)
            file_id = fs.put(file, filename=file.filename)
            update_data["file_id"] = file_id

            old_item = db.items.find_one({"_id": ObjectId(item_id)})
            fs.delete(ObjectId(old_item['file_id']))

        db.items.update_one({"_id": ObjectId(item_id)}, {"$set": update_data})
        return redirect(url_for('my_collections', user_id=user_id))
    else:
        item = db.items.find_one({"_id": ObjectId(item_id)})
        return render_template('update.html', item=item, user_id=user_id)

@app.route('/delete/<user_id>/<item_id>')
def delete(user_id, item_id):
    item_del = db.items.find_one({"_id": ObjectId(item_id)})
    fs = GridFS(db)
    fs.delete(ObjectId(item_del['file_id']))
    db.items.delete_one({"_id": ObjectId(item_id)})
    return redirect(url_for('my_collections', user_id=user_id))

if __name__ == "__main__":
    PORT = os.getenv('PORT', 5050) # use the PORT environment variable, or default to 5000
    #import logging
    #logging.basicConfig(filename='/home/ak8257/error.log',level=logging.DEBUG)
    # app.run(port=PORT, debug=True)
    app.run(host="0.0.0.0", debug=True, port=PORT)

