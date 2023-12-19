import pytest
from flask import Flask 
from app import app
from mongomock import MongoClient
import mongomock.gridfs
import io

# Setup for the Flask testing environment
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Mocking MongoDB
@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    mock_client = MongoClient()
    mock_db = mock_client['test_db']
    monkeypatch.setattr("pymongo.MongoClient", lambda *args, **kwargs: mock_client)

    # Mock GridFS
    grid_fs = mongomock.gridfs.GridFS(mock_db)
    monkeypatch.setattr("gridfs.GridFS", lambda db, **kwargs: grid_fs)

    yield

# Test for the main page access
def test_main_page_access(client):
    response = client.get('/main_page/test_user_id')
    assert response.status_code == 200

# Test for user registration
def test_register_user(client):
    response = client.post('/register', data={'username': 'testuser', 'password': 'testpass'})
    assert b'Registration successful' in response.data

# Test for user login
def test_login(client):
    client.post('/register', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/login', data={'username': 'testuser', 'password': 'testpass'})
    assert b'Incorrect password' not in response.data

# Test for unsuccessful login due to wrong password
def test_login_failure_wrong_password(client):
    client.post('/register', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/login', data={'username': 'testuser', 'password': 'wrongpass'})
    assert b'Incorrect password' in response.data

# Test for unsuccessful registration due to existing user
def test_register_existing_user(client):
    client.post('/register', data={'username': 'testuser', 'password': 'testpass'})
    response = client.post('/register', data={'username': 'testuser', 'password': 'anotherpass'})
    assert b'Username already exists' in response.data

# Test for uploading a file
def test_file_upload(client):
    data = {
        'file': (io.BytesIO(b"test file contents"), 'test.jpg'),
        'name': 'test item',
        'description': 'test description'
    }
    response = client.post('/upload/test_user_id', data=data, content_type='multipart/form-data')
    assert b'Invalid file format' not in response.data

# Test for image retrieval
def test_get_image(client):
    # Add a test image to the database and use its ID here
    fs = mongomock.gridfs.GridFS(mock_db)
    file_id = fs.put(io.BytesIO(b"test image data"), filename="test.jpg")
    response = client.get(f'/image/{test_image_id}')
    assert response.status_code == 200
    assert response.content_type.startswith('image/')
    
# Test for update function
def test_update_item_get(client, mock_db):

    test_item = mock_db.items.insert_one({"name": "test item", "desc": "description", "user_id": "test_user_id", "file_id": "some_file_id"})
    test_item_id = test_item.inserted_id
    response = client.get(f'/update/test_user_id/{test_item_id}')
    assert response.status_code == 200
    assert b'Update Item' in response.data

def test_update_item_post(client, mock_db):
    test_item = mock_db.items.insert_one({"name": "original name", "desc": "original description", "user_id": "test_user_id", "file_id": "some_file_id"})
    test_item_id = test_item.inserted_id

    updated_data = {
        'name': 'updated name',
        'description': 'updated description'
    }

    response = client.post(f'/update/test_user_id/{test_item_id}', data=updated_data)
    assert response.status_code == 302

    updated_item = mock_db.items.find_one({"_id": test_item_id})
    assert updated_item['name'] == 'updated name'
    assert updated_item['desc'] == 'updated description'

# Test for deleting an item
def test_delete_item(client):
    # Mock adding an item and getting its ID
    test_item = mock_db.items.insert_one({"name": "test item", "desc": "description", "user_id": "test_user_id"})
    test_item_id = test_item.inserted_id
    response = client.get(f'/delete/test_user_id/{test_item_id}')
    # Check if redirect occurred to the my_collections page
    assert response.status_code == 302
    assert '/personal_collections/test_user_id' in response.headers['Location']

# Test for requesting a non-existent image
def test_get_nonexistent_image(client):
    response = client.get('/image/nonexistent_id')
    assert response.status_code == 404
    assert b'Image not found' in response.data