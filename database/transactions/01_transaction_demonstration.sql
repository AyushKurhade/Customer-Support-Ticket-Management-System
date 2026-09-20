-- =============================================================================
-- Script: 01_transaction_demonstration.sql
-- Project: Customer Support Ticket Management System
-- Phase: 16 - Database Transactions & ACID Verification (Commit & Rollback)
-- =============================================================================

USE support_ticket_db;

-- -----------------------------------------------------------------------------
-- 1. SCENARIO A: Successful Multi-Operation Transaction (COMMIT)
-- Business Flow: Reassign ticket to Agent John, escalate priority to High,
--                and append an internal transfer note.
-- -----------------------------------------------------------------------------
START TRANSACTION;

-- Operation 1: Update assigned agent
UPDATE Tickets 
SET assigned_agent_id = 3
WHERE ticket_id = 1;

-- Operation 2: Escalate priority to High (priority_id = 3)
UPDATE Tickets 
SET priority_id = 3
WHERE ticket_id = 1;

-- Operation 3: Add internal handover note
INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal)
VALUES (1, 1, 'Admin Handover: Transferred ticket from Agent Sarah to Agent John with priority escalation.', TRUE);

-- Since all operations succeeded without conflict, commit the changes permanently
COMMIT;

-- Verify all 3 changes are committed
SELECT ticket_id, assigned_agent_id, priority_id FROM Tickets WHERE ticket_id = 1;
SELECT * FROM Ticket_Comments WHERE ticket_id = 1 AND is_internal = TRUE ORDER BY comment_id DESC LIMIT 1;


-- -----------------------------------------------------------------------------
-- 2. SCENARIO B: Transaction Failure & Auto-Reversion (ROLLBACK)
-- Demonstrates Atomicity: If any step fails, all preceding steps are rolled back.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_SafeTicketTransfer;
DELIMITER //
CREATE PROCEDURE sp_SafeTicketTransfer (
    IN p_ticket_id INT,
    IN p_new_agent_id INT,
    IN p_simulated_error BOOLEAN,
    OUT p_result_status VARCHAR(100)
)
BEGIN
    -- Declare SQLEXCEPTION handler that rolls back on any error
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_result_status = 'TRANSACTION FAILED: Error detected, rolled back all changes.';
    END;

    -- Begin the atomic transaction block
    START TRANSACTION;

    -- Step 1: Update assigned agent
    UPDATE Tickets 
    SET assigned_agent_id = p_new_agent_id
    WHERE ticket_id = p_ticket_id;

    -- Step 2: Simulate failure condition or invalid reference
    IF p_simulated_error = TRUE THEN
        -- Deliberate failure: insert into non-existent table or violate FK
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Simulated Hardware / Network Failure during transfer.';
    ELSE
        -- Valid insertion
        INSERT INTO Ticket_Comments (ticket_id, user_id, comment_text, is_internal)
        VALUES (p_ticket_id, p_new_agent_id, 'Transfer confirmed and accepted by agent.', TRUE);
        
        COMMIT;
        SET p_result_status = 'TRANSACTION SUCCESS: Ticket transferred and logged.';
    END IF;
END //
DELIMITER ;

