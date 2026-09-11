-- =========================================================================
-- Electricity Billing Management System -- Demo Seed Data
-- =========================================================================
-- Run AFTER schema.sql, on a fresh/empty database:
--     mysql -u root -p electricity_billing < database/seed.sql
--
-- This file assumes the tables are empty (fresh AUTO_INCREMENT counters
-- starting at 1) so the customer_id / bill_id values referenced below line
-- up. If you've already been using the app, back up first.
--
-- ABOUT THE PASSWORDS BELOW:
-- They are written here as plain text on purpose. services/security.py
-- recognises any password_hash value that isn't in our hashed format as a
-- "legacy plaintext" row -- login still works, and the very first
-- successful login automatically rehashes it properly. So the moment
-- these demo accounts are used once, they're no longer stored as
-- plaintext. This keeps the seed file simple and human-readable.
-- =========================================================================

USE electricity_billing;

-- ---------------------------------------------------------------------
-- Tariffs (non-overlapping slabs per connection type)
-- ---------------------------------------------------------------------
INSERT INTO tariffs (connection_type, min_units, max_units, rate_per_unit) VALUES
    ('DOMESTIC',   1,   100, 4.50),
    ('DOMESTIC',   101, 300, 6.00),
    ('DOMESTIC',   301, 99999, 8.00),
    ('COMMERCIAL', 1,   200, 7.00),
    ('COMMERCIAL', 201, 99999, 9.50),
    ('INDUSTRIAL', 1,   500, 6.50),
    ('INDUSTRIAL', 501, 99999, 8.75);

-- ---------------------------------------------------------------------
-- Customers (demo-safe, clearly labeled)
-- ---------------------------------------------------------------------
INSERT INTO customers (first_name, last_name, email, phone, address, city, state, pincode, connection_date, connection_type) VALUES
    ('Asha',  'Rao',    'demo.customer1@example.com', '9000000001', '12 MG Road',      'Bengaluru', 'Karnataka',   '560001', '2024-01-15', 'DOMESTIC'),
    ('Vikram','Shah',   'demo.customer2@example.com', '9000000002', '45 Anna Salai',   'Chennai',   'Tamil Nadu',  '600002', '2024-03-10', 'COMMERCIAL'),
    ('Meera', 'Nair',   'demo.customer3@example.com', '9000000003', '7 Park Street',   'Kolkata',   'West Bengal', '700016', '2023-11-05', 'DOMESTIC');

-- ---------------------------------------------------------------------
-- Meters
-- ---------------------------------------------------------------------
INSERT INTO meters (customer_id, meter_number, meter_type, installation_date, initial_reading, current_reading, meter_status) VALUES
    (1, 'MTR-DEMO-0001', 'SINGLE_PHASE', '2024-01-16', 0,    420, 'ACTIVE'),
    (2, 'MTR-DEMO-0002', 'THREE_PHASE',  '2024-03-11', 0,    1180, 'ACTIVE'),
    (3, 'MTR-DEMO-0003', 'SINGLE_PHASE', '2023-11-06', 100,  260, 'ACTIVE');

-- ---------------------------------------------------------------------
-- Users (login accounts) -- passwords documented at the bottom of this file
-- ---------------------------------------------------------------------
INSERT INTO users (username, password_hash, role, customer_id, employee_name) VALUES
    ('admin',          'Admin@123',    'ADMIN',    NULL, NULL),
    ('employee.raj',   'Employee@123', 'EMPLOYEE', NULL, 'Raj Employee (Demo)'),
    ('demo.customer1@example.com', 'DemoPass@123', 'CUSTOMER', 1, NULL),
    ('demo.customer2@example.com', 'DemoPass@123', 'CUSTOMER', 2, NULL),
    ('demo.customer3@example.com', 'DemoPass@123', 'CUSTOMER', 3, NULL);

-- ---------------------------------------------------------------------
-- Bills -- a mix of PAID, UNPAID (future due date) and one already past
-- due (UNPAID with a past due_date -- the app will flip it to OVERDUE
-- and apply the late fee the first time bills are viewed).
-- ---------------------------------------------------------------------
INSERT INTO bills (
    customer_id, customer_name, email, phone, address, connection_type, meter_number,
    billing_month, previous_reading, current_reading, units_consumed,
    energy_charge, fixed_charge, tax, late_fee, total_amount, due_date, status
) VALUES
    -- Customer 1: one paid bill, one currently unpaid (future due date)
    (1, 'Asha Rao', 'demo.customer1@example.com', '9000000001', '12 MG Road', 'DOMESTIC', 'MTR-DEMO-0001',
     '2026-07-01', 0, 210, 210, 1155.00, 0, 57.75, 0, 1212.75, '2026-07-16', 'PAID'),
    (1, 'Asha Rao', 'demo.customer1@example.com', '9000000001', '12 MG Road', 'DOMESTIC', 'MTR-DEMO-0001',
     '2026-08-01', 210, 420, 210, 1155.00, 0, 57.75, 0, 1212.75, '2026-09-20', 'UNPAID'),

    -- Customer 2: one bill already past its due date -> becomes OVERDUE on first view
    (2, 'Vikram Shah', 'demo.customer2@example.com', '9000000002', '45 Anna Salai', 'COMMERCIAL', 'MTR-DEMO-0002',
     '2026-07-01', 0, 1180, 1180, 9860.00, 0, 493.00, 0, 10353.00, '2026-08-01', 'UNPAID'),

    -- Customer 3: one paid bill for history
    (3, 'Meera Nair', 'demo.customer3@example.com', '9000000003', '7 Park Street', 'DOMESTIC', 'MTR-DEMO-0003',
     '2026-06-01', 100, 260, 160, 810.00, 0, 40.50, 0, 850.50, '2026-06-16', 'PAID');

-- ---------------------------------------------------------------------
-- Payments (matching the PAID bills above: bill_id 1 and bill_id 4)
-- ---------------------------------------------------------------------
INSERT INTO payments (bill_id, customer_name, amount, payment_method, transaction_id, payment_status) VALUES
    (1, 'Asha Rao',  1212.75, 'UPI',  'DEMO-TXN-0001', 'SUCCESS'),
    (4, 'Meera Nair', 850.50, 'CASH', 'DEMO-TXN-0002', 'SUCCESS');

-- ---------------------------------------------------------------------
-- Grievances
-- ---------------------------------------------------------------------
INSERT INTO grievances (customer_id, category, description, related_bill_id, status, resolution) VALUES
    (1, 'INCORRECT_BILL', 'My August bill seems higher than usual for the units shown.', 2, 'OPEN', NULL),
    (3, 'METER_READING',  'The reading on my June bill did not match the meter display.', 4, 'RESOLVED',
     'Reading verified against meter photo; original bill amount confirmed correct.');

-- =========================================================================
-- DEMO ACCOUNTS (documented here, not a secret -- this is a class project)
-- =========================================================================
--   Admin      username: admin                          password: Admin@123
--   Employee   username: employee.raj                   password: Employee@123
--   Customer   username: demo.customer1@example.com      password: DemoPass@123
--   Customer   username: demo.customer2@example.com      password: DemoPass@123
--   Customer   username: demo.customer3@example.com      password: DemoPass@123
-- =========================================================================
