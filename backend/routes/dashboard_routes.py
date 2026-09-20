from flask import Blueprint
from backend.utils.auth_middleware import role_required
from backend.controllers.dashboard_controller import get_dashboard_statistics

dashboard_bp = Blueprint('dashboard_bp', __name__, url_prefix='/api/dashboard')

# Accessible to Agents and Admins
dashboard_bp.add_url_rule('/stats', view_func=role_required(['agent', 'admin'])(get_dashboard_statistics), methods=['GET'])

