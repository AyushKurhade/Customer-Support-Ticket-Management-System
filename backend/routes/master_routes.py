from flask import Blueprint
from backend.controllers.master_controller import (
    get_categories,
    get_priorities,
    get_statuses
)

master_bp = Blueprint('master_bp', __name__, url_prefix='/api/master')

master_bp.add_url_rule('/categories', view_func=get_categories, methods=['GET'])
master_bp.add_url_rule('/priorities', view_func=get_priorities, methods=['GET'])
master_bp.add_url_rule('/statuses', view_func=get_statuses, methods=['GET'])
