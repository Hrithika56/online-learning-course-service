from flask import Flask, request, jsonify
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
# CREATE FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ==========================================
# JWT CONFIGURATION
# ==========================================

app.config["JWT_SECRET_KEY"] = "team10-user-service-secret"


# Initialize database and JWT
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

    # Check request body
    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    # Get data
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Validate required fields
    if not name or not email or not password:
        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    # Check if email already exists
    existing_user = User.query.filter_by(
        email=email
    ).first()

    if existing_user:
        return jsonify({
            "error": "Email already registered"
        }), 409

    # Hash password
    hashed_password = hash_password(password)

    # Create user
    user = User(
        name=name,
        email=email,
        password=hashed_password,
        role="student"
    )

    # Save user
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

    # Check request body
    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    # Get login data
    email = data.get("email")
    password = data.get("password")

    # Validate fields
    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    # Find user
    user = User.query.filter_by(
        email=email
    ).first()

    # User doesn't exist
    if not user:
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    # Check password
    if not verify_password(
        user.password,
        password
    ):
        return jsonify({
            "error": "Invalid email or password"
        }), 401

    # Create JWT token
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

    # Get user ID from JWT token
    user_id = get_jwt_identity()

    # Find user
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

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    # Update name
    if "name" in data:
        user.name = data["name"]

    # Update email
    if "email" in data:

        existing_user = User.query.filter_by(
            email=data["email"]
        ).first()

        if existing_user and existing_user.id != user.id:
            return jsonify({
                "error": "Email already in use"
            }), 409

        user.email = data["email"]

    # Update password
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