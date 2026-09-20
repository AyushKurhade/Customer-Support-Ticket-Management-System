from flask import jsonify
from backend.config.db import execute_query

def get_categories():
    """
    Fetches all master categories for ticket creation and filtering.
    """
    categories = execute_query(
        "SELECT category_id, category_name, description FROM Categories ORDER BY category_name ASC;"
    )
    return jsonify({'categories': categories}), 200

def get_priorities():
    """
    Fetches all master priorities with target SLA hours.
    """
    priorities = execute_query(
        "SELECT priority_id, priority_name, sla_hours FROM Priorities ORDER BY sla_hours ASC;"
    )
    return jsonify({'priorities': priorities}), 200

def get_statuses():
    """
    Fetches all ticket lifecycle statuses.
    """
    statuses = execute_query(
        "SELECT status_id, status_name, is_closed FROM Ticket_Status ORDER BY status_id ASC;"
    )
    return jsonify({'statuses': statuses}), 200
