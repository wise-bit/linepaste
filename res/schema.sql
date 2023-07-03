CREATE TABLE user_pastes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uuid VARCHAR(16),
    title VARCHAR(255),
    contents TEXT,
    passwd VARCHAR(100),
    created_at datetime not null default now(),
    expire_at datetime not null default (now() + interval 1 day)
);