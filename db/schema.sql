-- Table for storing assets
CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing threats
CREATE TABLE threats (
    id SERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(id) ON DELETE CASCADE,
    threat_name VARCHAR(255) NOT NULL,
    description TEXT,
    risk_level INT CHECK (risk_level BETWEEN 1 AND 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing vulnerabilities
CREATE TABLE vulnerabilities (
    id SERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(id) ON DELETE CASCADE,
    vulnerability_name VARCHAR(255) NOT NULL,
    description TEXT,
    severity_level INT CHECK (severity_level BETWEEN 1 AND 10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing risk ratings
CREATE TABLE risk_ratings (
    id SERIAL PRIMARY KEY,
    asset_id INT REFERENCES assets(id) ON DELETE CASCADE,
    threat_id INT REFERENCES threats(id) ON DELETE CASCADE,
    vulnerability_id INT REFERENCES vulnerabilities(id) ON DELETE CASCADE,
    overall_risk_level INT CHECK (overall_risk_level BETWEEN 1 AND 10),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);