"""Tests for IP address logging from X-Forwarded-For header.

These tests verify that IP addresses are correctly extracted from the
X-Forwarded-For header when behind a reverse proxy or ingress controller.
"""

import unittest
from unittest.mock import Mock, MagicMock
from src.bot_protection import BotProtection


class TestIPExtraction(unittest.TestCase):
    """Test IP address extraction from various request scenarios."""

    def test_get_client_ip_from_x_forwarded_for_single(self):
        """Test extracting IP from X-Forwarded-For with single IP."""
        bot_protection = BotProtection()

        # Mock request with X-Forwarded-For header
        request = Mock()
        request.headers = {'X-Forwarded-For': '192.168.1.100'}
        request.client = Mock(host='10.0.0.1')  # Ingress server IP

        ip = bot_protection.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')

    def test_get_client_ip_from_x_forwarded_for_multiple(self):
        """Test extracting IP from X-Forwarded-For with multiple IPs.

        Format: X-Forwarded-For: client, proxy1, proxy2
        We want the first IP (the original client).
        """
        bot_protection = BotProtection()

        # Mock request with X-Forwarded-For header containing multiple IPs
        request = Mock()
        request.headers = {'X-Forwarded-For': '192.168.1.100, 10.0.0.1, 10.0.0.2'}
        request.client = Mock(host='10.0.0.3')  # Ingress server IP

        ip = bot_protection.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')

    def test_get_client_ip_from_x_forwarded_for_with_spaces(self):
        """Test extracting IP from X-Forwarded-For with extra spaces."""
        bot_protection = BotProtection()

        # Mock request with X-Forwarded-For header with spaces
        request = Mock()
        request.headers = {'X-Forwarded-For': '  192.168.1.100  , 10.0.0.1 '}
        request.client = Mock(host='10.0.0.3')  # Ingress server IP

        ip = bot_protection.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')

    def test_get_client_ip_fallback_to_client_host(self):
        """Test falling back to request.client.host when no X-Forwarded-For."""
        bot_protection = BotProtection()

        # Mock request without X-Forwarded-For header
        request = Mock()
        request.headers = {}
        request.client = Mock(host='192.168.1.100')

        ip = bot_protection.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.100')

    def test_get_client_ip_empty_x_forwarded_for(self):
        """Test handling empty X-Forwarded-For header."""
        bot_protection = BotProtection()

        # Mock request with empty X-Forwarded-For header
        request = Mock()
        request.headers = {'X-Forwarded-For': ''}
        request.client = Mock(host='192.168.1.100')

        ip = bot_protection.get_client_ip(request)
        # Should fall back to client.host
        assert ip == '192.168.1.100'

    def test_get_client_ip_ipv6(self):
        """Test handling IPv6 addresses in X-Forwarded-For."""
        bot_protection = BotProtection()

        # Mock request with IPv6 in X-Forwarded-For
        request = Mock()
        request.headers = {'X-Forwarded-For': '2001:db8::1, 10.0.0.1'}
        request.client = Mock(host='10.0.0.2')

        ip = bot_protection.get_client_ip(request)
        self.assertEqual(ip, '2001:db8::1')

    def test_get_client_ip_kubernetes_scenario(self):
        """Test the Kubernetes ingress scenario described in the issue.

        In Kubernetes with ingress:
        - request.client.host is the ingress controller IP (always same)
        - X-Forwarded-For contains the real client IP
        """
        bot_protection = BotProtection()

        # Simulate Kubernetes ingress scenario
        request = Mock()
        request.headers = {'X-Forwarded-For': '203.0.113.45'}  # Real client IP
        request.client = Mock(host='10.244.0.5')  # Ingress controller pod IP

        ip = bot_protection.get_client_ip(request)
        self.assertEqual(ip, '203.0.113.45', "Should use X-Forwarded-For, not ingress IP")


class TestUsageTrackerIPLogging(unittest.TestCase):
    """Test that usage tracker receives correct IPs."""

    def test_start_ide_session_uses_x_forwarded_for(self):
        """Test that start_ide_session receives IP from X-Forwarded-For."""
        # This test documents the expected behavior after the fix
        # The nicegui backend should:
        # 1. Call bot_protection.get_client_ip(request)
        # 2. Pass that IP to tracker.start_ide_session()
        pass  # Implementation test would require mocking NiceGUI context

    def test_track_page_visit_uses_x_forwarded_for(self):
        """Test that track_page_visit receives IP from X-Forwarded-For."""
        # This test documents the expected behavior after the fix
        # The /api/track_page_visit endpoint should:
        # 1. Extract IP from X-Forwarded-For header in the request
        # 2. Pass that IP to tracker.track_page_visit()
        pass  # Implementation test would require FastAPI test client


if __name__ == '__main__':
    unittest.main()
