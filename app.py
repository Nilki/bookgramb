from flask import Flask, request, jsonify
from pymongo import MongoClient
import json
from flask_cors import CORS
from bson import ObjectId

import hybrid_recommendation

app = Flask(__name__)
CORS(app)
client = MongoClient('localhost', 27017)

db = client.bookgram_db
authentication = db.authentication
locations = db.locations
books = db.books


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/rec', methods=['POST'])
def recommend_books():
    global recommendations
    description = request.json['description']
    location = request.json['location']

    print(description)
    print(location)

    # Call the get_lstm_prediction function to get the top 10 books with the predicted genre
    top10_books = hybrid_recommendation.get_lstm_prediction(description)

    # Call the hybrid_recommendation function to get the final recommended books
    # recommended = hybrid_recommendation.hybrid_recommendation(top10_books, 0, location)

    # data = {"recommendations": recommendations.to_dict(orient='records')}
    recommendations_json = top10_books.to_json(orient='records', date_format='iso', date_unit='s',
                                                   default_handler=str)
    # data = {"recommendations": json.loads(recommendations_json)}
    recommendations = recommendations_json
    # print(recommendations)

    # Convert the recommendations dataframe to a JSON object and return it
    return jsonify(1)


@app.route('/rec1', methods=['GET'])
def get_recommendations():
    print(recommendations)
    data = {"recommendations": json.loads(recommendations)}
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


@app.route('/add_book', methods=['POST'])
def add_book():

    data = json.loads(request.data)
    bookName = data['bookName']
    author = data['author']
    description = data['description']
    isbn = data['isbn']

    # Added new book
    book = {
        'bookName': bookName,
        'author': author,
        'description': description,
        'isbn': isbn,
    }
    result = books.insert_one(book)
    return {'message': 'Book registered successfully'}, 200


@app.route('/get_books', methods=['GET'])
def get_books():
    result = books.find()
    data = []
    for document in result:
        # Convert ObjectId to string for serialization
        document['_id'] = str(document['_id'])
        data.append(document)
    return {'result': data}, 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
