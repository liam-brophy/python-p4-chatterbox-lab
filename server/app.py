from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()
    if not Message.query.first():
        default_message = Message(body="Welcome to Chatterbox!", username="admin")
        db.session.add(default_message)
        db.session.commit()

@app.route('/messages', methods=["GET", "POST"])
def messages():
    if request.method == "GET":
        messages = Message.query.order_by(Message.created_at.asc()).all()
        response = make_response(jsonify([message.to_dict() for message in messages]), 200)
    elif request.method == "POST":
        body = request.json.get('body')
        username = request.json.get('username')
        message = Message(body=body, username=username)
        db.session.add(message)
        db.session.commit()
        response = make_response(message.to_dict(), 201)
        
    return response

@app.route('/messages/<int:id>', methods=["GET", "PATCH", "DELETE"])
def messages_by_id(id):
    message = Message.query.filter(Message.id==id).first()
    if not message:
        response = make_response({"message": f"We could not find a message with such id ({id})"}, 200) 
    elif request.method == "GET":
        response = make_response(message.to_dict(), 200)
    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        response = make_response({"message": "successfully deleted message"}, 200)
    elif request.method == "PATCH":
        if message:  # Ensure message exists before updating
            body = request.json.get('body')
            if body:
                message.body = body
                db.session.add(message)
                db.session.commit()
                response = make_response(message.to_dict(), 200)
            else:
                response = make_response({"message": "Body is required to update the message"}, 400)
        else:
            response = make_response({"message": f"Message with id {id} not found"}, 404)
        
    return response

if __name__ == '__main__':
    app.run(port=5555)
