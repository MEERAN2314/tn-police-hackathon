from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Dict, List
import asyncio

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting middleware with multiple strategies"""
    
    def __init__(self, app):
        super().__init__(app)
        self.rate_limiters = {
            'global': TokenBucketLimiter(capacity=1000, refill_rate=100),
            'per_ip': {},
            'per_endpoint': {}
        }
        self.cleanup_task = None
        self.start_cleanup_task()
    
    def start_cleanup_task(self):
        """Start background cleanup task"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def _cleanup_loop(self):
        """Background task to cleanup old rate limiter entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                await self._cleanup_old_limiters()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
    
    async def _cleanup_old_limiters(self):
        """Remove inactive rate limiters to prevent memory leaks"""
        current_time = time.time()
        cutoff_time = current_time - 3600  # Remove limiters inactive for 1 hour
        
        # Cleanup per-IP limiters
        inactive_ips = []
        for ip, limiter in self.rate_limiters['per_ip'].items():
            if limiter.last_access < cutoff_time:
                inactive_ips.append(ip)
        
        for ip in inactive_ips:
            del self.rate_limiters['per_ip'][ip]
        
        # Cleanup per-endpoint limiters
        inactive_endpoints = []
        for endpoint, limiter in self.rate_limiters['per_endpoint'].items():
            if limiter.last_access < cutoff_time:
                inactive_endpoints.append(endpoint)
        
        for endpoint in inactive_endpoints:
            del self.rate_limiters['per_endpoint'][endpoint]
        
        if inactive_ips or inactive_endpoints:
            logger.info(f"Cleaned up {len(inactive_ips)} IP limiters and {len(inactive_endpoints)} endpoint limiters")
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Get client identifier
        client_ip = self._get_client_ip(request)
        endpoint = f"{request.method}:{request.url.path}"
        
        # Check rate limits
        if not await self._check_rate_limits(client_ip, endpoint, request):
            return Response(
                content="Rate limit exceeded. Please try again later.",
                status_code=429,
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": "100",
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + 60))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        self._add_rate_limit_headers(response, client_ip, endpoint)
        
        return response
    
    async def _check_rate_limits(self, client_ip: str, endpoint: str, request: Request) -> bool:
        """Check all applicable rate limits"""
        
        # Global rate limit
        if not self.rate_limiters['global'].consume():
            logger.warning(f"Global rate limit exceeded")
            return False
        
        # Per-IP rate limit
        ip_limiter = self._get_ip_limiter(client_ip)
        if not ip_limiter.consume():
            logger.warning(f"IP rate limit exceeded for {client_ip}")
            return False
        
        # Per-endpoint rate limit
        endpoint_limiter = self._get_endpoint_limiter(endpoint)
        if not endpoint_limiter.consume():
            logger.warning(f"Endpoint rate limit exceeded for {endpoint}")
            return False
        
        # API-specific rate limits
        if request.url.path.startswith('/api/'):
            api_limiter = self._get_api_limiter(client_ip)
            if not api_limiter.consume():
                logger.warning(f"API rate limit exceeded for {client_ip}")
                return False
        
        return True
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_ip_limiter(self, ip: str) -> 'TokenBucketLimiter':
        """Get or create rate limiter for IP"""
        if ip not in self.rate_limiters['per_ip']:
            # 100 requests per minute per IP
            self.rate_limiters['per_ip'][ip] = TokenBucketLimiter(
                capacity=100,
                refill_rate=100/60  # 100 per minute
            )
        return self.rate_limiters['per_ip'][ip]
    
    def _get_endpoint_limiter(self, endpoint: str) -> 'TokenBucketLimiter':
        """Get or create rate limiter for endpoint"""
        if endpoint not in self.rate_limiters['per_endpoint']:
            # Different limits for different endpoints
            if '/api/' in endpoint:
                capacity = 200
                refill_rate = 200/60
            elif '/dashboard' in endpoint:
                capacity = 50
                refill_rate = 50/60
            else:
                capacity = 100
                refill_rate = 100/60
            
            self.rate_limiters['per_endpoint'][endpoint] = TokenBucketLimiter(
                capacity=capacity,
                refill_rate=refill_rate
            )
        return self.rate_limiters['per_endpoint'][endpoint]
    
    def _get_api_limiter(self, ip: str) -> 'TokenBucketLimiter':
        """Get or create API-specific rate limiter"""
        api_key = f"api_{ip}"
        if api_key not in self.rate_limiters['per_ip']:
            # Stricter limits for API endpoints
            self.rate_limiters['per_ip'][api_key] = TokenBucketLimiter(
                capacity=50,
                refill_rate=50/60  # 50 per minute for API
            )
        return self.rate_limiters['per_ip'][api_key]
    
    def _add_rate_limit_headers(self, response: Response, client_ip: str, endpoint: str):
        """Add rate limit headers to response"""
        try:
            ip_limiter = self.rate_limiters['per_ip'].get(client_ip)
            if ip_limiter:
                response.headers["X-RateLimit-Limit"] = str(int(ip_limiter.capacity))
                response.headers["X-RateLimit-Remaining"] = str(int(ip_limiter.tokens))
                response.headers["X-RateLimit-Reset"] = str(int(time.time() + 60))
        except Exception as e:
            logger.error(f"Error adding rate limit headers: {e}")

class TokenBucketLimiter:
    """Token bucket rate limiter implementation"""
    
    def __init__(self, capacity: float, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.last_refill = time.time()
        self.last_access = time.time()
    
    def consume(self, tokens: float = 1.0) -> bool:
        """Consume tokens from bucket"""
        self.last_access = time.time()
        self._refill()
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
    
    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_refill
        
        if elapsed > 0:
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now

class SlidingWindowLimiter:
    """Sliding window rate limiter"""
    
    def __init__(self, limit: int, window_size: int):
        self.limit = limit
        self.window_size = window_size
        self.requests: List[float] = []
        self.last_access = time.time()
    
    def is_allowed(self) -> bool:
        """Check if request is allowed"""
        self.last_access = time.time()
        current_time = time.time()
        
        # Remove old requests outside the window
        cutoff_time = current_time - self.window_size
        self.requests = [req_time for req_time in self.requests if req_time > cutoff_time]
        
        # Check if under limit
        if len(self.requests) >= self.limit:
            return False
        
        # Add current request
        self.requests.append(current_time)
        return True
    
    def get_remaining(self) -> int:
        """Get remaining requests in current window"""
        current_time = time.time()
        cutoff_time = current_time - self.window_size
        active_requests = [req_time for req_time in self.requests if req_time > cutoff_time]
        return max(0, self.limit - len(active_requests))

class AdaptiveRateLimiter:
    """Adaptive rate limiter that adjusts based on system load"""
    
    def __init__(self, base_limit: int, max_limit: int):
        self.base_limit = base_limit
        self.max_limit = max_limit
        self.current_limit = base_limit
        self.load_samples = []
        self.last_adjustment = time.time()
    
    def update_system_load(self, load_percentage: float):
        """Update system load information"""
        self.load_samples.append((time.time(), load_percentage))
        
        # Keep only last 10 minutes of samples
        cutoff_time = time.time() - 600
        self.load_samples = [(t, load) for t, load in self.load_samples if t > cutoff_time]
        
        # Adjust rate limit based on load
        if time.time() - self.last_adjustment > 60:  # Adjust every minute
            self._adjust_rate_limit()
            self.last_adjustment = time.time()
    
    def _adjust_rate_limit(self):
        """Adjust rate limit based on system load"""
        if not self.load_samples:
            return
        
        # Calculate average load over last 5 minutes
        recent_samples = [(t, load) for t, load in self.load_samples if time.time() - t < 300]
        if not recent_samples:
            return
        
        avg_load = sum(load for _, load in recent_samples) / len(recent_samples)
        
        # Adjust limit based on load
        if avg_load > 80:  # High load - reduce limit
            self.current_limit = max(self.base_limit // 2, self.current_limit * 0.9)
        elif avg_load < 30:  # Low load - increase limit
            self.current_limit = min(self.max_limit, self.current_limit * 1.1)
        else:  # Normal load - gradually return to base
            if self.current_limit < self.base_limit:
                self.current_limit = min(self.base_limit, self.current_limit * 1.05)
            elif self.current_limit > self.base_limit:
                self.current_limit = max(self.base_limit, self.current_limit * 0.95)
        
        logger.info(f"Adjusted rate limit to {self.current_limit:.0f} based on {avg_load:.1f}% load")
    
    def get_current_limit(self) -> int:
        """Get current rate limit"""
        return int(self.current_limit)