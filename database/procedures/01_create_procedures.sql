-- =============================================================================
-- Script: 01_create_procedures.sql
-- Project: Customer Support Ticket Management System
-- Phase: 13 - Stored Procedures Implementation
-- Purpose: Encapsulates transactional business logic, parameter validation,
--          and procedural workflows at the database layer.
-- =============================================================================

USE support_ticket_db;

-- -----------------------------------------------------------------------------
-- 1. Procedure: sp_CreateTicket
-- Purpose: Safely creates a new support ticket with customer verification and
--          returns the newly generated ticket_id.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_CreateTicket;
DELIMITER //
CREATE PROCEDURE sp_CreateTicket (
    IN p_customer_id INT,
    IN p_category_id INT,
    IN p_priority_id INT,
    IN p_subject VARCHAR(150),
    IN p_description TEXT,
    OUT p_ticket_id INT
)
BEGIN
    DECLARE v_customer_exists INT DEFAULT 0;
    DECLARE v_open_status_id INT;

    -- Validate customer identity and role
    SELECT COUNT(*) INTO v_customer_exists 
    FROM Users 
    WHERE user_id = p_customer_id AND role = 'customer';

    IF v_customer_exists = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Validation Error: Invalid customer_id or user is not a customer.';
    END IF;

    -- Retrieve ID for initial 'Open' status
    SELECT status_id INTO v_open_status_id 
    FROM Ticket_Status 
    WHERE status_name = 'Open' 
    LIMIT 1;

    -- Insert ticket record
    INSERT INTO Tickets (
        customer_id, category_id, priority_id, status_id, 
        assigned_agent_id, subject, description
    ) VALUES (
        p_customer_id, p_category_id, p_priority_id, v_open_status_id, 
        NULL, p_subject, p_description
    );

    SET p_ticket_id = LAST_INSERT_ID();
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 2. Procedure: sp_AssignTicket
-- Purpose: Assigns an unassigned or active ticket to a qualified support agent,
--          optionally promoting status from 'Open' to 'In Progress'.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_AssignTicket;
DELIMITER //
CREATE PROCEDURE sp_AssignTicket (
    IN p_ticket_id INT,
    IN p_agent_id INT,
    IN p_assigned_by INT
)
BEGIN
    DECLARE v_agent_valid INT DEFAULT 0;
    DECLARE v_ticket_exists INT DEFAULT 0;
    DECLARE v_current_status INT;
    DECLARE v_open_status INT;
    DECLARE v_in_progress_status INT;

    -- Validate agent
    SELECT COUNT(*) INTO v_agent_valid 
    FROM Users 
    WHERE user_id = p_agent_id AND role = 'agent';

    IF v_agent_valid = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Validation Error: Assigned user does not exist or is not a support agent.';
    END IF;

    -- Check ticket existence and current status
    SELECT status_id INTO v_current_status 
    FROM Tickets 
    WHERE ticket_id = p_ticket_id;

    IF v_current_status IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Validation Error: Ticket ID does not exist.';
    END IF;

    -- Get status IDs
    SELECT status_id INTO v_open_status FROM Ticket_Status WHERE status_name = 'Open';
    SELECT status_id INTO v_in_progress_status FROM Ticket_Status WHERE status_name = 'In Progress';

    -- Assign agent and advance status if currently Open
    IF v_current_status = v_open_status THEN
        UPDATE Tickets 
        SET assigned_agent_id = p_agent_id,
            status_id = v_in_progress_status
        WHERE ticket_id = p_ticket_id;
    ELSE
        UPDATE Tickets 
        SET assigned_agent_id = p_agent_id
        WHERE ticket_id = p_ticket_id;
    END IF;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 3. Procedure: sp_UpdateTicketStatus
-- Purpose: Updates ticket status and automatically stamps resolved_at when moving
--          to 'Resolved'.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_UpdateTicketStatus;
DELIMITER //
CREATE PROCEDURE sp_UpdateTicketStatus (
    IN p_ticket_id INT,
    IN p_new_status_id INT,
    IN p_changed_by INT,
    IN p_remarks VARCHAR(255)
)
BEGIN
    DECLARE v_status_name VARCHAR(30);

    -- Validate new status exists
    SELECT status_name INTO v_status_name 
    FROM Ticket_Status 
    WHERE status_id = p_new_status_id;

    IF v_status_name IS NULL THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Validation Error: New status ID is invalid.';
    END IF;

    -- Update status and timestamp if resolved
    IF v_status_name = 'Resolved' THEN
        UPDATE Tickets 
        SET status_id = p_new_status_id,
            resolved_at = NOW()
        WHERE ticket_id = p_ticket_id;
    ELSE
        UPDATE Tickets 
        SET status_id = p_new_status_id
        WHERE ticket_id = p_ticket_id;
    END IF;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 4. Procedure: sp_AddTicketComment
-- Purpose: Appends an audit comment or internal note to a ticket thread.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_AddTicketComment;
DELIMITER //
CREATE PROCEDURE sp_AddTicketComment (
    IN p_ticket_id INT,
    IN p_user_id INT,
    IN p_comment_text TEXT,
    IN p_is_internal BOOLEAN,
    OUT p_comment_id INT
)
BEGIN
    DECLARE v_ticket_exists INT DEFAULT 0;

    SELECT COUNT(*) INTO v_ticket_exists 
    FROM Tickets 
    WHERE ticket_id = p_ticket_id;

    IF v_ticket_exists = 0 THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Validation Error: Ticket does not exist.';
    END IF;

    INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal)
    VALUES (p_ticket_id, p_user_id, p_comment_text, p_is_internal);

    SET p_comment_id = LAST_INSERT_ID();

    -- Touch parent ticket's updated_at timestamp
    UPDATE Tickets SET updated_at = NOW() WHERE ticket_id = p_ticket_id;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 5. Procedure: sp_GetCustomerTickets
-- Purpose: Returns all tickets submitted by a specific customer.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_GetCustomerTickets;
DELIMITER //
CREATE PROCEDURE sp_GetCustomerTickets (
    IN p_customer_id INT
)
BEGIN
    SELECT 
        t.ticket_id,
        t.subject,
        cat.category_name,
        p.priority_name,
        s.status_name,
        COALESCE(a.name, 'Unassigned') AS agent_name,
        t.created_at,
        t.resolved_at
    FROM Tickets t
    JOIN Categories cat ON t.category_id = cat.category_id
    JOIN Priorities p ON t.priority_id = p.priority_id
    JOIN Ticket_Status s ON t.status_id = s.status_id
    LEFT JOIN Users a ON t.assigned_agent_id = a.user_id
    WHERE t.customer_id = p_customer_id
    ORDER BY t.created_at DESC;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 6. Procedure: sp_GetAgentTickets
-- Purpose: Returns all tickets assigned to a specific agent with optional status filter.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_GetAgentTickets;
DELIMITER //
CREATE PROCEDURE sp_GetAgentTickets (
    IN p_agent_id INT,
    IN p_status_id INT
)
BEGIN
    SELECT 
        t.ticket_id,
        c.name AS customer_name,
        c.email AS customer_email,
        cat.category_name,
        p.priority_name,
        p.sla_hours,
        s.status_name,
        t.subject,
        t.created_at,
        ROUND(TIMESTAMPDIFF(MINUTE, t.created_at, NOW()) / 60.0, 1) AS age_hours
    FROM Tickets t
    JOIN Users c ON t.customer_id = c.user_id
    JOIN Categories cat ON t.category_id = cat.category_id
    JOIN Priorities p ON t.priority_id = p.priority_id
    JOIN Ticket_Status s ON t.status_id = s.status_id
    WHERE t.assigned_agent_id = p_agent_id
      AND (p_status_id IS NULL OR t.status_id = p_status_id)
    ORDER BY p.sla_hours ASC, t.created_at ASC;
END //
DELIMITER ;
