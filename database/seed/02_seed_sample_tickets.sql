-- =============================================================================
-- Script: 02_seed_sample_tickets.sql
-- Project: Customer Support Ticket Management System
-- Purpose: Populates additional realistic tickets and comments for SQL analysis
-- =============================================================================

USE support_ticket_db;

-- 1. Insert additional diverse tickets using subqueries for bulletproof foreign key resolution
INSERT INTO Tickets (customer_id, category_id, priority_id, status_id, assigned_agent_id, subject, description, created_at, updated_at, resolved_at)
VALUES
-- Ticket A: Software issue, Medium priority, Assigned to Agent John, Resolved
((SELECT user_id FROM Users WHERE email = 'bob@customer.com'),
 (SELECT category_id FROM Categories WHERE category_name = 'Software'),
 (SELECT priority_id FROM Priorities WHERE priority_name = 'Medium'),
 (SELECT status_id FROM Ticket_Status WHERE status_name = 'Resolved'),
 (SELECT user_id FROM Users WHERE email = 'john.agent@support.com'),
 'Excel crashes when opening large macro-enabled workbook', 
 'Financial report workbook closes unexpectedly with runtime error 1004.', 
 DATE_SUB(NOW(), INTERVAL 36 HOUR), DATE_SUB(NOW(), INTERVAL 12 HOUR), DATE_SUB(NOW(), INTERVAL 12 HOUR)),

-- Ticket B: Payment issue, High priority, Assigned to Agent Sarah, In Progress
((SELECT user_id FROM Users WHERE email = 'charlie@customer.com'),
 (SELECT category_id FROM Categories WHERE category_name = 'Payment'),
 (SELECT priority_id FROM Priorities WHERE priority_name = 'High'),
 (SELECT status_id FROM Ticket_Status WHERE status_name = 'In Progress'),
 (SELECT user_id FROM Users WHERE email = 'sarah.agent@support.com'),
 'Double charged for annual SaaS subscription', 
 'Credit card statement reflects duplicate debit of $499 on Sept 18.', 
 DATE_SUB(NOW(), INTERVAL 18 HOUR), NOW(), NULL),

-- Ticket C: Technical Issue, Critical priority, Assigned to Agent John, Open
((SELECT user_id FROM Users WHERE email = 'alice@customer.com'),
 (SELECT category_id FROM Categories WHERE category_name = 'Technical Issue'),
 (SELECT priority_id FROM Priorities WHERE priority_name = 'Critical'),
 (SELECT status_id FROM Ticket_Status WHERE status_name = 'Open'),
 (SELECT user_id FROM Users WHERE email = 'john.agent@support.com'),
 'VPN gateway timing out on remote connections', 
 'Remote staff cannot connect to corporate subnet via AnyConnect.', 
 DATE_SUB(NOW(), INTERVAL 4 HOUR), NOW(), NULL),

-- Ticket D: Account issue, Low priority, Unassigned, Open
((SELECT user_id FROM Users WHERE email = 'david@customer.com'),
 (SELECT category_id FROM Categories WHERE category_name = 'Account'),
 (SELECT priority_id FROM Priorities WHERE priority_name = 'Low'),
 (SELECT status_id FROM Ticket_Status WHERE status_name = 'Open'),
 NULL,
 'Request for shared team calendar access permissions', 
 'Need edit access added for marketing team Google Workspace calendar.', 
 DATE_SUB(NOW(), INTERVAL 2 DAY), NOW(), NULL),

-- Ticket E: Software issue, High priority, Assigned to Agent Sarah, Closed
((SELECT user_id FROM Users WHERE email = 'charlie@customer.com'),
 (SELECT category_id FROM Categories WHERE category_name = 'Software'),
 (SELECT priority_id FROM Priorities WHERE priority_name = 'High'),
 (SELECT status_id FROM Ticket_Status WHERE status_name = 'Closed'),
 (SELECT user_id FROM Users WHERE email = 'sarah.agent@support.com'),
 'Antivirus license expired alert showing on desktop', 
 'Symantec Endpoint Protection says license expired yesterday.', 
 DATE_SUB(NOW(), INTERVAL 5 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY), DATE_SUB(NOW(), INTERVAL 3 DAY)),

-- Ticket F: Hardware issue, Medium priority, Assigned to Agent John, Resolved
((SELECT user_id FROM Users WHERE email = 'david@customer.com'),
 (SELECT category_id FROM Categories WHERE category_name = 'Hardware'),
 (SELECT priority_id FROM Priorities WHERE priority_name = 'Medium'),
 (SELECT status_id FROM Ticket_Status WHERE status_name = 'Resolved'),
 (SELECT user_id FROM Users WHERE email = 'john.agent@support.com'),
 'Logitech wireless keyboard keys sticking', 
 'Spacebar and enter keys do not respond smoothly.', 
 DATE_SUB(NOW(), INTERVAL 24 HOUR), DATE_SUB(NOW(), INTERVAL 6 HOUR), DATE_SUB(NOW(), INTERVAL 6 HOUR)),

-- Ticket G: Network issue, Low priority, Unassigned, Open
((SELECT user_id FROM Users WHERE email = 'bob@customer.com'),
 (SELECT category_id FROM Categories WHERE category_name = 'Network'),
 (SELECT priority_id FROM Priorities WHERE priority_name = 'Low'),
 (SELECT status_id FROM Ticket_Status WHERE status_name = 'Open'),
 NULL,
 'Slow upload speeds when pushing git repositories', 
 'Branch push takes more than 10 minutes from office workstation.', 
 DATE_SUB(NOW(), INTERVAL 1 DAY), NOW(), NULL);

-- 2. Insert corresponding realistic comments for closed/resolved tickets
INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal)
VALUES
(1, (SELECT user_id FROM Users WHERE email = 'sarah.agent@support.com'), 'Configured 5GHz AP channel separation. Please test again.', FALSE),
(2, (SELECT user_id FROM Users WHERE email = 'sarah.agent@support.com'), 'Reissued password reset token and sent directly to registered email.', FALSE),
(3, (SELECT user_id FROM Users WHERE email = 'john.agent@support.com'), 'Scheduled hardware desk visit with replacement display cables.', FALSE);
