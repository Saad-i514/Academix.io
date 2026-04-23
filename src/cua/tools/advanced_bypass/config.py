"""Configuration management for advanced YouTube bypass system.

Handles configuration loading, validation, and hot-reload support for Railway environments.
"""

import os
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum
from pathlib import Path

logger = logging.getLogger("Academix.AdvancedBypass")


class ProxyProvider(Enum):
    """Supported residential proxy providers."""
    BRIGHT_DATA = "bright_data"
    OXYLABS = "oxylabs"
    SMARTPROXY = "smartproxy"


@dataclass
class ProxyConfig:
    """Configuration for proxy provider."""
    provider: ProxyProvider
    api_key: str
    api_secret: Optional[str] = None
    enabled: bool = True
    priority: int = 1  # Higher priority = used first
    max_retries: int = 3
    timeout: int = 30
    
    def validate(self) -> List[str]:
        """Validate proxy configuration."""
        warnings = []
        if not self.api_key:
            warnings.append(f"Proxy provider {self.provider.value} has no API key")
        if self.priority < 1:
            warnings.append(f"Proxy priority must be >= 1, got {self.priority}")
        if self.timeout < 5:
            warnings.append(f"Proxy timeout is very low: {self.timeout}s")
        return warnings


@dataclass
class BypassSystemMetrics:
    """Metrics for bypass system performance tracking."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    bot_detection_count: int = 0
    average_response_time: float = 0.0
    proxy_success_rates: Dict[str, float] = field(default_factory=dict)
    strategy_success_rates: Dict[str, float] = field(default_factory=dict)
    last_update_time: float = 0.0
    
    def get_success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return asdict(self)


@dataclass
class AdvancedBypassConfig:
    """Configuration for advanced YouTube bypass system."""
    
    # Proxy configuration
    proxy_providers: List[ProxyConfig] = field(default_factory=list)
    min_proxy_pool_size: int = 10
    proxy_health_check_interval: int = 60
    proxy_rotation_strategy: str = "round_robin"  # round_robin, random, priority
    
    # Browser emulation
    enable_browser_emulation: bool = True
    browser_profiles: List[str] = field(default_factory=lambda: ["chrome", "firefox", "safari"])
    fingerprint_rotation_interval: int = 300  # 5 minutes
    
    # Request fingerprinting
    enable_request_fingerprinting: bool = True
    tls_fingerprint_variation: bool = True
    http2_parameter_variation: bool = True
    
    # Rate limiting
    enable_adaptive_rate_limiting: bool = True
    base_request_interval: float = 15.0  # seconds
    max_request_interval: float = 45.0
    min_request_interval: float = 5.0
    
    # Session management
    session_timeout: int = 1800  # 30 minutes
    session_rotation_interval: int = 7200  # 2 hours
    max_sessions_per_proxy: int = 3
    
    # Captcha solving
    enable_captcha_solver: bool = True
    captcha_solver_services: List[str] = field(default_factory=lambda: ["2captcha", "anti_captcha"])
    captcha_timeout: int = 30
    
    # Behavioral randomization
    enable_behavior_randomization: bool = True
    pre_video_browsing_enabled: bool = True
    pre_video_browsing_duration: int = 30  # seconds
    
    # Monitoring and adaptation
    enable_monitoring: bool = True
    monitoring_interval: int = 60
    success_rate_threshold: float = 0.70  # 70%
    adaptation_enabled: bool = True
    
    # Railway environment
    railway_environment: bool = True
    memory_limit_mb: int = 512
    cpu_limit_cores: float = 0.5
    
    # Compliance and security
    respect_robots_txt: bool = True
    max_requests_per_user_per_day: int = 100
    audit_logging_enabled: bool = True
    
    # Feature flags
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Logging
    enable_detailed_logging: bool = False
    log_level: str = "INFO"
    
    def validate(self) -> List[str]:
        """Validate configuration and return warnings."""
        warnings = []
        
        if not self.proxy_providers:
            warnings.append("No proxy providers configured")
        
        for provider in self.proxy_providers:
            warnings.extend(provider.validate())
        
        if self.min_proxy_pool_size < 5:
            warnings.append(f"Minimum proxy pool size is very low: {self.min_proxy_pool_size}")
        
        if self.base_request_interval < self.min_request_interval:
            warnings.append("Base request interval is less than minimum interval")
        
        if self.base_request_interval > self.max_request_interval:
            warnings.append("Base request interval is greater than maximum interval")
        
        if self.memory_limit_mb < 256:
            warnings.append(f"Memory limit is very low: {self.memory_limit_mb}MB")
        
        return warnings
    
    @classmethod
    def from_env(cls) -> "AdvancedBypassConfig":
        """Load configuration from environment variables."""
        config = cls()
        
        # Load proxy providers from environment
        proxy_providers_str = os.environ.get("ADVANCED_BYPASS_PROXY_PROVIDERS", "")
        if proxy_providers_str:
            # Parse comma-separated provider list
            providers = proxy_providers_str.split(",")
            for provider_name in providers:
                provider_name = provider_name.strip().upper()
                try:
                    provider_enum = ProxyProvider[provider_name]
                    api_key = os.environ.get(f"{provider_name}_API_KEY", "")
                    api_secret = os.environ.get(f"{provider_name}_API_SECRET")
                    
                    if api_key:
                        proxy_config = ProxyConfig(
                            provider=provider_enum,
                            api_key=api_key,
                            api_secret=api_secret,
                        )
                        config.proxy_providers.append(proxy_config)
                except KeyError:
                    logger.warning(f"Unknown proxy provider: {provider_name}")
        
        # Load other settings from environment
        config.enable_browser_emulation = os.environ.get(
            "ADVANCED_BYPASS_BROWSER_EMULATION", "true"
        ).lower() == "true"
        
        config.enable_request_fingerprinting = os.environ.get(
            "ADVANCED_BYPASS_REQUEST_FINGERPRINTING", "true"
        ).lower() == "true"
        
        config.enable_adaptive_rate_limiting = os.environ.get(
            "ADVANCED_BYPASS_ADAPTIVE_RATE_LIMITING", "true"
        ).lower() == "true"
        
        config.enable_captcha_solver = os.environ.get(
            "ADVANCED_BYPASS_CAPTCHA_SOLVER", "true"
        ).lower() == "true"
        
        config.enable_monitoring = os.environ.get(
            "ADVANCED_BYPASS_MONITORING", "true"
        ).lower() == "true"
        
        config.adaptation_enabled = os.environ.get(
            "ADVANCED_BYPASS_ADAPTATION", "true"
        ).lower() == "true"
        
        config.enable_detailed_logging = os.environ.get(
            "ADVANCED_BYPASS_DETAILED_LOGGING", "false"
        ).lower() == "true"
        
        config.log_level = os.environ.get("ADVANCED_BYPASS_LOG_LEVEL", "INFO")
        
        # Railway detection
        config.railway_environment = os.environ.get("RAILWAY_ENVIRONMENT_NAME") is not None
        
        return config


class ConfigurationManager:
    """Manages configuration loading, validation, and hot-reload."""
    
    def __init__(self, config: Optional[AdvancedBypassConfig] = None):
        """Initialize configuration manager."""
        self.config = config or AdvancedBypassConfig.from_env()
        self.config_file_path: Optional[Path] = None
        self.last_reload_time: float = 0.0
        self._validate_config()
    
    def _validate_config(self) -> None:
        """Validate configuration and log warnings."""
        warnings = self.config.validate()
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")
    
    def reload_from_env(self) -> bool:
        """Reload configuration from environment variables."""
        try:
            new_config = AdvancedBypassConfig.from_env()
            self._validate_config()
            self.config = new_config
            logger.info("Configuration reloaded from environment variables")
            return True
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")
            return False
    
    def get_config(self) -> AdvancedBypassConfig:
        """Get current configuration."""
        return self.config
    
    def update_feature_flag(self, flag_name: str, enabled: bool) -> None:
        """Update a feature flag."""
        self.config.feature_flags[flag_name] = enabled
        logger.info(f"Feature flag '{flag_name}' set to {enabled}")
    
    def is_feature_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled."""
        return self.config.feature_flags.get(flag_name, False)
    
    def get_enabled_proxy_providers(self) -> List[ProxyConfig]:
        """Get list of enabled proxy providers."""
        return [p for p in self.config.proxy_providers if p.enabled]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return asdict(self.config)
