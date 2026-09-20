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
