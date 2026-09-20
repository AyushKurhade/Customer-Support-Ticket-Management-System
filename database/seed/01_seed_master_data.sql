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

