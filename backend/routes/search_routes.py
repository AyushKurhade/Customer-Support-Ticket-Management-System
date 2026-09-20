from flask import Blueprint
from backend.utils.auth_middleware import login_required
from backend.controllers.search_controller import search_tickets

search_bp = Blueprint('search_bp', __name__, url_prefix='/api/search')

# Accessible to any logged in user (customer sees own tickets, agent/admin sees all)
search_bp.add_url_rule('/tickets', view_func=login_required(search_tickets), methods=['GET'])

