import json

from werkzeug.exceptions import HTTPException

from app import app


class WeatherException(HTTPException):
    code = 400
    description = 'invalid input data entered'


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""

    response = e.get_response()
    response.data = json.dumps({
        "message": e.description,
    })
    response.content_type = "application/json"
    return response
