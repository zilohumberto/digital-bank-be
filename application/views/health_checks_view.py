from app import app
from flask import jsonify


@app.route("/")
def ping():
    return jsonify({"status": "success", "data": "pong"})
