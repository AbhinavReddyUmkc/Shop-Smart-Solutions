CREATE DATABASE ShopSmartSolutions;
USE ShopSmartSolutions;

CREATE TABLE assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_name VARCHAR(255) NOT NULL,
    asset_type VARCHAR(50) CHECK (asset_type IN ('Hardware', 'Software', 'Data', 'People', 'Process')),
    description TEXT
);
INSERT INTO assets (asset_name, asset_type, description)
VALUES
    ('Customer Database', 'Data', 'Stores customer information'),
    ('Web Application', 'Software', 'Public-facing e-commerce platform'),
    ('Payment Gateway API', 'Software', 'Third-party payment processing service');
    
SELECT * FROM assets;

