from flask import Blueprint
from backend.controllers.auth_controller import (
    register_user,
    login_user,
    logout_user,
    get_current_user_profile
)

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/api/auth')

auth_bp.add_url_rule('/register', view_func=register_user, methods=['POST'])
auth_bp.add_url_rule('/login', view_func=login_user, methods=['POST'])
auth_bp.add_url_rule('/logout', view_func=logout_user, methods=['POST'])
auth_bp.add_url_rule('/me', view_func=get_current_user_profile, methods=['GET'])
