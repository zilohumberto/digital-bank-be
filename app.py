from flask import Flask
from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from settings import DEBUG_MODE
from marshmallow import ValidationError
from flask_cors import CORS


from settings import SECRET_KEY

app = Flask(__name__)
app.config.from_object("settings")
app.secret_key = SECRET_KEY
db = SQLAlchemy(app)
CORS(app)

from application.views import *


@app.errorhandler(Exception)
def handle_errors(e):
    import traceback

    status_code = 500
    rollback = True
    message = "Unhandled exception"

    if type(e) == ValidationError:
        rollback = False
        message = "Schema failed - pls check input data"
        status_code = 400
    elif type(e) == ValueError:
        rollback = False
        message = "Not found"
        status_code = 400

    if rollback:
        db.session.rollback()

    log_fn = app.logger.exception
    log_fn("Unhandled exception in: {}".format(traceback.format_exc()))
    return jsonify({"status": "failure", "message": message}), status_code


if __name__ == "__main__":
    app.run(debug=DEBUG_MODE)
