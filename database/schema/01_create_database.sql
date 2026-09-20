-- =============================================================================
-- Script: 01_create_database.sql
-- Project: Customer Support Ticket Management System
-- Phase: 7 - Database Creation
-- Purpose: Creates the project database with proper character set and collation
-- =============================================================================

CREATE DATABASE IF NOT EXISTS support_ticket_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE support_ticket_db;
