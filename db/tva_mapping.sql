USE ShopSmartSolutions
CREATE TABLE tva_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    asset_id INT,
    threat_name VARCHAR(255),
    vulnerability_description TEXT,
    likelihood INT CHECK (likelihood BETWEEN 1 AND 5),
    impact INT CHECK (impact BETWEEN 1 AND 5),
    risk_score INT GENERATED ALWAYS AS (likelihood * impact) STORED,
    FOREIGN KEY (asset_id) REFERENCES assets(id)
);
INSERT INTO tva_mapping (asset_id, threat_name, vulnerability_description, likelihood, impact)
VALUES
    (1, 'SQL Injection', 'Improper input validation allows SQL injection attacks.', 4, 5),
    (2, 'Cross-Site Scripting (XSS)', 'User input not sanitized, leading to XSS vulnerabilities.', 3, 4),
    (3, 'Man-in-the-Middle Attack', 'Lack of encryption in payment gateway communication.', 2, 5)
    ;
SELECT * FROM tva_mapping;
