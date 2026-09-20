-- =============================================================================
-- Script: 01_crud_operations.sql
-- Project: Customer Support Ticket Management System
-- Phase: 10 - CRUD Operations Testing & Referential Integrity Verification
-- =============================================================================

USE support_ticket_db;

-- =============================================================================
-- 1. CREATE / INSERT OPERATIONS
-- =============================================================================

-- 1.1 Insert a new customer
INSERT INTO Users (name, email, password_hash, role, contact_number)
VALUES ('David Miller', 'david@customer.com', 'pbkdf2:sha256:1000000$i9BnxsIFt1MTeepe$493f48408d3e011ea2ed0fd6889c862d8d82f22679a397bb0e9ca5ae0ff54653', 'customer', '+1-555-0204');

-- 1.2 Insert Ticket 1 (Customer Alice, Category: Network, Priority: High, Status: Open)
INSERT INTO Tickets (customer_id, category_id, priority_id, status_id, subject, description)
VALUES (
    4, 3, 3, 1,
    'WiFi drops repeatedly in Conference Room B',
    'Laptops disconnect from the 5GHz SSID every 15 minutes during team video calls.'
);

-- 1.3 Insert Ticket 2 (Customer Bob, Category: Account, Priority: Medium, Status: Open)
INSERT INTO Tickets (customer_id, category_id, priority_id, status_id, subject, description)
VALUES (
    5, 4, 2, 1,
    'Password reset link expired',
    'Cannot access the employee benefits portal because my reset token timed out.'
);

-- 1.4 Insert Ticket 3 (Customer Alice, Category: Hardware, Priority: Critical, Status: Open)
INSERT INTO Tickets (customer_id, category_id, priority_id, status_id, subject, description)
VALUES (
    4, 1, 4, 1,
    'Workstation dual monitor not turning on',
    'Both screens remain completely blank with no power LED indicator.'
);

-- 1.5 Insert Comments on Ticket 1
INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal)
VALUES 
(1, 2, 'Hi Alice, checking access point AP-04 log metrics for packet drops.', FALSE),
(1, 4, 'Thanks Sarah! We are currently in meeting room B on the 3rd floor.', FALSE),
(1, 2, 'Internal note: Suspect DHCP lease pool exhaustion on VLAN 20.', TRUE);

-- =============================================================================
-- 2. READ / SELECT OPERATIONS
-- =============================================================================

-- 2.1 Read all tickets with human-readable master references
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
ORDER BY t.ticket_id ASC;

-- 2.2 Read comments for Ticket 1 (public & internal)
SELECT 
    tc.comment_id,
    u.name AS commenter_name,
    u.role AS commenter_role,
    tc.comment_text,
    tc.is_internal,
    tc.created_at
FROM Ticket_Comments tc
JOIN Users u ON tc.user_id = u.user_id
WHERE tc.ticket_id = 1
ORDER BY tc.created_at ASC;

-- =============================================================================
-- 3. UPDATE OPERATIONS
-- =============================================================================

-- 3.1 Assign Ticket 1 to Agent Sarah (user_id = 2)
UPDATE Tickets 
SET assigned_agent_id = 2
WHERE ticket_id = 1;

-- 3.2 Update Status of Ticket 1 to 'In Progress' (status_id = 2)
UPDATE Tickets 
SET status_id = 2
WHERE ticket_id = 1;

-- 3.3 Resolve Ticket 2 by setting status to 'Resolved' and recording resolved_at
UPDATE Tickets 
SET status_id = 3,
    resolved_at = CURRENT_TIMESTAMP
WHERE ticket_id = 2;

-- =============================================================================
-- 4. DELETE & REFERENTIAL INTEGRITY TESTS
-- =============================================================================

-- 4.1 Create a temporary test ticket and comment to demonstrate CASCADE DELETE
INSERT INTO Tickets (customer_id, category_id, priority_id, status_id, subject, description)
VALUES (6, 7, 1, 1, 'Temporary test ticket for cascade deletion', 'To be deleted in test.');

-- Capture the created ticket's ID (assuming ticket_id = 4)
SET @temp_ticket_id = LAST_INSERT_ID();

INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text)
VALUES (@temp_ticket_id, 6, 'Temporary test comment for cascade deletion.');

-- Verify the test ticket and comment exist before deletion
SELECT ticket_id, subject FROM Tickets WHERE ticket_id = @temp_ticket_id;
SELECT comment_id, ticket_id, comment_text FROM Ticket_Comments WHERE ticket_id = @temp_ticket_id;

-- Now delete the parent ticket
DELETE FROM Tickets WHERE ticket_id = @temp_ticket_id;

-- Verify child comment was automatically deleted via ON DELETE CASCADE (should return 0 rows)
SELECT * FROM Ticket_Comments WHERE ticket_id = @temp_ticket_id;
