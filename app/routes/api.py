from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.contants import WEATHER_FILES_PATH
from app.exceptions import WeatherException
from weatherman.runner import process_args, compute_monthly_average, generate_average_report

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/weatherman/yearly_report', methods=['GET'])
@jwt_required()
def weatherman_yearly_report():
    strategy = {
        'calc_strategy': None,
        'report_strategy': None
    }
    dates = request.args.getlist('year')
    try:
        reports = process_args(dates, 1, WEATHER_FILES_PATH, strategy, yearly=True)
    except Exception as e:
        raise WeatherException

    return jsonify(reports), 200


@api_bp.route('/weatherman/monthly_report', methods=['GET'])
@jwt_required()
def weatherman_monthly_report():
    strategy = {
        'calc_strategy': compute_monthly_average,
        'report_strategy': generate_average_report
    }
    dates = request.args.getlist('date')
    try:
        reports = process_args(dates, 1, WEATHER_FILES_PATH, strategy)
    except Exception as e:
        raise WeatherException

    return jsonify(reports), 200
