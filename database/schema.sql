-- =========================================================================
-- Electricity Billing Management System -- Database Schema
-- =========================================================================
-- Run this once to set up a fresh database:
--     mysql -u root -p < database/schema.sql
--
-- All tables use CREATE TABLE IF NOT EXISTS, so running this again on an
-- existing, already-set-up database is safe and will not delete any data.
--
-- NOTE ON UPGRADING AN OLDER DATABASE:
-- If you have an existing database from before this schema file existed
-- (a `users` table with a plain `password` column instead of
-- `password_hash`/`customer_id`/`employee_name`, and no `grievances`
-- table), this script will NOT alter that old `users` table for you
-- (ALTER-if-missing isn't portable across MySQL versions). The simplest
-- path for a class project is to drop and recreate the database with this
-- script, then re-run database/seed.sql for demo data.
-- =========================================================================

CREATE DATABASE IF NOT EXISTS electricity_billing;
USE electricity_billing;

-- ---------------------------------------------------------------------
-- Customers
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id      INT AUTO_INCREMENT PRIMARY KEY,
    first_name       VARCHAR(50)  NOT NULL,
    last_name        VARCHAR(50)  NOT NULL,
    email            VARCHAR(100) NOT NULL UNIQUE,
    phone            VARCHAR(20)  NOT NULL,
    address          VARCHAR(255) NOT NULL,
    city             VARCHAR(50)  NOT NULL,
    state            VARCHAR(50)  NOT NULL,
    pincode          VARCHAR(10),
    connection_date  DATE NOT NULL,
    connection_type  ENUM('DOMESTIC', 'COMMERCIAL', 'INDUSTRIAL') NOT NULL DEFAULT 'DOMESTIC'
);

-- ---------------------------------------------------------------------
-- Users (login accounts for all three roles)
-- customer_id is set only for role='CUSTOMER' and links to `customers`.
-- employee_name is set only for role='EMPLOYEE'.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(100) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    role           ENUM('ADMIN', 'EMPLOYEE', 'CUSTOMER') NOT NULL,
    customer_id    INT NULL,
    employee_name  VARCHAR(100) NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_users_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Meters (one meter per customer, matching the existing service logic)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS meters (
    meter_id           INT AUTO_INCREMENT PRIMARY KEY,
    customer_id        INT NOT NULL UNIQUE,
    meter_number       VARCHAR(50) NOT NULL UNIQUE,
    meter_type         ENUM('SINGLE_PHASE', 'THREE_PHASE') NOT NULL DEFAULT 'SINGLE_PHASE',
    installation_date  DATE NOT NULL,
    initial_reading    DECIMAL(12, 2) NOT NULL DEFAULT 0,
    current_reading    DECIMAL(12, 2) NOT NULL DEFAULT 0,
    meter_status       ENUM('ACTIVE', 'INACTIVE', 'FAULTY') NOT NULL DEFAULT 'ACTIVE',
    CONSTRAINT fk_meters_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Tariffs (slab-based rates per connection type -- non-overlap enforced
-- in services/tariff_service.py, not just here)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tariffs (
    tariff_id       INT AUTO_INCREMENT PRIMARY KEY,
    connection_type ENUM('DOMESTIC', 'COMMERCIAL', 'INDUSTRIAL') NOT NULL,
    min_units       DECIMAL(12, 2) NOT NULL,
    max_units       DECIMAL(12, 2) NOT NULL,
    rate_per_unit   DECIMAL(10, 2) NOT NULL
);

-- ---------------------------------------------------------------------
-- Bills
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS bills (
    bill_id           INT AUTO_INCREMENT PRIMARY KEY,
    customer_id       INT NOT NULL,
    customer_name     VARCHAR(120) NOT NULL,
    email             VARCHAR(100),
    phone             VARCHAR(20),
    address           VARCHAR(255),
    connection_type   ENUM('DOMESTIC', 'COMMERCIAL', 'INDUSTRIAL') NOT NULL,
    meter_number      VARCHAR(50),
    billing_month     DATE NOT NULL,
    previous_reading  DECIMAL(12, 2) NOT NULL,
    current_reading   DECIMAL(12, 2) NOT NULL,
    units_consumed    DECIMAL(12, 2) NOT NULL,
    energy_charge     DECIMAL(12, 2) NOT NULL DEFAULT 0,
    fixed_charge      DECIMAL(12, 2) NOT NULL DEFAULT 0,
    tax               DECIMAL(12, 2) NOT NULL DEFAULT 0,
    late_fee          DECIMAL(12, 2) NOT NULL DEFAULT 0,
    total_amount      DECIMAL(12, 2) NOT NULL DEFAULT 0,
    due_date          DATE NOT NULL,
    status            ENUM('UNPAID', 'PAID', 'OVERDUE') NOT NULL DEFAULT 'UNPAID',
    CONSTRAINT fk_bills_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Payments
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS payments (
    payment_id      INT AUTO_INCREMENT PRIMARY KEY,
    bill_id         INT NOT NULL,
    customer_name   VARCHAR(120) NOT NULL,
    amount          DECIMAL(12, 2) NOT NULL,
    payment_method  ENUM('CASH', 'CARD', 'UPI', 'NET_BANKING') NOT NULL,
    transaction_id  VARCHAR(100),
    payment_status  ENUM('SUCCESS', 'FAILED') NOT NULL DEFAULT 'SUCCESS',
    payment_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payments_bill
        FOREIGN KEY (bill_id) REFERENCES bills(bill_id)
        ON DELETE CASCADE
);

-- ---------------------------------------------------------------------
-- Grievances / appeals (customer-submitted, admin/employee-handled)
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS grievances (
    grievance_id     INT AUTO_INCREMENT PRIMARY KEY,
    customer_id      INT NOT NULL,
    category         ENUM('INCORRECT_BILL', 'METER_READING', 'PAYMENT_ISSUE', 'CONNECTION_ISSUE', 'OTHER') NOT NULL,
    description      TEXT NOT NULL,
    related_bill_id  INT NULL,
    status           ENUM('OPEN', 'IN_PROGRESS', 'RESOLVED', 'REJECTED') NOT NULL DEFAULT 'OPEN',
    resolution       TEXT NULL,
    submitted_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_grievances_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_grievances_bill
        FOREIGN KEY (related_bill_id) REFERENCES bills(bill_id)
        ON DELETE SET NULL
);
