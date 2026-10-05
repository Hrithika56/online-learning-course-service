from flask import Flask, request, jsonify
from database import initialize_database, get_db_connection

app = Flask(__name__)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return "Course Service is running!"


# ============================================================
# API VERSION 1
# ============================================================

# CREATE a course
@app.route("/api/v1/courses", methods=["POST"])
def create_course():
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    instructor = data.get("instructor")
    category = data.get("category")
    duration = data.get("duration")
    price = data.get("price")

    if not title or not instructor:
        return jsonify({
            "error": "Title and instructor are required"
        }), 400

    connection = get_db_connection()

    cursor = connection.execute("""
        INSERT INTO courses
        (title, description, instructor, category, duration, price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        description,
        instructor,
        category,
        duration,
        price
    ))

    connection.commit()

    course_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Course created successfully",
        "course_id": course_id
    }), 201


# GET all courses
@app.route("/api/v1/courses", methods=["GET"])
def get_courses():
    connection = get_db_connection()

    courses = connection.execute(
        "SELECT * FROM courses"
    ).fetchall()

    connection.close()

    return jsonify([dict(course) for course in courses])


# GET a single course by ID
@app.route("/api/v1/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    connection = get_db_connection()

    course = connection.execute(
        "SELECT * FROM courses WHERE course_id = ?",
        (course_id,)
    ).fetchone()

    connection.close()

    if course is None:
        return jsonify({
            "error": "Course not found"
        }), 404

    return jsonify(dict(course))


# UPDATE a course
@app.route("/api/v1/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    instructor = data.get("instructor")
    category = data.get("category")
    duration = data.get("duration")
    price = data.get("price")
    status = data.get("status")

    connection = get_db_connection()

    existing_course = connection.execute(
        "SELECT * FROM courses WHERE course_id = ?",
        (course_id,)
    ).fetchone()

    if existing_course is None:
        connection.close()

        return jsonify({
            "error": "Course not found"
        }), 404

    connection.execute("""
        UPDATE courses
        SET title = ?,
            description = ?,
            instructor = ?,
            category = ?,
            duration = ?,
            price = ?,
            status = ?
        WHERE course_id = ?
    """, (
        title,
        description,
        instructor,
        category,
        duration,
        price,
        status,
        course_id
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Course updated successfully",
        "course_id": course_id
    })


# DELETE a course
@app.route("/api/v1/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    connection = get_db_connection()

    course = connection.execute(
        "SELECT * FROM courses WHERE course_id = ?",
        (course_id,)
    ).fetchone()

    if course is None:
        connection.close()

        return jsonify({
            "error": "Course not found"
        }), 404

    connection.execute(
        "DELETE FROM courses WHERE course_id = ?",
        (course_id,)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Course deleted successfully",
        "course_id": course_id
    })


# ============================================================
# API VERSION 2
# ============================================================

# GET all courses - Version 2
@app.route("/api/v2/courses", methods=["GET"])
def get_courses_v2():
    connection = get_db_connection()

    courses = connection.execute(
        "SELECT * FROM courses"
    ).fetchall()

    connection.close()

    return jsonify({
        "version": "v2",
        "total_courses": len(courses),
        "courses": [dict(course) for course in courses]
    })


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)