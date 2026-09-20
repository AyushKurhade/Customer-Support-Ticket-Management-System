from flask import Blueprint
from backend.utils.auth_middleware import login_required
from backend.controllers.customer_controller import (
    create_ticket,
    get_my_tickets,
    get_ticket_details,
    add_ticket_comment,
    close_my_ticket
)

customer_bp = Blueprint('customer_bp', __name__, url_prefix='/api/customer')

customer_bp.add_url_rule('/tickets', view_func=login_required(create_ticket), methods=['POST'])
customer_bp.add_url_rule('/tickets', view_func=login_required(get_my_tickets), methods=['GET'])
customer_bp.add_url_rule('/tickets/<int:ticket_id>', view_func=login_required(get_ticket_details), methods=['GET'])
customer_bp.add_url_rule('/tickets/<int:ticket_id>/comments', view_func=login_required(add_ticket_comment), methods=['POST'])
customer_bp.add_url_rule('/tickets/<int:ticket_id>/close', view_func=login_required(close_my_ticket), methods=['POST'])
