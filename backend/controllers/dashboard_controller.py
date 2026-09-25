from flask import jsonify, session
from backend.config.db import execute_query, execute_single

def get_dashboard_statistics():
    """
    Computes real-time system metrics, aggregations, chart data, and agent summaries
    directly from the database for the Admin & Staff Dashboard.
    """
    # 1. Pipeline Summary KPI Counters
    kpi_sql = """
        SELECT 
            COUNT(t.ticket_id) AS total_tickets,
            SUM(CASE WHEN LOWER(s.status_name) = 'open' THEN 1 ELSE 0 END) AS open_tickets,
            SUM(CASE WHEN LOWER(s.status_name) = 'in progress' THEN 1 ELSE 0 END) AS in_progress_tickets,
            SUM(CASE WHEN LOWER(s.status_name) = 'resolved' THEN 1 ELSE 0 END) AS resolved_tickets,
            SUM(CASE WHEN LOWER(s.status_name) = 'closed' THEN 1 ELSE 0 END) AS closed_tickets,
            SUM(CASE WHEN t.assigned_agent_id IS NOT NULL THEN 1 ELSE 0 END) AS assigned_tickets,
            SUM(CASE WHEN t.assigned_agent_id IS NULL THEN 1 ELSE 0 END) AS unassigned_tickets,
            SUM(CASE WHEN s.is_closed = FALSE AND TIMESTAMPDIFF(HOUR, t.created_at, NOW()) > p.sla_hours THEN 1 ELSE 0 END) AS sla_breached_count
        FROM Tickets t
        JOIN Ticket_Status s ON t.status_id = s.status_id
        JOIN Priorities p ON t.priority_id = p.priority_id;
    """
    kpis = execute_single(kpi_sql) or {
        'total_tickets': 0, 'open_tickets': 0, 'in_progress_tickets': 0,
        'resolved_tickets': 0, 'closed_tickets': 0, 'assigned_tickets': 0,
        'unassigned_tickets': 0, 'sla_breached_count': 0
    }

    agent_id = session.get('user_id')
    agent_kpis = {}
    if agent_id:
        agent_kpi_sql = """
            SELECT 
                SUM(CASE WHEN t.assigned_agent_id = %s THEN 1 ELSE 0 END) AS my_assigned_tickets,
                SUM(CASE WHEN t.assigned_agent_id = %s AND LOWER(s.status_name) = 'in progress' THEN 1 ELSE 0 END) AS my_in_progress_tickets,
                SUM(CASE WHEN t.assigned_agent_id = %s AND LOWER(s.status_name) IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS my_resolved_tickets
            FROM Tickets t
            JOIN Ticket_Status s ON t.status_id = s.status_id;
        """
        agent_kpis = execute_single(agent_kpi_sql, (agent_id, agent_id, agent_id)) or {}

    # 2. Average Resolution Time
    avg_sql = """
        SELECT 
            ROUND(COALESCE(AVG(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 0), 2) AS avg_resolution_hours,
            ROUND(COALESCE(MIN(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 0), 2) AS min_resolution_hours,
            ROUND(COALESCE(MAX(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 0), 2) AS max_resolution_hours,
            COUNT(ticket_id) AS resolved_count
        FROM Tickets
        WHERE resolved_at IS NOT NULL;
    """
    res_stats = execute_single(avg_sql) or {'avg_resolution_hours': 0, 'min_resolution_hours': 0, 'max_resolution_hours': 0, 'resolved_count': 0}

    # 3. Chart 1: Tickets by Category (Using LEFT JOIN so 0-count categories are included)
    cat_sql = """
        SELECT 
            cat.category_id,
            cat.category_name,
            COUNT(t.ticket_id) AS ticket_count
        FROM Categories cat
        LEFT JOIN Tickets t ON cat.category_id = t.category_id
        GROUP BY cat.category_id, cat.category_name
        ORDER BY ticket_count DESC, cat.category_name ASC;
    """
    by_category = execute_query(cat_sql)

    # 4. Chart 2: Tickets by Priority
    pri_sql = """
        SELECT 
            p.priority_id,
            p.priority_name,
            p.sla_hours,
            COUNT(t.ticket_id) AS ticket_count
        FROM Priorities p
        LEFT JOIN Tickets t ON p.priority_id = t.priority_id
        GROUP BY p.priority_id, p.priority_name, p.sla_hours
        ORDER BY p.sla_hours ASC;
    """
    by_priority = execute_query(pri_sql)

    # 5. Chart 3: Tickets by Status
    status_sql = """
        SELECT 
            s.status_id,
            s.status_name,
            COUNT(t.ticket_id) AS ticket_count
        FROM Ticket_Status s
        LEFT JOIN Tickets t ON s.status_id = t.status_id
        GROUP BY s.status_id, s.status_name
        ORDER BY s.status_id ASC;
    """
    by_status = execute_query(status_sql)

    # 6. Chart 4: Monthly Ticket Volume Trend
    monthly_sql = """
        SELECT 
            DATE_FORMAT(t.created_at, %s) AS month_key,
            DATE_FORMAT(t.created_at, %s) AS month_label,
            COUNT(t.ticket_id) AS ticket_count
        FROM Tickets t
        GROUP BY month_key, month_label
        ORDER BY month_key ASC
        LIMIT 12;
    """
    by_month = execute_query(monthly_sql, ('%Y-%m', '%b %Y'))

    # 7. Agent Performance Summary (Directly querying Database View vw_AgentTicketSummary)
    agent_summary = execute_query("SELECT * FROM vw_AgentTicketSummary ORDER BY total_assigned DESC;")

    # 8. Recent 5 Tickets Feed
    recent_sql = """
        SELECT 
            t.ticket_id,
            c.name AS customer_name,
            cat.category_name,
            p.priority_name,
            s.status_name,
            COALESCE(a.name, 'Unassigned') AS agent_name,
            t.subject,
            t.created_at
        FROM Tickets t
        JOIN Users c ON t.customer_id = c.user_id
        JOIN Categories cat ON t.category_id = cat.category_id
        JOIN Priorities p ON t.priority_id = p.priority_id
        JOIN Ticket_Status s ON t.status_id = s.status_id
        LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
        ORDER BY t.created_at DESC
        LIMIT 5;
    """
    recent_tickets = execute_query(recent_sql)

    return jsonify({
        'kpis': {
            'total_tickets': int(kpis.get('total_tickets') or 0),
            'open_tickets': int(kpis.get('open_tickets') or 0),
            'in_progress_tickets': int(kpis.get('in_progress_tickets') or 0),
            'resolved_tickets': int(kpis.get('resolved_tickets') or 0),
            'closed_tickets': int(kpis.get('closed_tickets') or 0),
            'assigned_tickets': int(kpis.get('assigned_tickets') or 0),
            'unassigned_tickets': int(kpis.get('unassigned_tickets') or 0),
            'sla_breached_count': int(kpis.get('sla_breached_count') or 0),
            'my_assigned_tickets': int(agent_kpis.get('my_assigned_tickets') or 0),
            'my_in_progress_tickets': int(agent_kpis.get('my_in_progress_tickets') or 0),
            'my_resolved_tickets': int(agent_kpis.get('my_resolved_tickets') or 0),
            'avg_resolution_hours': float(res_stats.get('avg_resolution_hours') or 0),
            'min_resolution_hours': float(res_stats.get('min_resolution_hours') or 0),
            'max_resolution_hours': float(res_stats.get('max_resolution_hours') or 0),
            'total_resolved': int(res_stats.get('resolved_count') or 0)
        },
        'charts': {
            'by_category': by_category,
            'by_priority': by_priority,
            'by_status': by_status,
            'by_month': by_month
        },
        'agent_summary': agent_summary,
        'recent_tickets': recent_tickets
    }), 200
