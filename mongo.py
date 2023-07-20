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
  
# API endpoint to get all places for a user
@app.route('/api/users/<phone_number>/places', methods=['GET'])
def get_user_places(phone_number):
    user = collection.find_one({"phone_number": phone_number})
    if user:
        return jsonify(user.get('places', []))
    else:
        return jsonify({"message": "User not found"}), 404


# API endpoint to update all places for a user
@app.route('/api/users/<phone_number>/places', methods=['PATCH'])
def update_user_places(phone_number):
    data = request.get_json()
    print(data)
    if 'places' in data and isinstance(data['places'], list):
        # Retrieve existing user data from MongoDB
        user = collection.find_one({"phone_number": phone_number})
        if not user:
            # If user does not exist, create a new user document
            new_user = {
                "phone_number": phone_number,
                "places": data['places']
            }
            collection.insert_one(new_user)
            return jsonify({"message": "New user created successfully"}), 201
        else:
            # If user exists, update the user's places list with the new list of places
            user['places'] = data['places']
            # Update user data in MongoDB
            collection.update_one({"phone_number": phone_number}, {"$set": user})
            return jsonify({"message": "Places updated successfully"}), 200
    else:
        return jsonify({"message": "Invalid data"}), 400

  
if __name__ == '__main__':
    app.run(port=4000)