-- =============================================================================
-- Script: 02_advanced_queries.sql
-- Project: Customer Support Ticket Management System
-- Phase: 11 - SQL Queries, Relational Joins, Aggregations & Subqueries
-- =============================================================================

USE support_ticket_db;

-- -----------------------------------------------------------------------------
-- Query 1: Show all Open tickets
-- Concepts: SELECT, WHERE, INNER JOIN, ORDER BY
-- -----------------------------------------------------------------------------
SELECT 
    t.ticket_id,
    c.name AS customer_name,
    cat.category_name,
    p.priority_name,
    t.subject,
    t.created_at
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE s.status_name = 'Open'
ORDER BY p.sla_hours ASC, t.created_at ASC;

-- -----------------------------------------------------------------------------
-- Query 2: Show tickets belonging to a particular category ('Network')
-- Concepts: SELECT, WHERE, INNER JOIN
-- -----------------------------------------------------------------------------
SELECT 
    t.ticket_id,
    c.name AS customer_name,
    p.priority_name,
    s.status_name,
    t.subject,
    t.created_at
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE cat.category_name = 'Network'
ORDER BY t.created_at DESC;

-- -----------------------------------------------------------------------------
-- Query 3: Show tickets assigned to a specific agent ('sarah.agent@support.com')
-- Concepts: INNER JOIN, WHERE, ORDER BY
-- -----------------------------------------------------------------------------
SELECT 
    t.ticket_id,
    a.name AS agent_name,
    c.name AS customer_name,
    cat.category_name,
    p.priority_name,
    s.status_name,
    t.subject,
    t.created_at
FROM Tickets t
JOIN Users a ON t.assigned_agent_id = a.user_id
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE a.email = 'sarah.agent@support.com'
ORDER BY t.created_at DESC;

-- -----------------------------------------------------------------------------
-- Query 4: Count tickets by category
-- Concepts: GROUP BY, COUNT, LEFT JOIN, ORDER BY
-- -----------------------------------------------------------------------------
SELECT 
    cat.category_id,
    cat.category_name,
    COUNT(t.ticket_id) AS ticket_count
FROM Categories cat
LEFT JOIN Tickets t ON cat.category_id = t.category_id
GROUP BY cat.category_id, cat.category_name
ORDER BY ticket_count DESC, cat.category_name ASC;

-- -----------------------------------------------------------------------------
-- Query 5: Count tickets by priority with SLA specifications
-- Concepts: GROUP BY, COUNT, LEFT JOIN, ORDER BY
-- -----------------------------------------------------------------------------
SELECT 
    p.priority_id,
    p.priority_name,
    p.sla_hours,
    COUNT(t.ticket_id) AS ticket_count
FROM Priorities p
LEFT JOIN Tickets t ON p.priority_id = t.priority_id
GROUP BY p.priority_id, p.priority_name, p.sla_hours
ORDER BY p.sla_hours ASC;

-- -----------------------------------------------------------------------------
-- Query 6: Count tickets by status
-- Concepts: GROUP BY, COUNT, LEFT JOIN
-- -----------------------------------------------------------------------------
SELECT 
    s.status_id,
    s.status_name,
    COUNT(t.ticket_id) AS ticket_count
FROM Ticket_Status s
LEFT JOIN Tickets t ON s.status_id = t.status_id
GROUP BY s.status_id, s.status_name
ORDER BY s.status_id ASC;

-- -----------------------------------------------------------------------------
-- Query 7: Find average, minimum, and maximum resolution time in hours
-- Concepts: Aggregate functions (AVG, MIN, MAX), TIMESTAMPDIFF, ROUND, WHERE
-- -----------------------------------------------------------------------------
SELECT 
    ROUND(AVG(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 2) AS avg_resolution_hours,
    ROUND(MIN(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 2) AS min_resolution_hours,
    ROUND(MAX(TIMESTAMPDIFF(MINUTE, created_at, resolved_at) / 60.0), 2) AS max_resolution_hours,
    COUNT(ticket_id) AS total_resolved_tickets
FROM Tickets
WHERE resolved_at IS NOT NULL;

-- -----------------------------------------------------------------------------
-- Query 8: Find unresolved tickets (Open or In Progress)
-- Concepts: WHERE, IN, COALESCE, LEFT JOIN
-- -----------------------------------------------------------------------------
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
WHERE s.is_closed = FALSE AND s.status_name != 'Resolved'
ORDER BY p.sla_hours ASC, t.created_at ASC;

-- -----------------------------------------------------------------------------
-- Query 9: Find tickets created during a date range (Past 7 Days)
-- Concepts: Date-based queries, DATE_SUB, NOW(), INTERVAL, ORDER BY
-- -----------------------------------------------------------------------------
SELECT 
    t.ticket_id,
    t.subject,
    c.name AS customer_name,
    cat.category_name,
    p.priority_name,
    t.created_at
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
JOIN Priorities p ON t.priority_id = p.priority_id
WHERE t.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY t.created_at DESC;

-- -----------------------------------------------------------------------------
-- Query 10: Find customers with multiple tickets
-- Concepts: GROUP BY, HAVING, Aggregate COUNT, JOIN, ORDER BY
-- -----------------------------------------------------------------------------
SELECT 
    c.user_id,
    c.name AS customer_name,
    c.email,
    COUNT(t.ticket_id) AS total_tickets_submitted
FROM Users c
JOIN Tickets t ON c.user_id = t.customer_id
GROUP BY c.user_id, c.name, c.email
HAVING COUNT(t.ticket_id) > 1
ORDER BY total_tickets_submitted DESC;

-- -----------------------------------------------------------------------------
-- Query 11: Find agents and their assigned ticket counts
-- Concepts: LEFT JOIN, GROUP BY, Conditional Aggregation (SUM CASE), Role filter
-- -----------------------------------------------------------------------------
SELECT 
    a.user_id AS agent_id,
    a.name AS agent_name,
    a.email AS agent_email,
    COUNT(t.ticket_id) AS total_assigned_tickets,
    SUM(CASE WHEN s.status_name = 'In Progress' THEN 1 ELSE 0 END) AS active_in_progress,
    SUM(CASE WHEN s.status_name IN ('Resolved', 'Closed') THEN 1 ELSE 0 END) AS completed_tickets
FROM Users a
LEFT JOIN Tickets t ON a.user_id = t.assigned_agent_id
LEFT JOIN Ticket_Status s ON t.status_id = s.status_id
WHERE a.role = 'agent'
GROUP BY a.user_id, a.name, a.email
ORDER BY total_assigned_tickets DESC;

-- -----------------------------------------------------------------------------
-- Query 12: Find resolved tickets within a specific time period using a Subquery
-- Concepts: Subqueries (Nested SELECT), IN operator, Date filtering
-- -----------------------------------------------------------------------------
SELECT 
    t.ticket_id,
    c.name AS customer_name,
    cat.category_name,
    t.subject,
    t.resolved_at
FROM Tickets t
JOIN Users c ON t.customer_id = c.user_id
JOIN Categories cat ON t.category_id = cat.category_id
WHERE t.ticket_id IN (
    SELECT ticket_id 
    FROM Tickets 
    WHERE status_id IN (SELECT status_id FROM Ticket_Status WHERE status_name IN ('Resolved', 'Closed'))
      AND resolved_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
)
ORDER BY t.resolved_at DESC;
