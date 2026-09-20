from flask import request, jsonify, session
from backend.config.db import execute_query, execute_single, execute_dml

def create_ticket():
    """
    Submits a new support ticket on behalf of the authenticated customer.
    The database trigger automatically records the initial status history row.
    """
    customer_id = session.get('user_id')
    data = request.get_json() or {}

    subject = (data.get('subject') or '').strip()
    description = (data.get('description') or '').strip()
    category_id = data.get('category_id')
    priority_id = data.get('priority_id')

    # Validations
    if not subject or len(subject) < 5:
        return jsonify({'error': 'Subject must be at least 5 characters long.'}), 400
    if not description or len(description) < 10:
        return jsonify({'error': 'Description must be at least 10 characters long.'}), 400
    if not category_id:
        return jsonify({'error': 'Category is required.'}), 400
    if not priority_id:
        return jsonify({'error': 'Priority is required.'}), 400

    # Verify category and priority exist
    cat = execute_single("SELECT category_id FROM Categories WHERE category_id = %s;", (category_id,))
    if not cat:
        return jsonify({'error': 'Invalid category selected.'}), 400

    pri = execute_single("SELECT priority_id FROM Priorities WHERE priority_id = %s;", (priority_id,))
    if not pri:
        return jsonify({'error': 'Invalid priority selected.'}), 400

    # Default initial status is 'Open' (status_id = 1)
    status_row = execute_single("SELECT status_id FROM Ticket_Status WHERE status_name = 'Open';")
    open_status_id = status_row['status_id'] if status_row else 1

    try:
        sql = """
            INSERT INTO Tickets (customer_id, category_id, priority_id, status_id, subject, description)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        res = execute_dml(sql, (customer_id, category_id, priority_id, open_status_id, subject, description))
        new_ticket_id = res['last_id']

        return jsonify({
            'message': 'Support ticket created successfully.',
            'ticket': {
                'ticket_id': new_ticket_id,
                'customer_id': customer_id,
                'category_id': category_id,
                'priority_id': priority_id,
                'status_id': open_status_id,
                'subject': subject,
                'status': 'Open'
            }
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to create ticket: {str(e)}'}), 500

def get_my_tickets():
    """
    Returns all tickets submitted by the authenticated customer.
    Supports filtering by category, status, and search keyword.
    """
    customer_id = session.get('user_id')
    category_id = request.args.get('category_id')
    status_id = request.args.get('status_id')
    search = request.args.get('search', '').strip()

    sql = """
        SELECT 
            t.ticket_id,
            t.subject,
            t.description,
            cat.category_name,
            p.priority_name,
            p.sla_hours,
            s.status_id,
            s.status_name,
            s.is_closed,
            COALESCE(a.name, 'Unassigned') AS agent_name,
            t.created_at,
            t.updated_at,
            t.resolved_at,
            fn_GetSLAStatus(t.ticket_id) AS sla_status,
            fn_CalculateTicketAge(t.ticket_id) AS age_hours
        FROM Tickets t
        JOIN Categories cat ON t.category_id = cat.category_id
        JOIN Priorities p ON t.priority_id = p.priority_id
        JOIN Ticket_Status s ON t.status_id = s.status_id
        LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
        WHERE t.customer_id = %s
    """
    params = [customer_id]

    if category_id:
        sql += " AND t.category_id = %s"
        params.append(category_id)

    if status_id:
        sql += " AND t.status_id = %s"
        params.append(status_id)

    if search:
        sql += " AND (t.subject LIKE %s OR t.description LIKE %s OR t.ticket_id = %s)"
        params.extend([f"%{search}%", f"%{search}%", search if search.isdigit() else -1])

    sql += " ORDER BY t.created_at DESC;"

    tickets = execute_query(sql, tuple(params))
    return jsonify({'tickets': tickets, 'count': len(tickets)}), 200

def get_ticket_details(ticket_id):
    """
    Retrieves full details of a specific ticket, including public comments
    and status audit history.
    """
    user_id = session.get('user_id')
    user_role = session.get('role')

    # Fetch ticket details
    sql_ticket = """
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

    # Security check: Customer can only view their own tickets
    if user_role == 'customer' and ticket['customer_id'] != user_id:
        return jsonify({'error': 'Access denied: You can only view your own tickets.'}), 403

    # Fetch comments (customers see only public comments)
    if user_role == 'customer':
        sql_comments = """
            SELECT 
                tc.comment_id,
                tc.user_id,
                u.name AS commenter_name,
                u.role AS commenter_role,
                tc.comment_text,
                tc.created_at
            FROM Ticket_Comments tc
            JOIN Users u ON tc.user_id = u.user_id
            WHERE tc.ticket_id = %s AND tc.is_internal = FALSE
            ORDER BY tc.created_at ASC;
        """
    else:
        # Agents & Admins also see internal notes
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

    # Fetch status change history (populated by DB triggers)
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

def add_ticket_comment(ticket_id):
    """
    Adds a customer comment to an active ticket.
    """
    customer_id = session.get('user_id')
    user_role = session.get('role')
    data = request.get_json() or {}
    comment_text = (data.get('comment_text') or '').strip()

    if not comment_text:
        return jsonify({'error': 'Comment message cannot be empty.'}), 400

    # Verify ticket ownership if customer
    ticket = execute_single("SELECT customer_id, status_id FROM Tickets WHERE ticket_id = %s;", (ticket_id,))
    if not ticket:
        return jsonify({'error': 'Ticket not found.'}), 404

    if user_role == 'customer' and ticket['customer_id'] != customer_id:
        return jsonify({'error': 'Access denied: You can only comment on your own tickets.'}), 403

    try:
        sql = """
            INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal)
            VALUES (%s, %s, %s, FALSE);
        """
        res = execute_dml(sql, (ticket_id, customer_id, comment_text))
        
        # Touch updated_at on ticket
        execute_dml("UPDATE Tickets SET updated_at = NOW() WHERE ticket_id = %s;", (ticket_id,))

        return jsonify({
            'message': 'Comment added successfully.',
            'comment_id': res['last_id']
        }), 201

    except Exception as e:
        return jsonify({'error': f'Failed to add comment: {str(e)}'}), 500

def close_my_ticket(ticket_id):
    """
    Allows a customer to confirm resolution and close their ticket.
    Database trigger automatically records status transition to 'Closed'.
    """
    customer_id = session.get('user_id')
    user_role = session.get('role')

    ticket = execute_single("SELECT customer_id, status_id FROM Tickets WHERE ticket_id = %s;", (ticket_id,))
    if not ticket:
        return jsonify({'error': 'Ticket not found.'}), 404

    if user_role == 'customer' and ticket['customer_id'] != customer_id:
        return jsonify({'error': 'Access denied: You can only close your own tickets.'}), 403

    status_row = execute_single("SELECT status_id FROM Ticket_Status WHERE status_name = 'Closed';")
    closed_status_id = status_row['status_id'] if status_row else 4

    try:
        execute_dml("UPDATE Tickets SET status_id = %s WHERE ticket_id = %s;", (closed_status_id, ticket_id))
        return jsonify({'message': 'Ticket closed successfully.'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to close ticket: {str(e)}'}), 500

