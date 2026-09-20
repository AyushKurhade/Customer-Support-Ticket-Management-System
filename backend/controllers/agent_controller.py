from flask import request, jsonify, session
from backend.config.db import execute_query, execute_single, execute_dml

def get_assigned_tickets():
    """
    Returns all tickets currently assigned to the authenticated agent.
    Supports filtering by status, priority, category, and keyword search.
    Ordered by urgency (SLA hours ASC).
    """
    agent_id = session.get('user_id')
    status_id = request.args.get('status_id')
    priority_id = request.args.get('priority_id')
    category_id = request.args.get('category_id')
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
        WHERE t.assigned_agent_id = %s
    """
    params = [agent_id]

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
        sql += " AND (t.subject LIKE %s OR t.description LIKE %s OR c.name LIKE %s OR t.ticket_id = %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", search if search.isdigit() else -1])

    sql += " ORDER BY p.sla_hours ASC, t.created_at ASC;"

    tickets = execute_query(sql, tuple(params))
    return jsonify({'tickets': tickets, 'count': len(tickets)}), 200

def get_agent_ticket_details(ticket_id):
    """
    Retrieves full details of a ticket for an agent or admin,
    including both public messages AND internal notes.
    """
    sql_ticket = """
        SELECT 
            t.ticket_id,
            t.customer_id,
            c.name AS customer_name,
            c.email AS customer_email,
            c.contact_number AS customer_contact,
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
            fn_CalculateTicketAge(t.ticket_id) AS age_hours,
            fn_CalculateResolutionTime(t.ticket_id) AS resolution_hours
        FROM Tickets t
        JOIN Users c ON t.customer_id = c.user_id
        JOIN Categories cat ON t.category_id = cat.category_id
        JOIN Priorities p ON t.priority_id = p.priority_id
        JOIN Ticket_Status s ON t.status_id = s.status_id
        LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
        WHERE t.ticket_id = %s;
    """
    ticket = execute_single(sql_ticket, (ticket_id,))

    if not ticket:
        return jsonify({'error': 'Ticket not found.'}), 404

    # Agents and Admins see ALL comments (both public and internal)
    sql_comments = """
        SELECT 
            tc.comment_id,
            tc.user_id,
            u.name AS commenter_name,
            u.role AS commenter_role,
            tc.comment_text,
            tc.is_internal,
            tc.created_at
        FROM Ticket_Comments tc
        JOIN Users u ON tc.user_id = u.user_id
        WHERE tc.ticket_id = %s
        ORDER BY tc.created_at ASC;
    """
    comments = execute_query(sql_comments, (ticket_id,))

    # Status audit trail populated by database triggers
    sql_history = """
        SELECT 
            h.history_id,
            COALESCE(s_old.status_name, 'None') AS old_status,
            s_new.status_name AS new_status,
            COALESCE(u.name, 'System') AS changed_by_name,
            h.remarks,
            h.changed_at
        FROM Ticket_Status_History h
        LEFT JOIN Ticket_Status s_old ON h.old_status_id = s_old.status_id
        JOIN Ticket_Status s_new ON h.new_status_id = s_new.status_id
        LEFT JOIN Users u ON h.changed_by = u.user_id
        WHERE h.ticket_id = %s
        ORDER BY h.changed_at ASC, h.history_id ASC;
    """
    history = execute_query(sql_history, (ticket_id,))

    return jsonify({
        'ticket': ticket,
        'comments': comments,
        'status_history': history
    }), 200

def update_ticket_status(ticket_id):
    """
    Updates the status of a ticket (e.g. In Progress, Resolved).
    Database triggers automatically handle resolution timestamping and history logging.
    """
    data = request.get_json() or {}
    new_status_id = data.get('status_id')

    if not new_status_id:
        return jsonify({'error': 'status_id is required.'}), 400

    # Validate that status exists
    status_row = execute_single("SELECT status_id, status_name FROM Ticket_Status WHERE status_id = %s;", (new_status_id,))
    if not status_row:
        return jsonify({'error': 'Invalid status_id.'}), 400

    # Check ticket existence
    ticket = execute_single("SELECT ticket_id, status_id FROM Tickets WHERE ticket_id = %s;", (ticket_id,))
    if not ticket:
        return jsonify({'error': 'Ticket not found.'}), 404

    try:
        # Simple update: the BEFORE UPDATE trigger sets resolved_at if Resolved,
        # and the AFTER UPDATE trigger logs to Ticket_Status_History!
        execute_dml("UPDATE Tickets SET status_id = %s WHERE ticket_id = %s;", (new_status_id, ticket_id))

        return jsonify({
            'message': f"Ticket status successfully updated to '{status_row['status_name']}'.",
            'status_id': new_status_id,
            'status_name': status_row['status_name']
        }), 200

    except Exception as e:
        return jsonify({'error': f'Failed to update status: {str(e)}'}), 500

def resolve_ticket(ticket_id):
    """
    Direct endpoint to mark a ticket as Resolved.
    Optionally appends a resolution comment.
    """
    agent_id = session.get('user_id')
    data = request.get_json() or {}
    resolution_notes = (data.get('resolution_notes') or '').strip()

    status_row = execute_single("SELECT status_id FROM Ticket_Status WHERE status_name = 'Resolved';")
    resolved_status_id = status_row['status_id'] if status_row else 3

    try:
        # Update status (triggers take care of timestamp & history)
        execute_dml("UPDATE Tickets SET status_id = %s WHERE ticket_id = %s;", (resolved_status_id, ticket_id))

        # If resolution notes provided, append as public comment
        if resolution_notes:
            execute_dml(
                "INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal) VALUES (%s, %s, %s, FALSE);",
                (ticket_id, agent_id, f"Resolution: {resolution_notes}")
            )

        return jsonify({'message': 'Ticket marked as Resolved successfully.'}), 200

    except Exception as e:
        return jsonify({'error': f'Failed to resolve ticket: {str(e)}'}), 500

def add_agent_comment(ticket_id):
    """
    Adds a comment from an agent/admin, supporting internal notes (is_internal=True)
    or public replies to the customer (is_internal=False).
    """
    agent_id = session.get('user_id')
    data = request.get_json() or {}
    comment_text = (data.get('comment_text') or '').strip()
    is_internal = bool(data.get('is_internal', False))

    if not comment_text:
        return jsonify({'error': 'Comment text cannot be empty.'}), 400

    ticket = execute_single("SELECT ticket_id FROM Tickets WHERE ticket_id = %s;", (ticket_id,))
    if not ticket:
        return jsonify({'error': 'Ticket not found.'}), 404

    try:
        res = execute_dml(
            "INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal) VALUES (%s, %s, %s, %s);",
            (ticket_id, agent_id, comment_text, is_internal)
        )
        execute_dml("UPDATE Tickets SET updated_at = NOW() WHERE ticket_id = %s;", (ticket_id,))

        return jsonify({
            'message': 'Comment added successfully.',
            'comment_id': res['last_id'],
            'is_internal': is_internal
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to add comment: {str(e)}'}), 500

