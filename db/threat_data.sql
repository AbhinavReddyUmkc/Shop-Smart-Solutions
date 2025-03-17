CREATE TABLE threat_data (
    id SERIAL PRIMARY KEY,
    ip_address VARCHAR(15) NOT NULL,  
    ports TEXT,                       
    services TEXT,                    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  
);