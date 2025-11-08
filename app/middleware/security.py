from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import hashlib
import secrets

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware implementing multiple security layers"""
    
    def __init__(self, app):
        super().__init__(app)
        self.blocked_ips = set()
        self.suspicious_patterns = [
            'union select',
            'drop table',
            '<script',
            'javascript:',
            '../../../',
            'cmd.exe',
            '/etc/passwd'
        ]
        
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Security checks
        if not await self._security_checks(request):
            return Response(
                content="Access Denied",
                status_code=403,
                headers={"X-Security-Block": "true"}
            )
        
        # Add security headers
        response = await call_next(request)
        
        # Process time
        process_time = time.time() - start_time
        
        # Add security headers
        self._add_security_headers(response)
        
        # Log request
        await self._log_request(request, response, process_time)
        
        return response
    
    async def _security_checks(self, request: Request) -> bool:
        """Perform security checks on incoming requests"""
        
        # Check blocked IPs
        client_ip = self._get_client_ip(request)
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return False
        
        # Check for malicious patterns in URL
        url_path = str(request.url.path).lower()
        for pattern in self.suspicious_patterns:
            if pattern in url_path:
                logger.warning(f"Suspicious pattern detected in URL: {pattern} from {client_ip}")
                self._add_to_blocklist(client_ip)
                return False
        
        # Check query parameters
        if request.url.query:
            query_string = str(request.url.query).lower()
            for pattern in self.suspicious_patterns:
                if pattern in query_string:
                    logger.warning(f"Suspicious pattern detected in query: {pattern} from {client_ip}")
                    return False
        
        # Check User-Agent
        user_agent = request.headers.get("user-agent", "").lower()
        if self._is_suspicious_user_agent(user_agent):
            logger.warning(f"Suspicious user agent: {user_agent} from {client_ip}")
            return False
        
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(f"Request too large: {content_length} bytes from {client_ip}")
            return False
        
        return True
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent is suspicious"""
        suspicious_agents = [
            'sqlmap',
            'nikto',
            'nmap',
            'masscan',
            'burp',
            'owasp',
            'scanner'
        ]
        
        return any(agent in user_agent for agent in suspicious_agents)
    
    def _add_to_blocklist(self, ip: str):
        """Add IP to blocklist"""
        self.blocked_ips.add(ip)
        logger.info(f"Added {ip} to blocklist")
    
    def _add_security_headers(self, response: Response):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data: https:; font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com;",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Powered-By": "TOR-Analysis-System"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    async def _log_request(self, request: Request, response: Response, process_time: float):
        """Log request for security monitoring"""
        client_ip = self._get_client_ip(request)
        
        log_data = {
            "timestamp": time.time(),
            "client_ip": client_ip,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "process_time": process_time,
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", "")
        }
        
        # Log suspicious activity
        if response.status_code >= 400:
            logger.warning(f"HTTP {response.status_code} - {request.method} {request.url.path} from {client_ip}")
        
        # Log slow requests
        if process_time > 5.0:
            logger.warning(f"Slow request: {process_time:.2f}s - {request.method} {request.url.path}")

class CSRFProtection:
    """CSRF protection utility"""
    
    @staticmethod
    def generate_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_token(token: str, session_token: str) -> bool:
        """Verify CSRF token"""
        return secrets.compare_digest(token, session_token)

class InputSanitizer:
    """Input sanitization utility"""
    
    @staticmethod
    def sanitize_string(input_str: str) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            return ""
        
        # Remove null bytes
        sanitized = input_str.replace('\x00', '')
        
        # Limit length
        sanitized = sanitized[:1000]
        
        # Remove control characters except newline and tab
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\t')
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename"""
        if not isinstance(filename, str):
            return "unknown"
        
        # Remove path separators and dangerous characters
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*', '\x00']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit length
        sanitized = sanitized[:255]
        
        return sanitized.strip() or "unknown"

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests = {}
        self.cleanup_interval = 3600  # 1 hour
        self.last_cleanup = time.time()
    
    def is_allowed(self, identifier: str, limit: int = 100, window: int = 3600) -> bool:
        """Check if request is allowed under rate limit"""
        current_time = time.time()
        
        # Cleanup old entries
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time - window)
            self.last_cleanup = current_time
        
        # Get or create request history for identifier
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        request_times = self.requests[identifier]
        
        # Remove old requests outside the window
        request_times[:] = [t for t in request_times if current_time - t < window]
        
        # Check if under limit
        if len(request_times) >= limit:
            return False
        
        # Add current request
        request_times.append(current_time)
        return True
    
    def _cleanup_old_entries(self, cutoff_time: float):
        """Remove old entries to prevent memory leaks"""
        for identifier in list(self.requests.keys()):
            self.requests[identifier] = [
                t for t in self.requests[identifier] if t > cutoff_time
            ]
            
            # Remove empty entries
            if not self.requests[identifier]:
                del self.requests[identifier]