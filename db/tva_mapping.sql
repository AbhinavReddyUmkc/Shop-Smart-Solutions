USE ShopSmartSolutions;

-- Create the tva_mapping table if it doesn't exist
CREATE TABLE IF NOT EXISTS tva_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT,
    threat_name VARCHAR(255),
    vulnerability_description TEXT,
    likelihood INT CHECK (likelihood BETWEEN 1 AND 5),
    impact INT CHECK (impact BETWEEN 1 AND 5),
    risk_score INT GENERATED ALWAYS AS (likelihood * impact) STORED,
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);

-- Insert initial data into tva_mapping
INSERT INTO tva_mapping (asset_id, threat_name, vulnerability_description, likelihood, impact)
VALUES
    (1, 'SQL Injection', 'Improper input validation allows SQL injection attacks.', 4, 5),
    (2, 'Cross-Site Scripting (XSS)', 'User input not sanitized, leading to XSS vulnerabilities.', 3, 4),
    (3, 'Man-in-the-Middle Attack', 'Lack of encryption in payment gateway communication.', 2, 5);

-- Example: Dynamic TVA Update Based on OSINT Data
-- Update likelihood based on live threat feeds
UPDATE tva_mapping
SET likelihood = 5
WHERE threat_name = 'SQL Injection'
AND EXISTS (SELECT 1 FROM threat_data WHERE threat_data.threat_type = 'SQL Injection' AND threat_data.risk_score > 20);

-- Update impact based on live threat feeds
UPDATE tva_mapping
SET impact = 5
WHERE threat_name = 'Cross-Site Scripting (XSS)'
AND EXISTS (SELECT 1 FROM threat_data WHERE threat_data.threat_type = 'Cross-Site Scripting (XSS)' AND threat_data.risk_score > 20);

-- Update both likelihood and impact based on live threat feeds
UPDATE tva_mapping
SET likelihood = 5, impact = 5
WHERE threat_name = 'Man-in-the-Middle Attack'
AND EXISTS (SELECT 1 FROM threat_data WHERE threat_data.threat_type = 'Man-in-the-Middle Attack' AND threat_data.risk_score > 20);

-- Select all records from tva_mapping to verify updates
SELECT * FROM tva_mapping;
