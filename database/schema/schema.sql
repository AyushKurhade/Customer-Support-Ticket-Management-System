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
