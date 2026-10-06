from flask import Flask, request, jsonify

app = Flask(__name__)

students = {
    1: {
        "id": 1,
        "name": "Hrithik Muthappa",
        "email": "hrithik@example.com",
        "status": "ACTIVE"
    },
    2: {
        "id": 2,
        "name": "Rahul Kumar",
        "email": "rahul@example.com",
        "status": "ACTIVE"
    },
    3: {
        "id": 3,
        "name": "Ananya Sharma",
        "email": "ananya@example.com",
        "status": "ACTIVE"
    }
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": "student-service",
        "status": "UP"
    })


@app.route("/api/v1/students", methods=["GET"])
def get_students():
    return jsonify(list(students.values()))


@app.route("/api/v1/students/<int:student_id>", methods=["GET"])
def get_student(student_id):

    student = students.get(student_id)

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(student)


if __name__ == "__main__":

    app.run(
        host="localhost",
        port=5001,
        debug=True
    )