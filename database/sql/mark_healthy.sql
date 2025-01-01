USE kanver;

CREATE TABLE IF NOT EXISTS initialization_flag (
    id INT PRIMARY KEY AUTO_INCREMENT,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO initialization_flag (status) VALUES ('completed');