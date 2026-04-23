"""Advanced YouTube bypass system for Railway production environments.

This module provides sophisticated bot detection evasion mechanisms including:
- Multi-proxy infrastructure with residential IP rotation
- Advanced browser emulation and fingerprinting
- Intelligent request fingerprinting
- Adaptive rate limiting
- Session persistence and management
- Captcha resolution
- Behavioral pattern randomization
- Real-time monitoring and adaptation
"""

from .config import (
    AdvancedBypassConfig,
    ProxyConfig,
    BypassSystemMetrics,
    ConfigurationManager,
)
from .monitoring import HealthChecker, MetricsCollector
from .manager import AdvancedBypassManager

__all__ = [
    "AdvancedBypassConfig",
    "ProxyConfig",
    "BypassSystemMetrics",
    "ConfigurationManager",
    "HealthChecker",
    "MetricsCollector",
    "AdvancedBypassManager",
]
