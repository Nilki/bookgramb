from flask import Flask, request, jsonify
from pymongo import MongoClient
import json

import prediction


app = Flask(__name__)
client = MongoClient('localhost', 27017)

db = client.bookgram_db
authentication = db.authentication
locations = db.locations


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.route('/predict', methods=['POST'])
def predict_genre():
    input_text = request.json['description']
    data = prediction.get_genre(input_text)
    return jsonify(data)


@app.route('/register', methods=['POST'])
def register():
    # get current value of next_id from database
    next_id = db.counter.find_one_and_update(
        {'_id': 'userid'},
        {'$inc': {'seq': 1}},
        upsert=True,
        return_document=True
    )['seq']

    data = json.loads(request.data)
    email = data['email']
    password = data['password']
    full_name = data.get('full_name', '')

    # check if user already exists
    if authentication.find_one({'email': email}):
        return {'message': 'User already exists'}, 400

    # create new user
    user = {
        'userid': next_id,
        'email': email,
        'password': password,
        'full_name': full_name,
    }
    result = authentication.insert_one(user)
    next_id += 1
    return {'message': 'User registered successfully',
            'userid': user['userid']}, 200


@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    email = data['email']
    password = data['password']

    # find user by email and password
    user = authentication.find_one({'email': email, 'password': password})
    if user:
        return {'message': 'User authenticated successfully'}, 200
    else:
        return {'message': 'Invalid email or password'}, 401


@app.route('/locations', methods=['POST'])
def add_location():
    data = json.loads(request.data)
    longitude = data['longitude']
    latitude = data['latitude']

    # save location to locations collection
    location = {
        'longitude': longitude,
        'latitude': latitude,
    }
    result = locations.insert_one(location)

    return {'message': 'Location saved successfully'}, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
