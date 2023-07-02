CREATE TABLE user_pastes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(16),
    title VARCHAR(255),
    contents TEXT,
    passwd VARCHAR(20)
);