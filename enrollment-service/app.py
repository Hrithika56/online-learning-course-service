from flask import Flask, request, jsonify
from database import get_db, init_db

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "enrollment-service",
        "status": "UP"
    })


@app.route("/api/v1/enrollments", methods=["POST"])
def create_enrollment():

    data = request.get_json()

    student_id = data.get("student_id")
    course_id = data.get("course_id")

    if not student_id or not course_id:
        return jsonify({
            "error": "student_id and course_id are required"
        }), 400

    connection = get_db()

    cursor = connection.execute("""
        INSERT INTO enrollments
        (student_id, course_id, status)
        VALUES (?, ?, ?)
    """, (
        student_id,
        course_id,
        "ENROLLED"
    ))

    connection.commit()

    enrollment_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Student enrolled successfully",
        "enrollment": {
            "id": enrollment_id,
            "student_id": student_id,
            "course_id": course_id,
            "status": "ENROLLED"
        }
    }), 201


@app.route("/api/v1/enrollments/<int:enrollment_id>",
           methods=["GET"])
def get_enrollment(enrollment_id):

    connection = get_db()

    enrollment = connection.execute("""
        SELECT *
        FROM enrollments
        WHERE id = ?
    """, (enrollment_id,)).fetchone()

    connection.close()

    if enrollment is None:
        return jsonify({
            "error": "Enrollment not found"
        }), 404

    return jsonify({
        "id": enrollment["id"],
        "student_id": enrollment["student_id"],
        "course_id": enrollment["course_id"],
        "status": enrollment["status"],
        "enrolled_at": enrollment["enrolled_at"]
    })


@app.route("/api/v1/enrollments/student/<int:student_id>",
           methods=["GET"])
def get_student_enrollments(student_id):

    connection = get_db()

    enrollments = connection.execute("""
        SELECT *
        FROM enrollments
        WHERE student_id = ?
    """, (student_id,)).fetchall()

    connection.close()

    result = []

    for enrollment in enrollments:
        result.append({
            "id": enrollment["id"],
            "student_id": enrollment["student_id"],
            "course_id": enrollment["course_id"],
            "status": enrollment["status"],
            "enrolled_at": enrollment["enrolled_at"]
        })

    return jsonify(result)


@app.route("/api/v1/enrollments/<int:enrollment_id>",
           methods=["DELETE"])
def cancel_enrollment(enrollment_id):

    connection = get_db()

    enrollment = connection.execute("""
        SELECT *
        FROM enrollments
        WHERE id = ?
    """, (enrollment_id,)).fetchone()

    if enrollment is None:
        connection.close()

        return jsonify({
            "error": "Enrollment not found"
        }), 404

    connection.execute("""
        UPDATE enrollments
        SET status = ?
        WHERE id = ?
    """, (
        "CANCELLED",
        enrollment_id
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Enrollment cancelled successfully",
        "enrollment_id": enrollment_id,
        "status": "CANCELLED"
    })


if __name__ == "__main__":

    init_db()

    app.run(
        host="localhost",
        port=5003,
        debug=True
    )