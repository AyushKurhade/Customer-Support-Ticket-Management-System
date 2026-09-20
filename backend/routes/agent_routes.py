from flask import Blueprint
from backend.utils.auth_middleware import role_required
from backend.controllers.agent_controller import (
    get_assigned_tickets,
    get_agent_ticket_details,
    update_ticket_status,
    resolve_ticket,
    add_agent_comment,
    claim_ticket
)

agent_bp = Blueprint('agent_bp', __name__, url_prefix='/api/agent')

# All agent routes require role 'agent' or 'admin'
agent_bp.add_url_rule('/tickets', view_func=role_required(['agent', 'admin'])(get_assigned_tickets), methods=['GET'])
agent_bp.add_url_rule('/tickets/<int:ticket_id>', view_func=role_required(['agent', 'admin'])(get_agent_ticket_details), methods=['GET'])
agent_bp.add_url_rule('/tickets/<int:ticket_id>/status', view_func=role_required(['agent', 'admin'])(update_ticket_status), methods=['PUT'])
agent_bp.add_url_rule('/tickets/<int:ticket_id>/resolve', view_func=role_required(['agent', 'admin'])(resolve_ticket), methods=['POST'])
agent_bp.add_url_rule('/tickets/<int:ticket_id>/comments', view_func=role_required(['agent', 'admin'])(add_agent_comment), methods=['POST'])
agent_bp.add_url_rule('/tickets/<int:ticket_id>/claim', view_func=role_required(['agent', 'admin'])(claim_ticket), methods=['POST'])

