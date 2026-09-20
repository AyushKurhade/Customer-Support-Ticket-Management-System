from flask import Blueprint, request
from backend.utils.auth_middleware import role_required
from backend.controllers.reports_controller import (
    get_category_report,
    get_status_report,
    get_priority_report,
    get_agent_performance_report,
    get_resolution_time_analysis,
    export_report_csv
)

reports_bp = Blueprint('reports_bp', __name__, url_prefix='/api/reports')

# Analytical Report endpoints (restricted to Agent & Admin)
reports_bp.add_url_rule('/category', view_func=role_required(['agent', 'admin'])(get_category_report), methods=['GET'])
reports_bp.add_url_rule('/status', view_func=role_required(['agent', 'admin'])(get_status_report), methods=['GET'])
reports_bp.add_url_rule('/priority', view_func=role_required(['agent', 'admin'])(get_priority_report), methods=['GET'])
reports_bp.add_url_rule('/agents', view_func=role_required(['agent', 'admin'])(get_agent_performance_report), methods=['GET'])
reports_bp.add_url_rule('/resolution-time', view_func=role_required(['agent', 'admin'])(get_resolution_time_analysis), methods=['GET'])

@reports_bp.route('/export', methods=['GET'])
@role_required(['agent', 'admin'])
def export_csv():
    report_type = request.args.get('type', 'category').lower()
    return export_report_csv(report_type)

