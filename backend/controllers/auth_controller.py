import re
from flask import request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from backend.config.db import execute_single, execute_dml

EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def register_user():
    """
    Registers a new customer account.
    Enforces password hashing, email validation, and unique constraint check.
    """
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    contact = (data.get('contact_number') or '').strip()

    # Field validations
    if not name or len(name) < 2:
        return jsonify({'error': 'Full name must be at least 2 characters.'}), 400
    if not email or not re.match(EMAIL_REGEX, email):
        return jsonify({'error': 'A valid email address is required.'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long.'}), 400

    # Check for duplicate email
    existing = execute_single("SELECT user_id FROM Users WHERE email = %s;", (email,))
    if existing:
        return jsonify({'error': 'An account with this email already exists.'}), 409

    # Securely hash password using PBKDF2:SHA256
    pwd_hash = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        res = execute_dml(
            "INSERT INTO Users (name, email, password_hash, role, contact_number) VALUES (%s, %s, %s, 'customer', %s);",
            (name, email, pwd_hash, contact or None)
        )
        new_user_id = res['last_id']

        # Auto-login the customer into session
        session['user_id'] = new_user_id
        session['name'] = name
        session['email'] = email
        session['role'] = 'customer'

        return jsonify({
            'message': 'Registration successful.',
            'user': {
                'user_id': new_user_id,
                'name': name,
                'email': email,
                'role': 'customer'
            }
        }), 201

    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

def login_user():
    """
    Authenticates Customer, Agent, or Admin using email and password hash.
    Establishes server-side session.
    """
    data = request.get_json() or {}
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    # Fetch user row by email
    user = execute_single(
        "SELECT user_id, name, email, password_hash, role, contact_number FROM Users WHERE email = %s;",
        (email,)
    )

    if not user:
        return jsonify({'error': 'Invalid email or password.'}), 401

    # Verify password hash
    if not check_password_hash(user['password_hash'], password):
        return jsonify({'error': 'Invalid email or password.'}), 401

    # Store user identity in Flask session
    session['user_id'] = user['user_id']
    session['name'] = user['name']
    session['email'] = user['email']
    session['role'] = user['role']

    return jsonify({
        'message': 'Login successful.',
        'user': {
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'contact_number': user['contact_number']
        }
    }), 200

def logout_user():
    """
    Clears the current user session.
    """
    session.clear()
    return jsonify({'message': 'Logged out successfully.'}), 200

def get_current_user_profile():
    """
    Returns profile information of the currently authenticated user.
    """
    if 'user_id' not in session:
        return jsonify({'authenticated': False, 'user': None}), 200

    user = execute_single(
        "SELECT user_id, name, email, role, contact_number, created_at FROM Users WHERE user_id = %s;",
        (session['user_id'],)
    )

    if not user:
        session.clear()
        return jsonify({'authenticated': False, 'user': None}), 200

    return jsonify({
        'authenticated': True,
        'user': user
    }), 200

