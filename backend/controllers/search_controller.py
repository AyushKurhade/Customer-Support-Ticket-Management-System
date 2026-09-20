from datetime import datetime, timedelta
from flask import request, jsonify, session
from backend.config.db import execute_query, execute_single

def search_tickets():
    """
    Advanced Multi-Criteria Search & Filtering Engine.
    Supports simultaneous combining of:
    - Text search (ticket_id, subject, description, customer name/email, agent name)
    - Exact filters (category, priority, status, assigned agent)
    - SLA compliance status (via fn_GetSLAStatus)
    - Date ranges (start_date, end_date, or presets)
    - Dynamic sorting and pagination
    - Role-based scoping (Customers automatically restricted to their own tickets)
    """
    user_id = session.get('user_id')
    user_role = session.get('role')

    # Query Parameters
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id')
    priority_id = request.args.get('priority_id')
    status_id = request.args.get('status_id')
    agent_id = request.args.get('agent_id')
    unassigned = request.args.get('unassigned', '').lower() in ('true', '1')
    sla_filter = request.args.get('sla_status', '').strip().upper()
    
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    preset_date = request.args.get('date_preset', '').strip().lower()

    sort_by = request.args.get('sort_by', 'created_at').strip().lower()
    order = request.args.get('order', 'desc').strip().lower()
    page = max(int(request.args.get('page', 1)), 1)
    limit = min(max(int(request.args.get('limit', 20)), 1), 100)
    offset = (page - 1) * limit

    # Base query
    where_clauses = ["1=1"]
    params = []

    # 1. Role-based scoping (Customers only see their own tickets)
    if user_role == 'customer':
        where_clauses.append("t.customer_id = %s")
        params.append(user_id)

    # 2. Text Search across multiple dimensions
    if q:
        text_clause = """
            (t.subject LIKE %s 
             OR t.description LIKE %s 
             OR c.name LIKE %s 
             OR c.email LIKE %s 
             OR a.name LIKE %s 
             OR cat.category_name LIKE %s
        """
        search_term = f"%{q}%"
        params.extend([search_term, search_term, search_term, search_term, search_term, search_term])
        
        # If user typed a numeric ID, search exact ticket_id
        if q.isdigit():
            text_clause += " OR t.ticket_id = %s"
            params.append(int(q))
            
        text_clause += ")"
        where_clauses.append(text_clause)

    # 3. Categorical Filters
    if category_id:
        where_clauses.append("t.category_id = %s")
        params.append(category_id)

    if priority_id:
        where_clauses.append("t.priority_id = %s")
        params.append(priority_id)

    if status_id:
        where_clauses.append("t.status_id = %s")
        params.append(status_id)

    # 4. Agent Assignment Filter
    if unassigned:
        where_clauses.append("t.assigned_agent_id IS NULL")
    elif agent_id:
        where_clauses.append("t.assigned_agent_id = %s")
        params.append(agent_id)

    # 5. Date Range Filtering
    if preset_date == 'today':
        where_clauses.append("DATE(t.created_at) = CURDATE()")
    elif preset_date == 'last_7_days':
        where_clauses.append("t.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)")
    elif preset_date == 'last_30_days':
        where_clauses.append("t.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)")
    elif preset_date == 'this_month':
        where_clauses.append("MONTH(t.created_at) = MONTH(NOW()) AND YEAR(t.created_at) = YEAR(NOW())")
    else:
        if start_date:
            where_clauses.append("DATE(t.created_at) >= %s")
            params.append(start_date)
        if end_date:
            where_clauses.append("DATE(t.created_at) <= %s")
            params.append(end_date)

    # 6. SLA Filter (via stored function fn_GetSLAStatus with collation safety)
    if sla_filter:
        where_clauses.append("fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci = %s")
        params.append(sla_filter)

    where_sql = " AND ".join(where_clauses)

    # Sorting options
    valid_sorts = {
        'created_at': 't.created_at',
        'updated_at': 't.updated_at',
        'ticket_id': 't.ticket_id',
        'priority': 'p.sla_hours',
        'status': 's.status_id'
    }
    sort_column = valid_sorts.get(sort_by, 't.created_at')
    sort_direction = 'ASC' if order == 'asc' else 'DESC'

    # Count total matching rows
    count_sql = f"""
        SELECT COUNT(t.ticket_id) AS total_count
        FROM Tickets t
        JOIN Users c ON t.customer_id = c.user_id
        JOIN Categories cat ON t.category_id = cat.category_id
        JOIN Priorities p ON t.priority_id = p.priority_id
        JOIN Ticket_Status s ON t.status_id = s.status_id
        LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
        WHERE {where_sql};
    """
    total_result = execute_single(count_sql, tuple(params))
    total_count = total_result['total_count'] if total_result else 0

    # Data query
    data_sql = f"""
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
        WHERE {where_sql}
        ORDER BY {sort_column} {sort_direction}
        LIMIT %s OFFSET %s;
    """
    data_params = list(params)
    data_params.extend([limit, offset])

    tickets = execute_query(data_sql, tuple(data_params))

    return jsonify({
        'tickets': tickets,
        'pagination': {
            'total_count': total_count,
            'page': page,
            'limit': limit,
            'total_pages': (total_count + limit - 1) // limit if limit > 0 else 1
        },
        'applied_filters': {
            'q': q,
            'category_id': category_id,
            'priority_id': priority_id,
            'status_id': status_id,
            'agent_id': agent_id,
            'unassigned': unassigned,
            'sla_status': sla_filter,
            'start_date': start_date,
            'end_date': end_date,
            'date_preset': preset_date,
            'sort_by': sort_by,
            'order': order
        }
    }), 200
