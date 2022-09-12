from flask import Flask, request, jsonify, make_response, abort, url_for
import json
import requests
import os

OPA_URL = "http://localhost:8181"


def get_authentication(request):
    return request.headers.get("Authorization", "")


app = Flask(__name__)


@app.route('/')
def index():
    return 'Hello world'


@app.before_request
def check_authorization():
    try:
        input = json.dumps({
            "method": request.method,
            "path": request.path.strip().split("/")[1:],
            "user": get_authentication(request),
        }, indent=2)
        url = os.environ.get("OPA_URL", OPA_URL)
        app.logger.debug("OPA query: %s. Body: %s", url, input)
        response = requests.post(url, data=input)
    except Exception as e:
        app.logger.exception("Unexpected error querying OPA.")
        abort(500)

    if response.status_code != 200:
        app.logger.error("OPA status code: %s. Body: %s",
                         response.status_code, response.json())
        abort(500)

    allowed = response.json()
    app.logger.debug("OPA result: %s", allowed)
    if not allowed:
        abort(403)


app.run(host='0.0.0.0', port=81)
