"""
Rate Limiting Middleware
Implements rate limiting per FR-022: 10 req/min per session, 100 req/hour per IP
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)
