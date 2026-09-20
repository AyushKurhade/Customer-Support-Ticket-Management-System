-- =============================================================================
-- Script: 02_create_tables.sql
-- Project: Customer Support Ticket Management System
-- Phase: 7 & 8 - Table Definitions & Constraints
-- Storage Engine: InnoDB (Enforces ACID properties and Foreign Key constraints)
-- =============================================================================

USE support_ticket_db;

-- -----------------------------------------------------------------------------
-- 1. Table: Users
-- Stores authentication and profile data for Customers, Agents, and Admins.
-- Demonstrates: PK, Candidate Key (email), CHECK constraint on role.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Users (
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

-- -----------------------------------------------------------------------------
-- 2. Table: Categories (Master Data)
-- Classifies support issues into functional IT domains.
-- Demonstrates: PK, Candidate Key (category_name).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Categories (
    category_id INT AUTO_INCREMENT,
    category_name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_categories PRIMARY KEY (category_id),
    CONSTRAINT uq_categories_name UNIQUE (category_name)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 3. Table: Priorities (Master Data)
-- Sets urgency tiers and associated SLA resolution windows.
-- Demonstrates: PK, Candidate Key (priority_name), CHECK constraint (sla_hours > 0).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Priorities (
    priority_id INT AUTO_INCREMENT,
    priority_name VARCHAR(20) NOT NULL,
    sla_hours INT NOT NULL DEFAULT 24,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT pk_priorities PRIMARY KEY (priority_id),
    CONSTRAINT uq_priorities_name UNIQUE (priority_name),
    CONSTRAINT chk_priorities_sla CHECK (sla_hours > 0)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 4. Table: Ticket_Status (Master Data)
-- Enforces allowed lifecycle states in the ticket state machine.
-- Demonstrates: PK, Candidate Key (status_name), DEFAULT constraint.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Ticket_Status (
    status_id INT AUTO_INCREMENT,
    status_name VARCHAR(30) NOT NULL,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT pk_ticket_status PRIMARY KEY (status_id),
    CONSTRAINT uq_ticket_status_name UNIQUE (status_name)
) ENGINE=InnoDB;

-- -----------------------------------------------------------------------------
-- 5. Table: Tickets (Core Transactional Table)
-- Represents customer requests, category classification, agent assignment, and state.
-- Demonstrates: PK, Multiple Foreign Keys, Referential Integrity actions.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Tickets (
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

-- -----------------------------------------------------------------------------
-- 6. Table: Ticket_Comments (Child Activity Table)
-- Threaded communications between customer, assigned agent, and admin.
-- Demonstrates: PK, Composite Foreign Keys with CASCADE on ticket deletion.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Ticket_Comments (
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

-- -----------------------------------------------------------------------------
-- 7. Table: Ticket_Status_History (Audit Trail Table)
-- Immutable audit log of state changes for SLA compliance and lifecycle tracking.
-- Demonstrates: Dual Foreign Keys to Ticket_Status (old and new).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS Ticket_Status_History (
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
