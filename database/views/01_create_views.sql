-- =============================================================================
-- Script: 01_create_views.sql
-- Project: Customer Support Ticket Management System
-- Phase: 12 - Database Views Implementation
-- Purpose: Creates reusable virtual tables for active tickets, agent performance,
--          and customer ticket history.
-- =============================================================================

USE support_ticket_db;

-- -----------------------------------------------------------------------------
-- 1. View: vw_OpenTickets
-- Description: Unifies active tickets (Open & In Progress) with customer names,
--              categories, priority SLAs, assigned agents, and elapsed age in hours.
-- Purpose: Eliminates repeating 5-table joins across agent queues and dashboards.
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_OpenTickets;
CREATE VIEW vw_OpenTickets AS
SELECT 
    t.ticket_id,
    t.subject,
    t.description,
    c.user_id AS customer_id,
    c.name AS customer_name,
    c.email AS customer_email,
    cat.category_id,
    cat.category_name,
    p.priority_id,
    p.priority_name,
    p.sla_hours,
    s.status_id,
    s.status_name,
    t.assigned_agent_id,
    COALESCE(a.name, 'Unassigned') AS agent_name,
    COALESCE(a.email, 'N/A') AS agent_email,
    t.created_at,
    ROUND(TIMESTAMPDIFF(MINUTE, t.created_at, NOW()) / 60.0, 1) AS ticket_age_hours,
    CASE 
        WHEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) > p.sla_hours THEN 'SLA BREACHED'
        WHEN TIMESTAMPDIFF(HOUR, t.created_at, NOW()) > (p.sla_hours * 0.75) THEN 'SLA WARNING'
        ELSE 'WITHIN SLA'
    END AS sla_status
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
WHERE s.is_closed = FALSE;

-- -----------------------------------------------------------------------------
-- 2. View: vw_AgentTicketSummary
-- Description: Aggregates real-time performance and workload metrics per agent.
-- Purpose: Provides instant statistics for Admin Dashboard and workload reports.
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_AgentTicketSummary;
CREATE VIEW vw_AgentTicketSummary AS
SELECT 
    a.user_id AS agent_id,
    a.name AS agent_name,
    a.email AS agent_email,
    a.contact_number,
    COUNT(t.ticket_id) AS total_assigned,
    SUM(CASE WHEN s.status_name = 'In Progress' THEN 1 ELSE 0 END) AS active_in_progress,
    SUM(CASE WHEN s.status_name = 'Resolved' THEN 1 ELSE 0 END) AS resolved_count,
    SUM(CASE WHEN s.status_name = 'Closed' THEN 1 ELSE 0 END) AS closed_count,
    ROUND(COALESCE(AVG(TIMESTAMPDIFF(MINUTE, t.created_at, t.resolved_at) / 60.0), 0), 2) AS avg_resolution_hours
FROM Users a
LEFT JOIN Tickets t ON a.user_id = t.assigned_agent_id
LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE a.role = 'agent'
GROUP BY a.user_id, a.name, a.email, a.contact_number;

-- -----------------------------------------------------------------------------
-- 3. View: vw_CustomerTicketHistory
-- Description: Comprehensive ticket timeline for customers and detail screens,
--              including total comment count and latest activity timestamp.
-- Purpose: Shields customer portals from complex aggregation queries.
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_CustomerTicketHistory;
CREATE VIEW vw_CustomerTicketHistory AS
SELECT 
    t.ticket_id,
    t.customer_id,
    c.name AS customer_name,
    c.email AS customer_email,
    t.subject,
    cat.category_name,
    p.priority_name,
    s.status_name,
    s.is_closed,
    COALESCE(a.name, 'Unassigned') AS agent_name,
    t.created_at,
    t.updated_at,
    t.resolved_at,
    COUNT(tc.comment_id) AS total_comments,
    MAX(tc.created_at) AS last_comment_at
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
LEFT JOIN Ticket_Comments tc ON t.ticket_id = tc.ticket_id
GROUP BY 
    t.ticket_id, t.customer_id, c.name, c.email, t.subject, 
    cat.category_name, p.priority_name, s.status_name, s.is_closed,
    a.name, t.created_at, t.updated_at, t.resolved_at;
