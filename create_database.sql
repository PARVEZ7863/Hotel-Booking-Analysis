-- ============================================================
-- Hotel Booking Analysis
-- Database and Table Creation Script
-- ============================================================

CREATE DATABASE IF NOT EXISTS hotel_booking_analysis
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE hotel_booking_analysis;


-- ============================================================
-- Create MySQL User for the Project
-- Change the password if required.
-- Use the same password in hotel_booking_analysis.ipynb.
-- ============================================================

CREATE USER IF NOT EXISTS 'hotel_user'@'localhost'
IDENTIFIED BY 'HotelProject@2026';

GRANT ALL PRIVILEGES
ON hotel_booking_analysis.*
TO 'hotel_user'@'localhost';

FLUSH PRIVILEGES;


-- ============================================================
-- Create Hotel Bookings Table
-- ============================================================

CREATE TABLE IF NOT EXISTS hotel_bookings (
    hotel VARCHAR(50),
    is_canceled INT,
    lead_time INT,
    arrival_date_year INT,
    arrival_date_month VARCHAR(20),
    arrival_date_week_number INT,
    arrival_date_day_of_month INT,
    stays_in_weekend_nights INT,
    stays_in_week_nights INT,
    adults INT,
    children VARCHAR(20) NULL,
    babies INT,
    meal VARCHAR(20),
    country VARCHAR(20),
    market_segment VARCHAR(50),
    distribution_channel VARCHAR(50),
    is_repeated_guest INT,
    previous_cancellations INT,
    previous_bookings_not_canceled INT,
    reserved_room_type VARCHAR(10),
    assigned_room_type VARCHAR(10),
    booking_changes INT,
    deposit_type VARCHAR(30),
    agent VARCHAR(20) NULL,
    company VARCHAR(20) NULL,
    days_in_waiting_list INT,
    customer_type VARCHAR(30),
    adr DECIMAL(10,2),
    required_car_parking_spaces INT,
    total_of_special_requests INT,
    reservation_status VARCHAR(30),
    reservation_status_date DATE
);


-- ============================================================
-- Verification Queries
-- Run these after importing the CSV data into the table.
-- ============================================================

-- Check total number of records
SELECT COUNT(*) AS total_rows
FROM hotel_bookings;


-- Display sample records
SELECT *
FROM hotel_bookings
LIMIT 10;


-- Check important columns for NULL values
SELECT
    SUM(hotel IS NULL) AS hotel_nulls,
    SUM(is_canceled IS NULL) AS is_canceled_nulls,
    SUM(lead_time IS NULL) AS lead_time_nulls,
    SUM(children IS NULL) AS children_nulls,
    SUM(country IS NULL) AS country_nulls,
    SUM(agent IS NULL) AS agent_nulls,
    SUM(company IS NULL) AS company_nulls,
    SUM(adr IS NULL) AS adr_nulls,
    SUM(reservation_status_date IS NULL) AS reservation_status_date_nulls
FROM hotel_bookings;