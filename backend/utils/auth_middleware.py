from functools import wraps
from flask import session, jsonify

def login_required(f):
    """
    Decorator to protect routes requiring an active user session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required. Please log in.', 'status_code': 401}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """
    Decorator to restrict route access to specific roles (e.g. ['admin'], ['agent', 'admin']).
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return jsonify({'error': 'Authentication required. Please log in.', 'status_code': 401}), 401
            user_role = session.get('role')
            if user_role not in allowed_roles:
                return jsonify({
                    'error': f'Access denied. Required role: {allowed_roles}, your role: {user_role}',
                    'status_code': 403
                }), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

