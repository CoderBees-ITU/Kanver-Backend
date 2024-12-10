-- Drop tables if they already exist (for a clean slate)
DROP TABLE IF EXISTS Notifications;
DROP TABLE IF EXISTS On_The_Way;
DROP TABLE IF EXISTS Banned_Users;
DROP TABLE IF EXISTS Requests;
DROP TABLE IF EXISTS User;

-- Create User table
CREATE TABLE User (
    TC_ID              BIGINT PRIMARY KEY,
    Location           VARCHAR(255),
    Age                INT,
    Email              VARCHAR(255),
    Phone_Number       VARCHAR(50),
    Blood_Type         VARCHAR(10),
    Last_Donation_Date DATE,
    Is_Eligible        BOOLEAN,
    Gender             VARCHAR(10)
);

-- Create Banned_Users table (1:1 with User)
-- We assume a user can either be banned or not. If they are banned, an entry appears here.
CREATE TABLE Banned_Users (
    TC_ID       BIGINT PRIMARY KEY,
    Date        DATE,
    Cause       VARCHAR(255),
    Unban_Date  DATE,
    FOREIGN KEY (TC_ID) REFERENCES User(TC_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Create Requests table
-- Requests are created by a User (Requested_TC_ID) on behalf of a patient (Patient_TC_ID, which might also be in User)
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
    FOREIGN KEY (Requested_TC_ID) REFERENCES User(TC_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Patient_TC_ID) REFERENCES User(TC_ID) ON DELETE SET NULL ON UPDATE CASCADE
);

-- Create On_The_Way table
-- A donor (Donor_TC_ID) responding to a Request (Request_ID)
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
-- Notifications are related to a single Request
CREATE TABLE Notifications (
    ID                 BIGINT PRIMARY KEY AUTO_INCREMENT,
    Request_ID         BIGINT NOT NULL,
    Notification_Type  VARCHAR(50),
    Message            TEXT,
    FOREIGN KEY (Request_ID) REFERENCES Requests(Request_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Optionally create indexes for foreign keys to improve performance
CREATE INDEX idx_requests_requested_tc_id ON Requests (Requested_TC_ID);
CREATE INDEX idx_requests_patient_tc_id ON Requests (Patient_TC_ID);
CREATE INDEX idx_on_the_way_request_id ON On_The_Way (Request_ID);
CREATE INDEX idx_on_the_way_donor_tc_id ON On_The_Way (Donor_TC_ID);
CREATE INDEX idx_notifications_request_id ON Notifications (Request_ID);

-- The database schema is now created
