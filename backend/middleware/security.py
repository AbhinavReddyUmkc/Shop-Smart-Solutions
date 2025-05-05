from functools import wraps
from flask import request, jsonify
import os
import time

# Rate limiting configuration
RATE_LIMIT = int(os.environ.get('RATE_LIMIT', 100))  # requests per minute
RATE_LIMIT_WINDOW = 60  # seconds

# Simple in-memory rate limiting (in production, use Redis or similar)
request_history = {}

def rate_limit_middleware():
    """
    Rate limiting middleware to protect the API from abuse
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Initialize or clean up request history
            if client_ip not in request_history:
                request_history[client_ip] = []
            
            # Remove requests older than the window
            request_history[client_ip] = [t for t in request_history[client_ip] 
                                         if current_time - t < RATE_LIMIT_WINDOW]
            
            # Check if rate limit exceeded
            if len(request_history[client_ip]) >= RATE_LIMIT:
                return jsonify({
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later."
                }), 429
            
            # Add current request timestamp
            request_history[client_ip].append(current_time)
            
            # Proceed with the request
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def api_key_required(f):
    """
    Decorator to require API key for sensitive endpoints
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.environ.get('API_KEY')
        
        if not expected_key:
            # If API key is not configured, skip validation
            return f(*args, **kwargs)
        
        if not api_key or api_key != expected_key:
            return jsonify({
                "error": "Unauthorized",
                "message": "Invalid or missing API key"
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function