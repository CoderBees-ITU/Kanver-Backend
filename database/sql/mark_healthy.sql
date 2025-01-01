-- this file should be executed by docker last,  in order for the health checks to correctly identify when the database service is healthy
USE kanver;

CREATE TABLE IF NOT EXISTS initialization_flag (
    id INT PRIMARY KEY AUTO_INCREMENT,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO initialization_flag (status) VALUES ('completed');