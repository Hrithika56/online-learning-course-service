import os

from dotenv import load_dotenv

from flask import Flask, request, jsonify, send_from_directory

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from database import db
from models import User
from auth import hash_password, verify_password


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# CREATE FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# FRONTEND
# ==========================================

FRONTEND_FOLDER = os.path.join(
    app.root_path,
    "frontend"
)


@app.route("/web")
def web():
    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


@app.route("/web/<path:filename>")
def web_files(filename):
    return send_from_directory(
        FRONTEND_FOLDER,
        filename
    )


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ==========================================
# JWT CONFIGURATION
# ==========================================

app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY"
)


# ==========================================
# INITIALIZE DATABASE AND JWT
# ==========================================

db.init_app(app)

jwt = JWTManager(app)


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

with app.app_context():
    db.create_all()


# ==========================================
# HOME / HEALTH CHECK
# ==========================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "service": "User Authentication Service",
        "status": "running"
    })


# ==========================================
# REGISTER USER
# ==========================================

@app.route("/api/v1/users/register", methods=["POST"])
def register():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "Email already registered"
        }), 409

    hashed_password = hash_password(password)

    user = User(
        name=name,
        email=email,
        password=hashed_password,
        role="student"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user": user.to_dict()
    }), 201


# ==========================================
# LOGIN USER
# ==========================================

@app.route("/api/v1/users/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    user = User.query.filter_by(
        email=email
    ).first()

    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not verify_password(
        user.password,
        password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.id)
    )

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


# ==========================================
# GET ALL USERS
# ==========================================

@app.route("/api/v1/users", methods=["GET"])
def get_users():

    users = User.query.all()

    return jsonify([
        user.to_dict()
        for user in users
    ]), 200


# ==========================================
# GET USER BY ID
# ==========================================

@app.route("/api/v1/users/<int:user_id>", methods=["GET"])
def get_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify(
        user.to_dict()
    ), 200


# ==========================================
# GET CURRENT LOGGED-IN USER
# ==========================================

@app.route("/api/v1/users/me", methods=["GET"])
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = User.query.get(
        int(user_id)
    )

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    return jsonify({
        "message": "Authenticated user",
        "user": user.to_dict()
    }), 200


# ==========================================
# UPDATE USER
# ==========================================

@app.route("/api/v1/users/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    current_user_id = get_jwt_identity()

    if int(current_user_id) != user_id:
        return jsonify({
            "error": "You can only update your own account"
        }), 403

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "name" in data:
        user.name = data["name"]

    if "email" in data:

        existing_user = User.query.filter_by(
            email=data["email"]
        ).first()

        if existing_user and existing_user.id != user.id:
            return jsonify({
                "error": "Email already in use"
            }), 409

        user.email = data["email"]

    if "password" in data:

        user.password = hash_password(
            data["password"]
        )

    db.session.commit()

    return jsonify({
        "message": "User updated successfully",
        "user": user.to_dict()
    }), 200


# ==========================================
# DELETE USER
# ==========================================

@app.route("/api/v1/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "error": "User not found"
        }), 404

    current_user_id = get_jwt_identity()

    if int(current_user_id) != user_id:
        return jsonify({
            "error": "You can only delete your own account"
        }), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully"
    }), 200


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )