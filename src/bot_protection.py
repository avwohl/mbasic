"""Bot protection middleware for MBASIC web UI.

Implements CAPTCHA verification and rate limiting to prevent bot abuse.
"""

import os
import time
import hashlib
import requests
from typing import Optional, Dict
from functools import wraps


class BotProtection:
    """Bot protection using hCaptcha and rate limiting."""

    def __init__(self, redis_client=None):
        """Initialize bot protection.

        Args:
            redis_client: Redis client for session storage (optional)
        """
        self.hcaptcha_site_key = os.environ.get('HCAPTCHA_SITE_KEY')
        self.hcaptcha_secret_key = os.environ.get('HCAPTCHA_SECRET_KEY')
        self.redis_client = redis_client
        self.enabled = bool(self.hcaptcha_site_key and self.hcaptcha_secret_key)

        # In-memory fallback if Redis not available
        self._verified_sessions = {}  # session_id -> timestamp
        self._rate_limit_cache = {}   # ip_address -> [timestamps]

    def is_verified(self, session_id: str) -> bool:
        """Check if a session has passed CAPTCHA verification.

        Args:
            session_id: Unique session identifier

        Returns:
            True if verified, False otherwise
        """
        if not self.enabled:
            return True  # No CAPTCHA configured, allow all

        # Check Redis first
        if self.redis_client:
            try:
                key = f"bot_verified:{session_id}"
                return bool(self.redis_client.get(key))
            except Exception:
                pass  # Fall through to in-memory

        # Check in-memory cache
        if session_id in self._verified_sessions:
            timestamp = self._verified_sessions[session_id]
            # Expire after 24 hours
            if time.time() - timestamp < 86400:
                return True
            else:
                del self._verified_sessions[session_id]

        return False

    def mark_verified(self, session_id: str, duration: int = 86400):
        """Mark a session as verified after passing CAPTCHA.

        Args:
            session_id: Unique session identifier
            duration: How long verification lasts (seconds, default 24 hours)
        """
        # Store in Redis
        if self.redis_client:
            try:
                key = f"bot_verified:{session_id}"
                self.redis_client.setex(key, duration, "1")
            except Exception:
                pass  # Fall through to in-memory

        # Store in-memory as backup
        self._verified_sessions[session_id] = time.time()

    def verify_captcha(self, token: str, ip_address: Optional[str] = None) -> bool:
        """Verify hCaptcha response token.

        Args:
            token: hCaptcha response token from client
            ip_address: Client IP address (optional)

        Returns:
            True if CAPTCHA passed, False otherwise
        """
        if not self.enabled:
            return True

        try:
            data = {
                'secret': self.hcaptcha_secret_key,
                'response': token
            }
            if ip_address:
                data['remoteip'] = ip_address

            response = requests.post(
                'https://hcaptcha.com/siteverify',
                data=data,
                timeout=5
            )

            result = response.json()
            return result.get('success', False)

        except Exception as e:
            # Log error but don't block users if CAPTCHA service is down
            print(f"hCaptcha verification error: {e}")
            return True  # Fail open

    def check_rate_limit(self, ip_address: str, max_requests: int = 60, window: int = 60) -> bool:
        """Check if IP address is within rate limits.

        Args:
            ip_address: Client IP address
            max_requests: Maximum requests allowed
            window: Time window in seconds

        Returns:
            True if within limits, False if exceeded
        """
        now = time.time()
        window_start = now - window

        # Check Redis first
        if self.redis_client:
            try:
                key = f"rate_limit:{ip_address}"
                count = self.redis_client.incr(key)
                if count == 1:
                    self.redis_client.expire(key, window)
                return count <= max_requests
            except Exception:
                pass  # Fall through to in-memory

        # In-memory rate limiting
        if ip_address not in self._rate_limit_cache:
            self._rate_limit_cache[ip_address] = []

        # Remove old timestamps
        self._rate_limit_cache[ip_address] = [
            ts for ts in self._rate_limit_cache[ip_address]
            if ts > window_start
        ]

        # Add current timestamp
        self._rate_limit_cache[ip_address].append(now)

        # Check limit
        return len(self._rate_limit_cache[ip_address]) <= max_requests

    def get_session_id(self, request) -> str:
        """Generate or retrieve session ID for a request.

        Args:
            request: NiceGUI request object

        Returns:
            Unique session identifier
        """
        # Try to get from cookie
        session_cookie = request.cookies.get('mbasic_session')
        if session_cookie:
            return session_cookie

        # Generate new session ID
        ip = request.headers.get('X-Forwarded-For', request.client.host)
        user_agent = request.headers.get('User-Agent', '')
        timestamp = str(time.time())

        session_data = f"{ip}:{user_agent}:{timestamp}"
        session_id = hashlib.sha256(session_data.encode()).hexdigest()

        return session_id

    def get_client_ip(self, request) -> str:
        """Get client IP address from request.

        Args:
            request: NiceGUI request object

        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (from load balancer)
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            # Take first IP (client IP before proxies)
            return forwarded.split(',')[0].strip()

        # Fall back to direct client IP
        return request.client.host


# Global bot protection instance
_bot_protection: Optional[BotProtection] = None


def get_bot_protection(redis_client=None) -> BotProtection:
    """Get global bot protection instance.

    Args:
        redis_client: Redis client for session storage (optional)

    Returns:
        BotProtection instance
    """
    global _bot_protection
    if _bot_protection is None:
        _bot_protection = BotProtection(redis_client)
    return _bot_protection


def require_verification(func):
    """Decorator to require CAPTCHA verification before accessing a page.

    Usage:
        @require_verification
        async def my_page():
            # Page content
            pass
    """
    @wraps(func)
    async def wrapper(request, *args, **kwargs):
        bot_protection = get_bot_protection()
        session_id = bot_protection.get_session_id(request)

        if not bot_protection.is_verified(session_id):
            # Redirect to CAPTCHA page
            from nicegui import ui
            ui.navigate.to('/verify')
            return

        return await func(request, *args, **kwargs)

    return wrapper
