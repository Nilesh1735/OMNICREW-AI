CREATE DATABASE IF NOT EXISTS autobrowse_db;
USE autobrowse_db;

CREATE TABLE IF NOT EXISTS leads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    entity_name VARCHAR(255) NOT NULL,
    data_payload JSON NOT NULL,
    classification VARCHAR(50) NOT NULL,
    source_url TEXT NOT NULL,
    data_hash VARCHAR(64) UNIQUE NOT NULL,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
    cost_tokens INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);