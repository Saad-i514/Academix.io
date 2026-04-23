"""Advanced bypass manager orchestrating all bypass mechanisms."""

import logging
from typing import Optional, Dict, Any

from .config import AdvancedBypassConfig, ConfigurationManager
from .monitoring import HealthChecker, MetricsCollector

logger = logging.getLogger("Academix.AdvancedBypass")


class AdvancedBypassManager:
    """Orchestrates all advanced YouTube bypass mechanisms.
    
    This manager coordinates:
    - Multi-proxy infrastructure
    - Browser emulation
    - Request fingerprinting
    - Adaptive rate limiting
    - Session management
    - Captcha resolution
    - Behavioral randomization
    - Real-time monitoring and adaptation
    """
    
    def __init__(self, config: Optional[AdvancedBypassConfig] = None):
        """Initialize advanced bypass manager.
        
        Args:
            config: AdvancedBypassConfig instance. If None, loads from environment.
        """
        self.config_manager = ConfigurationManager(config)
        self.config = self.config_manager.get_config()
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        
        self._initialize_components()
        logger.info("AdvancedBypassManager initialized")
    
    def _initialize_components(self) -> None:
        """Initialize all bypass system components."""
        logger.info("Initializing bypass system components...")
        
        # Validate configuration
        warnings = self.config.validate()
        for warning in warnings:
            logger.warning(f"Configuration: {warning}")
        
        # Initialize proxy providers
        enabled_providers = self.config_manager.get_enabled_proxy_providers()
        logger.info(f"Initialized {len(enabled_providers)} proxy providers")
        
        # Initialize browser emulation if enabled
        if self.config.enable_browser_emulation:
            logger.info("Browser emulation enabled")
        
        # Initialize request fingerprinting if enabled
        if self.config.enable_request_fingerprinting:
            logger.info("Request fingerprinting enabled")
        
        # Initialize adaptive rate limiting if enabled
        if self.config.enable_adaptive_rate_limiting:
            logger.info("Adaptive rate limiting enabled")
        
        # Initialize captcha solver if enabled
        if self.config.enable_captcha_solver:
            logger.info("Captcha solver enabled")
        
        # Initialize monitoring if enabled
        if self.config.enable_monitoring:
            logger.info("Monitoring enabled")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status of all components.
        
        Returns:
            Dictionary with health status information.
        """
        return {
            "system_healthy": self.health_checker.is_system_healthy(),
            "component_status": self.health_checker.get_all_health_status(),
            "metrics": self.metrics_collector.get_metrics_summary(),
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current system metrics.
        
        Returns:
            Dictionary with system metrics.
        """
        return self.metrics_collector.get_metrics_summary()
    
    def reload_configuration(self) -> bool:
        """Reload configuration from environment variables.
        
        Returns:
            True if reload successful, False otherwise.
        """
        return self.config_manager.reload_from_env()
    
    def enable_feature(self, feature_name: str) -> None:
        """Enable a feature flag.
        
        Args:
            feature_name: Name of the feature to enable.
        """
        self.config_manager.update_feature_flag(feature_name, True)
    
    def disable_feature(self, feature_name: str) -> None:
        """Disable a feature flag.
        
        Args:
            feature_name: Name of the feature to disable.
        """
        self.config_manager.update_feature_flag(feature_name, False)
    
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled.
        
        Args:
            feature_name: Name of the feature to check.
            
        Returns:
            True if feature is enabled, False otherwise.
        """
        return self.config_manager.is_feature_enabled(feature_name)
    
    def perform_health_check(self) -> bool:
        """Perform comprehensive health check of all components.
        
        Returns:
            True if all components are healthy, False otherwise.
        """
        logger.info("Performing comprehensive health check...")
        
        # Check system resources
        self.health_checker.check_system_resources()
        
        # Check proxy connectivity
        for provider in self.config_manager.get_enabled_proxy_providers():
            self.health_checker.check_proxy_connectivity(provider.provider.value)
        
        # Check captcha services
        if self.config.enable_captcha_solver:
            for service in self.config.captcha_solver_services:
                self.health_checker.check_captcha_service(service)
        
        is_healthy = self.health_checker.is_system_healthy()
        logger.info(f"Health check complete. System healthy: {is_healthy}")
        
        return is_healthy
    
    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        self.metrics_collector.reset_metrics()
        logger.info("Metrics reset")
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration as dictionary.
        
        Returns:
            Dictionary representation of current configuration.
        """
        return self.config_manager.to_dict()
