from flask import Flask, request, jsonify
from pymongo import MongoClient

from db.models.user import User
  
app = Flask(__name__)
  
# root route
@app.route('/')
def hello_world():
    return 'Hello, World!'

uri = "mongodb+srv://aditikumaresan:C3C9qU2lASi1cDt4@tourista.rdze9hh.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)

# Create database named demo if they don't exist already
db = client['user_details']
  
# Create collection named data if it doesn't exist already
collection = db['info']
  
# Add data to MongoDB route
# API endpoint to add a new user
@app.route('/api/users', methods=['POST'])
def add_user():
    data = request.get_json()
    if 'phone_number' in data:
        new_user = User(phone_number=data['phone_number'], places=data.get('places'), location=data.get('location'))
        # Insert user data into MongoDB
        collection.insert_one(new_user.__dict__)
        return jsonify({"message": "User added successfully"}), 201
    else:
        return jsonify({"message": "Invalid data"}), 400

# API endpoint to get a specific user by phone number
@app.route('/api/users/<phone_number>', methods=['GET'])
def get_user(phone_number):
    user = collection.find_one({"phone_number": phone_number})
    if user:
        return jsonify(user)
    else:
        return jsonify({"message": "User not found"}), 404

# API endpoint to add a new place for a user
@app.route('/api/users/<phone_number>/places', methods=['POST'])
def add_place(phone_number):
    data = request.get_json()
    if 'name' in data and 'lat' in data and 'long' in data:
        # Retrieve existing user data from MongoDB
        user = collection.find_one({"phone_number": phone_number})
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Add the new place to the user's places list
        user['places'].append({"name": data['name'], "lat": data['lat'], "long": data['long']})

        # Update user data in MongoDB
        collection.update_one({"phone_number": phone_number}, {"$set": user})
        return jsonify({"message": "Place added successfully"}), 201
    else:
        return jsonify({"message": "Invalid data"}), 400

# API endpoint to get all places for a user
@app.route('/api/users/<phone_number>/places', methods=['GET'])
def get_user_places(phone_number):
    user = collection.find_one({"phone_number": phone_number})
    if user:
        return jsonify(user.get('places', []))
    else:
        return jsonify({"message": "User not found"}), 404

# API endpoint to get a specific place by name for a user
@app.route('/api/users/<phone_number>/places/<place_name>', methods=['GET'])
def get_user_place_by_name(phone_number, place_name):
    user = collection.find_one({"phone_number": phone_number})
    if user:
        place = next((place for place in user.get('places', []) if place['name'] == place_name), None)
        if place:
            return jsonify(place)
        else:
            return jsonify({"message": "Place not found"}), 404
    else:
        return jsonify({"message": "User not found"}), 404

# API endpoint to delete a specific place by name for a user
@app.route('/api/users/<phone_number>/places/<place_name>', methods=['DELETE'])
def delete_user_place_by_name(phone_number, place_name):
    user = collection.find_one({"phone_number": phone_number})
    if user:
        # Filter out the place to be deleted from the user's places list
        user['places'] = [place for place in user.get('places', []) if place['name'] != place_name]

        # Update user data in MongoDB
        collection.update_one({"phone_number": phone_number}, {"$set": user})
        return jsonify({"message": "Place deleted successfully"}), 200
    else:
        return jsonify({"message": "User not found"}), 404
  
  
if __name__ == '__main__':
    app.run(port=4000)