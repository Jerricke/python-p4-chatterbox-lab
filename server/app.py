from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
import json

from models import db, Message

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    return "<h1>This is working!</h1>"


@app.route("/messages", methods=["GET", "POST"])
def messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()

    if messages == None:
        response = make_response("No messages found", 404)
        return response
    else:
        if request.method == "GET":
            response_body = [message.to_dict() for message in messages]
            response_body_serialized = jsonify(response_body)
            return make_response(response_body_serialized, 200)
        if request.method == "POST":
            data = request.json
            new_message = Message(
                body=data["body"],
                username=data["username"],
            )
            db.session.add(new_message)
            db.session.commit()

            response = make_response(jsonify(new_message.to_dict()), 200)

            return response


@app.route("/messages/<int:id>", methods=["PATCH", "DELETE"])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if message == None:
        response = make_response("Message not found", 404)
        return response
    else:
        if request.method == "PATCH":
            data = request.json
            for attr in data:
                setattr(message, attr, data[attr])
            db.session.add(message)
            db.session.commit()

            response = make_response(message.to_dict(), 200)
            response.headers["Content-Type"] = "application/json"
            return response
        elif request.method == "DELETE":
            db.session.delete(message)
            db.session.commit()

            response_body = {
                "Message": "Deleted a message sucessfully",
            }
            response = make_response(jsonify(response_body), 200)
            return response


if __name__ == "__main__":
    app.run(port=5555)
