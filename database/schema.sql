-- Drop tables if they already exist (for a clean slate)
DROP DATABASE kanver;
CREATE DATABASE kanver;
USE kanver;

-- Create User table
CREATE TABLE `User` (
    `User_id`            VARCHAR(255),
    `TC_ID`              BIGINT PRIMARY KEY,
    `Location`           VARCHAR(255),
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
    Patient_TC_ID    BIGINT,
    Blood_Type       VARCHAR(10),
    Age              INT,
    Gender           VARCHAR(10),
    Note             TEXT,
    Location         VARCHAR(255),
    Coordinates      VARCHAR(255),
    Status           VARCHAR(50),
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
