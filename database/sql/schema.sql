-- Drop tables if they already exist (for a clean slate)
DROP DATABASE kanver;
CREATE DATABASE kanver;
USE kanver;

-- Create User table
CREATE TABLE `User` (
    `User_id`            VARCHAR(255),
    `TC_ID`              BIGINT PRIMARY KEY,
    `City`               VARCHAR(255),
    `District`           VARCHAR(255),
    `Birth_Date`         DATE NOT NULL,
    `Name`               VARCHAR(255) NOT NULL,
    `Surname`            VARCHAR(255) NOT NULL,
    `Email`              VARCHAR(255) NOT NULL UNIQUE,
    `Blood_Type`         VARCHAR(10),
    `Last_Donation_Date` DATE,
    `Is_Eligible`        BOOLEAN DEFAULT TRUE
);

-- Create Banned_Users table (1:1 with User)
CREATE TABLE Banned_Users (
    TC_ID       BIGINT PRIMARY KEY,
    Date        DATE,
    Cause       VARCHAR(255),
    Unban_Date  DATE,
    FOREIGN KEY (TC_ID) REFERENCES User(TC_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create Requests table
CREATE TABLE Requests (
    Request_ID       BIGINT PRIMARY KEY AUTO_INCREMENT,
    Requested_TC_ID  BIGINT NOT NULL,
    Patient_TC_ID    BIGINT NOT NULL,
    Blood_Type       VARCHAR(3) NOT NULL,
    Age              INT NOT NULL,
    Gender           VARCHAR(10) NOT NULL,
    Note             TEXT,
    patient_name     VARCHAR(255) NOT NULL,
    patient_surname  VARCHAR(255) NOT NULL,
    Lat              DECIMAL(9,6),
    Lng              DECIMAL(9,6),
    City             VARCHAR(50),
    District         VARCHAR(100),
    Hospital         VARCHAR(200),
    Donor_Count      INT DEFAULT 0,
    Status           VARCHAR(50) NOT NULL,
    Create_Time      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Requested_TC_ID) REFERENCES User(TC_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create On_The_Way table
CREATE TABLE On_The_Way (
    ID             BIGINT PRIMARY KEY AUTO_INCREMENT,
    Request_ID     BIGINT NOT NULL,
    Donor_TC_ID    BIGINT NOT NULL,
    Status         VARCHAR(50),
    Create_Time    DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (Request_ID) REFERENCES Requests(Request_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Donor_TC_ID) REFERENCES User(TC_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create Notifications table
CREATE TABLE Notifications (
    ID                 BIGINT PRIMARY KEY AUTO_INCREMENT,
    Request_ID         BIGINT NOT NULL,
    Notification_Type  VARCHAR(50),
    Message            TEXT,
    Total_Mail_Sent    int,
    FOREIGN KEY (Request_ID) REFERENCES Requests(Request_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create Locations table
CREATE TABLE Locations (
    City_Name       VARCHAR(50) NOT NULL,
    District_Name   VARCHAR(50) NOT NULL,
    PRIMARY KEY(City_Name, District_Name)
);

-- Optionally create indexes for foreign keys to improve performance
CREATE INDEX idx_requests_requested_tc_id ON Requests (Requested_TC_ID);
CREATE INDEX idx_requests_patient_tc_id ON Requests (Patient_TC_ID);
CREATE INDEX idx_on_the_way_request_id ON On_The_Way (Request_ID);
CREATE INDEX idx_on_the_way_donor_tc_id ON On_The_Way (Donor_TC_ID);
CREATE INDEX idx_notifications_request_id ON Notifications (Request_ID);

-- Event scheduler for updating Requests->Status automatically
SET GLOBAL event_scheduler = ON;

CREATE EVENT IF NOT EXISTS UpdateRequestStatus
ON SCHEDULE EVERY 1 DAY
DO
    UPDATE Requests
    SET Status = 'closed'
    WHERE Status != 'closed'
      AND Create_Time <= NOW() - INTERVAL 7 DAY;

CREATE EVENT IF NOT EXISTS UpdateEligibility
ON SCHEDULE EVERY 1 DAY
DO
    UPDATE User
    SET Is_Eligible = TRUE
    WHERE Is_Eligible = FALSE
      AND Last_Donation_Date <= NOW() - INTERVAL 90 DAY;