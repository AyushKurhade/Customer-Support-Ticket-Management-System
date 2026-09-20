import io
import csv
from flask import jsonify, Response
from backend.config.db import execute_query

def get_category_report():
    """
    Detailed Category Report:
    Aggregates ticket counts, active vs resolved, SLA breaches, and average resolution hours.
    """
    sql = """
        SELECT 
            c.category_id,
            c.category_name,
            COUNT(t.ticket_id) AS total_tickets,
            SUM(CASE WHEN s.status_name IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS active_tickets,
            SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
            ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
            SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets
        FROM Categories c
        LEFT JOIN Tickets t ON c.category_id = t.category_id
        LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
        GROUP BY c.category_id, c.category_name
        ORDER BY total_tickets DESC;
    """
    results = execute_query(sql)
    
    # Calculate overall summary
    total_tickets = sum(r['total_tickets'] for r in results)
    total_active = sum(r['active_tickets'] for r in results)
    total_resolved = sum(r['resolved_tickets'] for r in results)
    total_breached = sum(r['breached_tickets'] for r in results)
    
    return jsonify({
        'summary': {
            'total_tickets': total_tickets,
            'active_tickets': total_active,
            'resolved_tickets': total_resolved,
            'breached_tickets': total_breached
        },
        'report_data': results
    }), 200

def get_status_report():
    """
    Lifecycle & Status Distribution Report:
    Computes ticket counts, system percentage, and oldest unresolved ticket age per status.
    """
    sql = """
        SELECT 
            s.status_id,
            s.status_name,
            COUNT(t.ticket_id) AS total_tickets,
            ROUND(COUNT(t.ticket_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM Tickets), 0), 2) AS percentage,
            MAX(CASE WHEN s.status_name NOT IN ('Resolved', 'Closed') THEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) ELSE NULL END) AS oldest_ticket_hours
        FROM Ticket_Status s
        LEFT JOIN Tickets t ON s.status_id = t.status_id
        GROUP BY s.status_id, s.status_name
        ORDER BY s.status_id ASC;
    """
    results = execute_query(sql)
    return jsonify({
        'report_data': results
    }), 200

def get_priority_report():
    """
    Priority & SLA Compliance Report:
    Evaluates SLA performance targets against actual resolution averages.
    """
    sql = """
        SELECT 
            p.priority_id,
            p.priority_name,
            p.sla_hours,
            COUNT(t.ticket_id) AS total_tickets,
            SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
            ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
            SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets,
            ROUND(
                (COUNT(t.ticket_id) - SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END)) * 100.0 / NULLIF(COUNT(t.ticket_id), 0), 
                2
            ) AS sla_compliance_pct
        FROM Priorities p
        LEFT JOIN Tickets t ON p.priority_id = t.priority_id
        LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
        GROUP BY p.priority_id, p.priority_name, p.sla_hours
        ORDER BY p.priority_id ASC;
    """
    results = execute_query(sql)
    return jsonify({
        'report_data': results
    }), 200

def get_agent_performance_report():
    """
    Agent Productivity & SLA Scorecard:
    Computes ticket assignments, backlog, resolution volume, and SLA compliance per agent.
    """
    sql = """
        SELECT 
            u.user_id,
            u.name AS agent_name,
            u.email,
            COUNT(t.ticket_id) AS assigned_tickets,
            SUM(CASE WHEN s.status_name IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS pending_tickets,
            SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
            ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
            SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets,
            ROUND(
                (COUNT(t.ticket_id) - SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END)) * 100.0 / NULLIF(COUNT(t.ticket_id), 0),
                2
            ) AS sla_compliance_pct
        FROM Users u
        LEFT JOIN Tickets t ON u.user_id = t.assigned_agent_id
        LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
        WHERE u.role = 'Agent'
        GROUP BY u.user_id, u.name, u.email
        ORDER BY resolved_tickets DESC;
    """
    results = execute_query(sql)
    return jsonify({
        'report_data': results
    }), 200

def get_resolution_time_analysis():
    """
    Ticket Resolution Time Analytics & Bucket Breakdown:
    Categorizes resolved tickets into time brackets (<4h, 4-24h, 24-48h, >48h) and lists recent resolutions.
    """
    # 1. Bucket distribution
    buckets_sql = """
        SELECT 
            SUM(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) < 4 THEN 1 ELSE 0 END) AS under_4_hours,
            SUM(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) >= 4 AND TIMESTAMPDIFF(HOUR, created_at, resolved_at) < 24 THEN 1 ELSE 0 END) AS hours_4_to_24,
            SUM(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) >= 24 AND TIMESTAMPDIFF(HOUR, created_at, resolved_at) < 48 THEN 1 ELSE 0 END) AS hours_24_to_48,
            SUM(CASE WHEN TIMESTAMPDIFF(HOUR, created_at, resolved_at) >= 48 THEN 1 ELSE 0 END) AS over_48_hours,
            ROUND(AVG(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 2) AS overall_avg_hours,
            COUNT(ticket_id) AS total_resolved
        FROM Tickets
        WHERE resolved_at IS NOT NULL;
    """
    buckets = execute_query(buckets_sql)
    distribution = buckets[0] if buckets else {}

    # 2. Detailed resolution log
    details_sql = """
        SELECT 
            t.ticket_id,
            t.subject,
            c.category_name,
            p.priority_name,
            u_cust.name AS customer_name,
            COALESCE(u_agent.name, 'Unassigned') AS agent_name,
            t.created_at,
            t.resolved_at,
            ROUND(TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0, 2) AS resolution_hours,
            p.sla_hours,
            fn_GetSLAStatus(t.ticket_id) AS sla_status
        FROM Tickets t
        JOIN Categories c ON t.category_id = c.category_id
        JOIN Priorities p ON t.priority_id = p.priority_id
        JOIN Users u_cust ON t.customer_id = u_cust.user_id
        LEFT JOIN Users u_agent ON t.assigned_agent_id = u_agent.user_id
        WHERE t.resolved_at IS NOT NULL
        ORDER BY t.resolved_at DESC
        LIMIT 50;
    """
    details = execute_query(details_sql)

    return jsonify({
        'distribution': distribution,
        'resolved_tickets': details
    }), 200

def export_report_csv(report_type):
    """
    Generates dynamic CSV file download for any requested analytical report.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    if report_type == 'category':
        data = execute_query("""
            SELECT c.category_name, COUNT(t.ticket_id) AS total_tickets,
                   SUM(CASE WHEN s.status_name IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS active_tickets,
                   SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
                   ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
                   SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets
            FROM Categories c
            LEFT JOIN Tickets t ON c.category_id = t.category_id
            LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
            GROUP BY c.category_id, c.category_name
            ORDER BY total_tickets DESC;
        """)
        writer.writerow(['Category Name', 'Total Tickets', 'Active Tickets', 'Resolved Tickets', 'Avg Resolution (Hours)', 'Breached Tickets'])
        for r in data:
            writer.writerow([r['category_name'], r['total_tickets'], r['active_tickets'], r['resolved_tickets'], r['avg_resolution_hours'] or 0, r['breached_tickets']])

    elif report_type == 'status':
        data = execute_query("""
            SELECT s.status_name, COUNT(t.ticket_id) AS total_tickets,
                   ROUND(COUNT(t.ticket_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM Tickets), 0), 2) AS percentage,
                   MAX(CASE WHEN s.status_name NOT IN ('Resolved', 'Closed') THEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) ELSE NULL END) AS oldest_ticket_hours
            FROM Ticket_Status s
            LEFT JOIN Tickets t ON s.status_id = t.status_id
            GROUP BY s.status_id, s.status_name;
        """)
        writer.writerow(['Status Name', 'Total Tickets', 'Percentage (%)', 'Oldest Active Ticket (Hours)'])
        for r in data:
            writer.writerow([r['status_name'], r['total_tickets'], r['percentage'] or 0, r['oldest_ticket_hours'] or 0])

    elif report_type == 'priority':
        data = execute_query("""
            SELECT p.priority_name, p.sla_hours, COUNT(t.ticket_id) AS total_tickets,
                   SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
                   ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
                   SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets,
                   ROUND((COUNT(t.ticket_id) - SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END)) * 100.0 / NULLIF(COUNT(t.ticket_id), 0), 2) AS sla_compliance_pct
            FROM Priorities p
            LEFT JOIN Tickets t ON p.priority_id = t.priority_id
            LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
            GROUP BY p.priority_id, p.priority_name, p.sla_hours;
        """)
        writer.writerow(['Priority Name', 'SLA Target (Hours)', 'Total Tickets', 'Resolved Tickets', 'Avg Resolution (Hours)', 'Breached Tickets', 'SLA Compliance (%)'])
        for r in data:
            writer.writerow([r['priority_name'], r['sla_hours'], r['total_tickets'], r['resolved_tickets'], r['avg_resolution_hours'] or 0, r['breached_tickets'], r['sla_compliance_pct'] or 100])

    elif report_type == 'agents':
        data = execute_query("""
            SELECT u.name AS agent_name, u.email, COUNT(t.ticket_id) AS assigned_tickets,
                   SUM(CASE WHEN s.status_name IN ('Open', 'In Progress') THEN 1 ELSE 0 END) AS pending_tickets,
                   SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS resolved_tickets,
                   ROUND(AVG(CASE WHEN t.resolved_at IS NOT NULL THEN TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0 END), 2) AS avg_resolution_hours,
                   SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END) AS breached_tickets,
                   ROUND((COUNT(t.ticket_id) - SUM(CASE WHEN fn_GetSLAStatus(t.ticket_id) COLLATE utf8mb4_unicode_ci IN ('SLA BREACHED', 'RESOLVED LATE') THEN 1 ELSE 0 END)) * 100.0 / NULLIF(COUNT(t.ticket_id), 0), 2) AS sla_compliance_pct
            FROM Users u
            LEFT JOIN Tickets t ON u.user_id = t.assigned_agent_id
            LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
            WHERE u.role = 'Agent'
            GROUP BY u.user_id, u.name, u.email;
        """)
        writer.writerow(['Agent Name', 'Email', 'Assigned Tickets', 'Pending Tickets', 'Resolved Tickets', 'Avg Resolution (Hours)', 'Breached Tickets', 'SLA Compliance (%)'])
        for r in data:
            writer.writerow([r['agent_name'], r['email'], r['assigned_tickets'], r['pending_tickets'] or 0, r['resolved_tickets'] or 0, r['avg_resolution_hours'] or 0, r['breached_tickets'] or 0, r['sla_compliance_pct'] or 100])

    elif report_type == 'resolution':
        data = execute_query("""
            SELECT t.ticket_id, t.subject, c.category_name, p.priority_name, u_cust.name AS customer_name,
                   COALESCE(u_agent.name, 'Unassigned') AS agent_name, t.created_at, t.resolved_at,
                   ROUND(TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0, 2) AS resolution_hours,
                   p.sla_hours, fn_GetSLAStatus(t.ticket_id) AS sla_status
            FROM Tickets t
            JOIN Categories c ON t.category_id = c.category_id
            JOIN Priorities p ON t.priority_id = p.priority_id
            JOIN Users u_cust ON t.customer_id = u_cust.user_id
            LEFT JOIN Users u_agent ON t.assigned_agent_id = u_agent.user_id
            WHERE t.resolved_at IS NOT NULL
            ORDER BY t.resolved_at DESC;
        """)
        writer.writerow(['Ticket ID', 'Subject', 'Category', 'Priority', 'Customer', 'Agent', 'Created At', 'Resolved At', 'Resolution Time (Hours)', 'SLA Target (Hours)', 'SLA Status'])
        for r in data:
            writer.writerow([r['ticket_id'], r['subject'], r['category_name'], r['priority_name'], r['customer_name'], r['agent_name'], r['created_at'], r['resolved_at'], r['resolution_hours'], r['sla_hours'], r['sla_status']])
    else:
        return jsonify({'error': f"Unknown report type '{report_type}'"}), 400

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{report_type}.csv"}
    )
