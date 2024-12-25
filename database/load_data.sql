LOAD DATA INFILE '/var/lib/mysql-files/locations.csv'
INTO TABLE Locations
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
(@City_Name, 
 @District_Name)
SET 
    City_Name = NULLIF(@City_Name, ''),
    District_Name = NULLIF(@District_Name, '');
