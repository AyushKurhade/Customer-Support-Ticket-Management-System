from flask import Blueprint
from backend.utils.auth_middleware import role_required
from backend.controllers.admin_controller import (
    get_all_users,
    create_staff_user,
    get_all_tickets,
    assign_ticket_to_agent,
    change_ticket_priority,
    create_category,
    update_priority_sla
)

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')

# All admin routes require role 'admin'
admin_bp.add_url_rule('/users', view_func=role_required(['admin'])(get_all_users), methods=['GET'])
admin_bp.add_url_rule('/users', view_func=role_required(['admin'])(create_staff_user), methods=['POST'])
admin_bp.add_url_rule('/tickets', view_func=role_required(['admin'])(get_all_tickets), methods=['GET'])
admin_bp.add_url_rule('/tickets/<int:ticket_id>/assign', view_func=role_required(['admin'])(assign_ticket_to_agent), methods=['POST'])
admin_bp.add_url_rule('/tickets/<int:ticket_id>/priority', view_func=role_required(['admin'])(change_ticket_priority), methods=['PUT'])
admin_bp.add_url_rule('/categories', view_func=role_required(['admin'])(create_category), methods=['POST'])
admin_bp.add_url_rule('/priorities/<int:priority_id>', view_func=role_required(['admin'])(update_priority_sla), methods=['PUT'])
