from flask import request, jsonify, session
from werkzeug.security import generate_password_hash
from backend.config.db import execute_query, execute_single, execute_dml, call_stored_procedure

def get_all_users():
    """
    Fetches all registered users (Customers, Agents, Admins).
    Supports filtering by role (?role=agent). Excludes password hashes for security.
    """
    role = request.args.get('role', '').strip().lower()
    sql = """
        SELECT 
            u.user_id,
            u.name,
            u.email,
            u.role,
            u.contact_number,
            u.created_at,
            COUNT(t.ticket_id) AS total_tickets
        FROM Users u
        LEFT JOIN Tickets t ON (u.role = 'customer' AND u.user_id = t.customer_id) 
                            OR (u.role = 'agent' AND u.user_id = t.assigned_agent_id)
    """
    params = []
    if role:
        sql += " WHERE u.role = %s"
        params.append(role)

    sql += " GROUP BY u.user_id, u.name, u.email, u.role, u.contact_number, u.created_at ORDER BY u.created_at DESC;"

    users = execute_query(sql, tuple(params))
    return jsonify({'users': users, 'count': len(users)}), 200

def create_staff_user():
    """
    Admin can provision new Support Agents or Administrators.
    """
    data = request.get_json() or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    role = (data.get('role') or '').strip().lower()
    contact = (data.get('contact_number') or '').strip()

    if not name or len(name) < 2:
        return jsonify({'error': 'Name must be at least 2 characters.'}), 400
    if not email or '@' not in email:
        return jsonify({'error': 'Valid email is required.'}), 400
    if not password or len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters.'}), 400
    if role not in ('agent', 'admin', 'customer'):
        return jsonify({'error': "Role must be 'agent', 'admin', or 'customer'."}), 400

    existing = execute_single("SELECT user_id FROM Users WHERE email = %s;", (email,))
    if existing:
        return jsonify({'error': 'An account with this email already exists.'}), 409

    pwd_hash = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        res = execute_dml(
            "INSERT INTO Users (name, email, password_hash, role, contact_number) VALUES (%s, %s, %s, %s, %s);",
            (name, email, pwd_hash, role, contact or None)
        )
        return jsonify({
            'message': f"User '{name}' provisioned successfully as '{role}'.",
            'user_id': res['last_id']
        }), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create user: {str(e)}'}), 500

def get_all_tickets():
    """
    Admin overview of all tickets across all customers and agents.
    Supports filters: status_id, priority_id, category_id, assigned_agent_id, unassigned_only.
    """
    status_id = request.args.get('status_id')
    priority_id = request.args.get('priority_id')
    category_id = request.args.get('category_id')
    agent_id = request.args.get('agent_id')
    unassigned_only = request.args.get('unassigned_only')
    search = request.args.get('search', '').strip()

    sql = """
        SELECT 
            t.ticket_id,
            t.customer_id,
            c.name AS customer_name,
            c.email AS customer_email,
            t.category_id,
            cat.category_name,
            t.priority_id,
            p.priority_name,
            p.sla_hours,
            t.status_id,
            s.status_name,
            s.is_closed,
            t.assigned_agent_id,
            COALESCE(a.name, 'Unassigned') AS agent_name,
            COALESCE(a.email, 'N/A') AS agent_email,
            t.subject,
            t.description,
            t.created_at,
            t.updated_at,
            t.resolved_at,
            fn_GetSLAStatus(t.ticket_id) AS sla_status,
            fn_CalculateTicketAge(t.ticket_id) AS age_hours
        FROM Tickets t
        JOIN Users c ON t.customer_id = c.user_id
        JOIN Categories cat ON t.category_id = cat.category_id
        JOIN Priorities p ON t.priority_id = p.priority_id
        JOIN Ticket_Status s ON t.status_id = s.status_id
        LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
        WHERE 1=1
    """
    params = []

    if unassigned_only and unassigned_only.lower() in ('true', '1'):
        sql += " AND t.assigned_agent_id IS NULL"
    elif agent_id:
        sql += " AND t.assigned_agent_id = %s"
        params.append(agent_id)

    if status_id:
        sql += " AND t.status_id = %s"
        params.append(status_id)

    if priority_id:
        sql += " AND t.priority_id = %s"
        params.append(priority_id)

    if category_id:
        sql += " AND t.category_id = %s"
        params.append(category_id)

    if search:
        sql += " AND (t.subject LIKE %s OR t.description LIKE %s OR c.name LIKE %s OR a.name LIKE %s OR t.ticket_id = %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", search if search.isdigit() else -1])

    sql += " ORDER BY t.created_at DESC;"

    tickets = execute_query(sql, tuple(params))
    return jsonify({'tickets': tickets, 'count': len(tickets)}), 200

def assign_ticket_to_agent(ticket_id):
    """
    Assigns or reassigns a ticket to a support agent using Stored Procedure sp_AssignTicket.
    If ticket was 'Open', sp_AssignTicket auto-advances status to 'In Progress'.
    """
    admin_id = session.get('user_id')
    data = request.get_json() or {}
    agent_id = data.get('agent_id')

    if not agent_id:
        return jsonify({'error': 'agent_id is required.'}), 400

    # Validate agent
    agent = execute_single("SELECT user_id, name, role FROM Users WHERE user_id = %s AND role = 'agent';", (agent_id,))
    if not agent:
        return jsonify({'error': 'Invalid agent_id. User must have role agent.'}), 400

    ticket = execute_single("SELECT ticket_id, status_id FROM Tickets WHERE ticket_id = %s;", (ticket_id,))
    if not ticket:
        return jsonify({'error': 'Ticket not found.'}), 404

    try:
        # Call Stored Procedure sp_AssignTicket
        call_stored_procedure('sp_AssignTicket', (ticket_id, agent_id, admin_id))

        # Add an internal audit comment
        execute_dml(
            "INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal) VALUES (%s, %s, %s, TRUE);",
            (ticket_id, admin_id, f"Ticket assigned to Agent {agent['name']} by Administrator.")
        )

        return jsonify({
            'message': f"Ticket #{ticket_id} successfully assigned to Agent {agent['name']}.",
            'ticket_id': ticket_id,
            'assigned_agent_id': agent_id,
            'agent_name': agent['name']
        }), 200

    except Exception as e:
        return jsonify({'error': f'Assignment failed: {str(e)}'}), 500

def change_ticket_priority(ticket_id):
    """
    Escalates or adjusts ticket priority with an internal audit remark.
    """
    admin_id = session.get('user_id')
    data = request.get_json() or {}
    priority_id = data.get('priority_id')
    remarks = (data.get('remarks') or '').strip()

    if not priority_id:
        return jsonify({'error': 'priority_id is required.'}), 400

    pri = execute_single("SELECT priority_id, priority_name, sla_hours FROM Priorities WHERE priority_id = %s;", (priority_id,))
    if not pri:
        return jsonify({'error': 'Invalid priority_id.'}), 400

    try:
        execute_dml("UPDATE Tickets SET priority_id = %s WHERE ticket_id = %s;", (priority_id, ticket_id))

        # Append internal escalation comment
        comment_msg = f"Priority adjusted to '{pri['priority_name']}' (SLA: {pri['sla_hours']}h)."
        if remarks:
            comment_msg += f" Reason: {remarks}"

        execute_dml(
            "INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal) VALUES (%s, %s, %s, TRUE);",
            (ticket_id, admin_id, comment_msg)
        )

        return jsonify({
            'message': f"Ticket priority updated to '{pri['priority_name']}'.",
            'priority_id': priority_id,
            'priority_name': pri['priority_name']
        }), 200

    except Exception as e:
        return jsonify({'error': f'Priority update failed: {str(e)}'}), 500

def create_category():
    """
    Creates a new IT service category in master data.
    """
    data = request.get_json() or {}
    name = (data.get('category_name') or '').strip()
    description = (data.get('description') or '').strip()

    if not name or len(name) < 2:
        return jsonify({'error': 'Category name must be at least 2 characters.'}), 400

    existing = execute_single("SELECT category_id FROM Categories WHERE category_name = %s;", (name,))
    if existing:
        return jsonify({'error': 'A category with this name already exists.'}), 409

    try:
        res = execute_dml(
            "INSERT INTO Categories (category_name, description) VALUES (%s, %s);",
            (name, description or None)
        )
        return jsonify({
            'message': f"Category '{name}' created successfully.",
            'category_id': res['last_id']
        }), 201
    except Exception as e:
        return jsonify({'error': f'Failed to create category: {str(e)}'}), 500

def update_priority_sla(priority_id):
    """
    Updates the SLA hours of an existing priority tier.
    Enforces the database CHECK constraint chk_priorities_sla (sla_hours > 0).
    """
    data = request.get_json() or {}
    sla_hours = data.get('sla_hours')

    if sla_hours is None or not isinstance(sla_hours, int) or sla_hours <= 0:
        return jsonify({'error': 'sla_hours must be a positive integer (> 0).'}), 400

    pri = execute_single("SELECT priority_id, priority_name FROM Priorities WHERE priority_id = %s;", (priority_id,))
    if not pri:
        return jsonify({'error': 'Priority not found.'}), 404

    try:
        execute_dml("UPDATE Priorities SET sla_hours = %s WHERE priority_id = %s;", (sla_hours, priority_id))
        return jsonify({
            'message': f"SLA for priority '{pri['priority_name']}' updated to {sla_hours} hours.",
            'priority_id': priority_id,
            'sla_hours': sla_hours
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update priority SLA: {str(e)}'}), 500
