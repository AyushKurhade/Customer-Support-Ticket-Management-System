-- ========================================================
-- Complete Customer Support Ticket System Database Setup
-- ========================================================
CREATE DATABASE IF NOT EXISTS support_ticket_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE support_ticket_db;

-- >>> START: schema.sql <<<
-- =============================================================================
-- MASTER SCHEMA SCRIPT: schema.sql
-- Project: Customer Support Ticket Management System
-- Phases: 7 (Database Creation) & 8 (Constraints & Referential Integrity)
-- Storage Engine: InnoDB
-- =============================================================================

DROP DATABASE IF EXISTS support_ticket_db;
CREATE DATABASE support_ticket_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE support_ticket_db;

-- 1. Users Table
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    contact_number VARCHAR(20) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_users PRIMARY KEY (user_id),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT chk_users_role CHECK (role IN ('customer', 'agent', 'admin'))
) ENGINE=InnoDB;

-- 2. Categories Table
CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_categories PRIMARY KEY (category_id),
    CONSTRAINT uq_categories_name UNIQUE (category_name)
) ENGINE=InnoDB;

-- 3. Priorities Table
CREATE TABLE Priorities (
    priority_id INT AUTO_INCREMENT,
    priority_name VARCHAR(20) NOT NULL,
    sla_hours INT NOT NULL DEFAULT 24,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_priorities PRIMARY KEY (priority_id),
    CONSTRAINT uq_priorities_name UNIQUE (priority_name),
    CONSTRAINT chk_priorities_sla CHECK (sla_hours > 0)
) ENGINE=InnoDB;

-- 4. Ticket_Status Table
CREATE TABLE Ticket_Status (
    status_id INT AUTO_INCREMENT,
    status_name VARCHAR(30) NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_ticket_status PRIMARY KEY (status_id),
    CONSTRAINT uq_ticket_status_name UNIQUE (status_name)
) ENGINE=InnoDB;

-- 5. Tickets Table
CREATE TABLE Tickets (
    ticket_id INT AUTO_INCREMENT,
    customer_id INT NOT NULL,
    category_id INT NOT NULL,
    priority_id INT NOT NULL,
    status_id INT NOT NULL,
    assigned_agent_id INT NULL,
    subject VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    CONSTRAINT pk_tickets PRIMARY KEY (ticket_id),
    CONSTRAINT fk_tickets_customer FOREIGN KEY (customer_id) 
        REFERENCES Users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_tickets_category FOREIGN KEY (category_id) 
        REFERENCES Categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_tickets_priority FOREIGN KEY (priority_id) 
        REFERENCES Priorities(priority_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_tickets_status FOREIGN KEY (status_id) 
        REFERENCES Ticket_Status(status_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_tickets_agent FOREIGN KEY (assigned_agent_id) 
        REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 6. Ticket_Comments Table
CREATE TABLE Ticket_Comments (
    comment_id INT AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    user_id INT NOT NULL,
    comment_text TEXT NOT NULL,
    is_internal BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_ticket_comments PRIMARY KEY (comment_id),
    CONSTRAINT fk_comments_ticket FOREIGN KEY (ticket_id) 
        REFERENCES Tickets(ticket_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_comments_user FOREIGN KEY (user_id) 
        REFERENCES Users(user_id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB;

-- 7. Ticket_Status_History Table
CREATE TABLE Ticket_Status_History (
    history_id INT AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    old_status_id INT NULL,
    new_status_id INT NOT NULL,
    changed_by INT NULL,
    remarks VARCHAR(255) NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_ticket_status_history PRIMARY KEY (history_id),
    CONSTRAINT fk_history_ticket FOREIGN KEY (ticket_id) 
        REFERENCES Tickets(ticket_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_history_old_status FOREIGN KEY (old_status_id) 
        REFERENCES Ticket_Status(status_id) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_history_new_status FOREIGN KEY (new_status_id) 
        REFERENCES Ticket_Status(status_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_history_changed_by FOREIGN KEY (changed_by) 
        REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB;



-- >>> START: 01_seed_master_data.sql <<<
-- =============================================================================
-- Script: 01_seed_master_data.sql
-- Project: Customer Support Ticket Management System
-- Phase: 9 - Master Data Seeding
-- Purpose: Populates Categories, Priorities, Ticket_Status, and Initial Users
-- =============================================================================

USE support_ticket_db;

-- -----------------------------------------------------------------------------
-- 1. Seed Categories (Master Reference Data)
-- -----------------------------------------------------------------------------
INSERT INTO Categories (category_name, description) VALUES
('Hardware', 'Physical devices, workstations, monitors, peripherals, printers, and accessories'),
('Software', 'Operating systems, office suites, business applications, and software installation'),
('Network', 'WiFi connectivity, LAN access, VPN configuration, firewalls, and DNS lookup errors'),
('Account', 'User access credentials, password resets, account lockouts, and permissions'),
('Payment', 'Billing invoices, subscription renewals, charge disputes, and payment processing'),
('Technical Issue', 'System performance degradation, application freezes, unexpected crashes, and bugs'),
('Other', 'General IT inquiries, service requests, feedback, and miscellaneous issues')
ON DUPLICATE KEY UPDATE description = VALUES(description);

-- -----------------------------------------------------------------------------
-- 2. Seed Priorities (Master Reference Data with SLA Hours)
-- -----------------------------------------------------------------------------
INSERT INTO Priorities (priority_name, sla_hours) VALUES
('Low', 72),
('Medium', 48),
('High', 24),
('Critical', 4)
ON DUPLICATE KEY UPDATE sla_hours = VALUES(sla_hours);

-- -----------------------------------------------------------------------------
-- 3. Seed Ticket Statuses (Master Reference Data)
-- -----------------------------------------------------------------------------
INSERT INTO Ticket_Status (status_name, is_closed) VALUES
('Open', FALSE),
('In Progress', FALSE),
('Resolved', FALSE),
('Closed', TRUE)
ON DUPLICATE KEY UPDATE is_closed = VALUES(is_closed);

-- -----------------------------------------------------------------------------
-- 4. Seed Initial Users (Role-based testing accounts)
-- Password for all seed accounts: Password@123
-- Stored using PBKDF2:SHA256 standard password hash
-- -----------------------------------------------------------------------------
INSERT INTO Users (name, email, password_hash, role, contact_number) VALUES
('System Administrator', 'admin@support.com', 'pbkdf2:sha256:1000000$i9BnxsIFt1MTeepe$493f48408d3e011ea2ed0fd6889c862d8d82f22679a397bb0e9ca5ae0ff54653', 'admin', '+1-555-0100'),
('Sarah Jenkins (Agent)', 'sarah.agent@support.com', 'pbkdf2:sha256:1000000$i9BnxsIFt1MTeepe$493f48408d3e011ea2ed0fd6889c862d8d82f22679a397bb0e9ca5ae0ff54653', 'agent', '+1-555-0101'),
('John Davis (Agent)', 'john.agent@support.com', 'pbkdf2:sha256:1000000$i9BnxsIFt1MTeepe$493f48408d3e011ea2ed0fd6889c862d8d82f22679a397bb0e9ca5ae0ff54653', 'agent', '+1-555-0102'),
('Alice Morgan (Customer)', 'alice@customer.com', 'pbkdf2:sha256:1000000$i9BnxsIFt1MTeepe$493f48408d3e011ea2ed0fd6889c862d8d82f22679a397bb0e9ca5ae0ff54653', 'customer', '+1-555-0201'),
('Bob Martinez (Customer)', 'bob@customer.com', 'pbkdf2:sha256:1000000$i9BnxsIFt1MTeepe$493f48408d3e011ea2ed0fd6889c862d8d82f22679a397bb0e9ca5ae0ff54653', 'customer', '+1-555-0202'),
('Charlie Brown (Customer)', 'charlie@customer.com', 'pbkdf2:sha256:1000000$i9BnxsIFt1MTeepe$493f48408d3e011ea2ed0fd6889c862d8d82f22679a397bb0e9ca5ae0ff54653', 'customer', '+1-555-0203')
ON DUPLICATE KEY UPDATE name = VALUES(name);



-- >>> START: 01_create_views.sql <<<
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



-- >>> START: 01_create_functions.sql <<<
-- =============================================================================
-- Script: 01_create_functions.sql
-- Project: Customer Support Ticket Management System
-- Phase: 14 - Database Functions Implementation
-- Purpose: User-Defined Functions (UDFs) for ticket age, resolution duration,
--          and SLA compliance calculation.
-- =============================================================================

USE support_ticket_db;

-- -----------------------------------------------------------------------------
-- 1. Function: fn_CalculateTicketAge
-- Description: Computes elapsed age of a ticket in hours from creation up to
--              resolution (if resolved) or current time (if active).
-- -----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_CalculateTicketAge;
DELIMITER //
CREATE FUNCTION fn_CalculateTicketAge (
    p_ticket_id INT
) 
RETURNS DECIMAL(10, 2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_created_at TIMESTAMP;
    DECLARE v_resolved_at TIMESTAMP;
    DECLARE v_end_time TIMESTAMP;
    DECLARE v_age_hours DECIMAL(10, 2);

    SELECT created_at, resolved_at 
    INTO v_created_at, v_resolved_at
    FROM Tickets 
    WHERE ticket_id = p_ticket_id;

    IF v_created_at IS NULL THEN
        RETURN NULL;
    END IF;

    -- If ticket is already resolved, age stops at resolved_at; else it continues to NOW()
    IF v_resolved_at IS NOT NULL THEN
        SET v_end_time = v_resolved_at;
    ELSE
        SET v_end_time = NOW();
    END IF;

    SET v_age_hours = ROUND(TIMESTAMPDIFF(MINUTE, v_created_at, v_end_time) / 60.0, 2);

    RETURN v_age_hours;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 2. Function: fn_CalculateResolutionTime
-- Description: Computes exact duration in hours required to resolve a ticket.
--              Returns NULL if ticket is not yet resolved.
-- -----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_CalculateResolutionTime;
DELIMITER //
CREATE FUNCTION fn_CalculateResolutionTime (
    p_ticket_id INT
) 
RETURNS DECIMAL(10, 2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_created_at TIMESTAMP;
    DECLARE v_resolved_at TIMESTAMP;
    DECLARE v_res_hours DECIMAL(10, 2);

    SELECT created_at, resolved_at 
    INTO v_created_at, v_resolved_at
    FROM Tickets 
    WHERE ticket_id = p_ticket_id;

    IF v_created_at IS NULL OR v_resolved_at IS NULL THEN
        RETURN NULL;
    END IF;

    SET v_res_hours = ROUND(TIMESTAMPDIFF(MINUTE, v_created_at, v_resolved_at) / 60.0, 2);

    RETURN v_res_hours;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 3. Function: fn_GetSLAStatus
-- Description: Evaluates SLA compliance based on priority SLA targets and
--              actual resolution or elapsed ticket time.
-- -----------------------------------------------------------------------------
DROP FUNCTION IF EXISTS fn_GetSLAStatus;
DELIMITER //
CREATE FUNCTION fn_GetSLAStatus (
    p_ticket_id INT
)
RETURNS VARCHAR(25)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE v_created_at TIMESTAMP;
    DECLARE v_resolved_at TIMESTAMP;
    DECLARE v_sla_hours INT;
    DECLARE v_elapsed_hours DECIMAL(10, 2);

    SELECT t.created_at, t.resolved_at, p.sla_hours
    INTO v_created_at, v_resolved_at, v_sla_hours
    FROM Tickets t
    JOIN Priorities p ON t.priority_id = p.priority_id
    WHERE t.ticket_id = p_ticket_id;

    IF v_created_at IS NULL THEN
        RETURN 'TICKET NOT FOUND';
    END IF;

    -- Case 1: Ticket is already resolved
    IF v_resolved_at IS NOT NULL THEN
        SET v_elapsed_hours = TIMESTAMPDIFF(MINUTE, v_created_at, v_resolved_at) / 60.0;
        IF v_elapsed_hours <= v_sla_hours THEN
            RETURN 'RESOLVED ON TIME';
        ELSE
            RETURN 'RESOLVED LATE';
        END IF;
    END IF;

    -- Case 2: Ticket is still open / active
    SET v_elapsed_hours = TIMESTAMPDIFF(MINUTE, v_created_at, NOW()) / 60.0;
    IF v_elapsed_hours > v_sla_hours THEN
        RETURN 'SLA BREACHED';
    ELSEIF v_elapsed_hours > (v_sla_hours * 0.75) THEN
        RETURN 'SLA WARNING';
    ELSE
        RETURN 'WITHIN SLA';
    END IF;
END //
DELIMITER ;



-- >>> START: 01_create_procedures.sql <<<
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



-- >>> START: 01_create_triggers.sql <<<
-- =============================================================================
-- Script: 01_create_triggers.sql
-- Project: Customer Support Ticket Management System
-- Phase: 15 - Database Triggers Implementation
-- Purpose: Automatic resolution timestamping and immutable status audit logging
-- =============================================================================

USE support_ticket_db;

-- -----------------------------------------------------------------------------
-- 1. Trigger: trg_Ticket_Initial_History_Log
-- Event: AFTER INSERT ON Tickets
-- Purpose: Automatically creates the inception record in Ticket_Status_History
--          when a customer submits a new ticket.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_Ticket_Initial_History_Log;
DELIMITER //
CREATE TRIGGER trg_Ticket_Initial_History_Log
AFTER INSERT ON Tickets
FOR EACH ROW
BEGIN
    INSERT INTO Ticket_Status_History (
        ticket_id,
        old_status_id,
        new_status_id,
        changed_by,
        remarks,
        changed_at
    ) VALUES (
        NEW.ticket_id,
        NULL,
        NEW.status_id,
        NEW.customer_id,
        'Ticket initially submitted by customer',
        NOW()
    );
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 2. Trigger: trg_Ticket_Status_Resolved_Timestamp
-- Event: BEFORE UPDATE ON Tickets
-- Purpose: Automatically stamps resolved_at = NOW() when status changes to
--          'Resolved' (status_id = 3). Clears resolved_at if reopened.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_Ticket_Status_Resolved_Timestamp;
DELIMITER //
CREATE TRIGGER trg_Ticket_Status_Resolved_Timestamp
BEFORE UPDATE ON Tickets
FOR EACH ROW
BEGIN
    DECLARE v_resolved_status_id INT;

    SELECT status_id INTO v_resolved_status_id 
    FROM Ticket_Status 
    WHERE status_name = 'Resolved' 
    LIMIT 1;

    -- If status is changing to Resolved, set resolved_at automatically
    IF NEW.status_id = v_resolved_status_id AND (OLD.status_id <> v_resolved_status_id OR OLD.status_id IS NULL) THEN
        IF NEW.resolved_at IS NULL THEN
            SET NEW.resolved_at = NOW();
        END IF;
    -- If ticket was previously resolved and is being reopened (e.g., moved back to In Progress or Open)
    ELSEIF OLD.status_id = v_resolved_status_id AND NEW.status_id <> v_resolved_status_id THEN
        SET NEW.resolved_at = NULL;
    END IF;
END //
DELIMITER ;

-- -----------------------------------------------------------------------------
-- 3. Trigger: trg_Ticket_Status_History_Log
-- Event: AFTER UPDATE ON Tickets
-- Purpose: Automatically intercepts any change to status_id and writes an
--          immutable audit trail entry into Ticket_Status_History.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_Ticket_Status_History_Log;
DELIMITER //
CREATE TRIGGER trg_Ticket_Status_History_Log
AFTER UPDATE ON Tickets
FOR EACH ROW
BEGIN
    DECLARE v_old_status_name VARCHAR(30);
    DECLARE v_new_status_name VARCHAR(30);

    -- Only record history if status actually transitioned
    IF OLD.status_id <> NEW.status_id THEN
        SELECT status_name INTO v_old_status_name FROM Ticket_Status WHERE status_id = OLD.status_id;
        SELECT status_name INTO v_new_status_name FROM Ticket_Status WHERE status_id = NEW.status_id;

        INSERT INTO Ticket_Status_History (
            ticket_id,
            old_status_id,
            new_status_id,
            changed_by,
            remarks,
            changed_at
        ) VALUES (
            NEW.ticket_id,
            OLD.status_id,
            NEW.status_id,
            NEW.assigned_agent_id,
            CONCAT('Status transitioned from ', COALESCE(v_old_status_name, 'Unknown'), ' to ', v_new_status_name),
            NOW()
        );
    END IF;
END //
DELIMITER ;



