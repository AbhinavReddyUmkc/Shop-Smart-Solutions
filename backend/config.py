import os

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default-development-key')
    
    # Database configuration
    DB_NAME = os.environ.get('DB_NAME', 'threat_intelligence')
    DB_USER = os.environ.get('DB_USER', 'postgres')
    DB_PASS = os.environ.get('DB_PASS', 'password')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '5432')
    
    # API Keys
    NVD_API_KEY = os.environ.get('NVD_API_KEY', '883c2296-bb61-4131-9c25-6961a40eaadf')
    OTX_API_KEY = os.environ.get('OTX_API_KEY', 'd2435e058f11fbd4c49ae3a8dd9dd8cc709088727a1a9c13774544281074180f')
    VIRUSTOTAL_API_KEY = os.environ.get('VIRUSTOTAL_API_KEY', '5884a7b7d11fb8cc2f2fdceb26b0df091835389117c69a8c843bf0f131a5b12e')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', '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')
    
    # API rate limits (requests per minute)
    NVD_RATE_LIMIT = 50
    OTX_RATE_LIMIT = 100
    VIRUSTOTAL_RATE_LIMIT = 4
    HUGGINGFACE_RATE_LIMIT = 60

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

class ProductionConfig(Config):
    DEBUG = False