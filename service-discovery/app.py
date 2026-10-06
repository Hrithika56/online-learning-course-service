from flask import Flask, request, jsonify

app = Flask(__name__)

services = {}


@app.route("/register", methods=["POST"])
def register_service():

    data = request.get_json()

    name = data.get("name")
    url = data.get("url")

    if not name or not url:
        return jsonify({
            "error": "name and url are required"
        }), 400

    services[name] = {
        "url": url
    }

    return jsonify({
        "message": "Service registered successfully",
        "name": name,
        "url": url
    }), 201


@app.route("/services/<name>", methods=["GET"])
def get_service(name):

    service = services.get(name)

    if service is None:
        return jsonify({
            "error": "Service not found"
        }), 404

    return jsonify({
        "name": name,
        "url": service["url"]
    })


@app.route("/services", methods=["GET"])
def get_services():

    return jsonify(services)


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "service": "service-discovery",
        "status": "UP"
    })


if __name__ == "__main__":

    app.run(
        host="localhost",
        port=5000,
        debug=True
    )