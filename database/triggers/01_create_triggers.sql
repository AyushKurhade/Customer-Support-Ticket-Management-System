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

