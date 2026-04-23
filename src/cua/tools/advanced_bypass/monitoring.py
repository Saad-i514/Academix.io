"""Monitoring and health checking for advanced bypass system."""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger("Academix.AdvancedBypass")


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component_name: str
    is_healthy: bool
    status_message: str
    check_time: float = field(default_factory=time.time)
    response_time_ms: float = 0.0
    error_details: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "component": self.component_name,
            "healthy": self.is_healthy,
            "status": self.status_message,
            "check_time": self.check_time,
            "response_time_ms": self.response_time_ms,
            "error": self.error_details,
        }


class HealthChecker:
    """Performs health checks on bypass system components."""
    
    def __init__(self):
        """Initialize health checker."""
        self.last_check_time: Dict[str, float] = {}
        self.check_results: Dict[str, HealthCheckResult] = {}
        self.check_interval: int = 60  # seconds
    
    def check_proxy_connectivity(self, proxy_url: str) -> HealthCheckResult:
        """Check if a proxy is reachable."""
        start_time = time.time()
        try:
            # Simulate proxy connectivity check
            # In production, this would make actual HTTP requests
            response_time = (time.time() - start_time) * 1000
            
            result = HealthCheckResult(
                component_name=f"proxy_{proxy_url}",
                is_healthy=True,
                status_message="Proxy is reachable",
                response_time_ms=response_time,
            )
            self.check_results[result.component_name] = result
            return result
        except Exception as e:
            result = HealthCheckResult(
                component_name=f"proxy_{proxy_url}",
                is_healthy=False,
                status_message="Proxy connectivity failed",
                error_details=str(e),
            )
            self.check_results[result.component_name] = result
            return result
    
    def check_captcha_service(self, service_name: str) -> HealthCheckResult:
        """Check if captcha service is available."""
        start_time = time.time()
        try:
            # Simulate captcha service check
            response_time = (time.time() - start_time) * 1000
            
            result = HealthCheckResult(
                component_name=f"captcha_{service_name}",
                is_healthy=True,
                status_message=f"Captcha service {service_name} is available",
                response_time_ms=response_time,
            )
            self.check_results[result.component_name] = result
            return result
        except Exception as e:
            result = HealthCheckResult(
                component_name=f"captcha_{service_name}",
                is_healthy=False,
                status_message=f"Captcha service {service_name} check failed",
                error_details=str(e),
            )
            self.check_results[result.component_name] = result
            return result
    
    def check_system_resources(self) -> HealthCheckResult:
        """Check system resource availability."""
        try:
            import psutil
            
            # Check memory usage
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            
            is_healthy = memory.percent < 90 and cpu < 90
            status = f"Memory: {memory.percent:.1f}%, CPU: {cpu:.1f}%"
            
            result = HealthCheckResult(
                component_name="system_resources",
                is_healthy=is_healthy,
                status_message=status,
            )
        except ImportError:
            # psutil not available, assume healthy
            result = HealthCheckResult(
                component_name="system_resources",
                is_healthy=True,
                status_message="Resource monitoring unavailable",
            )
        
        self.check_results[result.component_name] = result
        return result
    
    def get_all_health_status(self) -> Dict[str, bool]:
        """Get health status of all components."""
        return {
            name: result.is_healthy
            for name, result in self.check_results.items()
        }
    
    def is_system_healthy(self) -> bool:
        """Check if entire system is healthy."""
        if not self.check_results:
            return True
        return all(result.is_healthy for result in self.check_results.values())


class MetricsCollector:
    """Collects and aggregates system metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, any] = {}
        self.start_time = time.time()
        self.request_times: List[float] = []
        self.success_count = 0
        self.failure_count = 0
        self.bot_detection_count = 0
    
    def record_request(self, success: bool, response_time_ms: float, 
                      bot_detected: bool = False) -> None:
        """Record a request metric."""
        self.request_times.append(response_time_ms)
        
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        if bot_detected:
            self.bot_detection_count += 1
        
        # Keep only last 1000 request times to avoid memory bloat
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
    
    def record_proxy_success(self, proxy_name: str) -> None:
        """Record successful proxy usage."""
        if "proxy_success_rates" not in self.metrics:
            self.metrics["proxy_success_rates"] = {}
        
        if proxy_name not in self.metrics["proxy_success_rates"]:
            self.metrics["proxy_success_rates"][proxy_name] = {"success": 0, "total": 0}
        
        self.metrics["proxy_success_rates"][proxy_name]["success"] += 1
        self.metrics["proxy_success_rates"][proxy_name]["total"] += 1
    
    def record_proxy_failure(self, proxy_name: str) -> None:
        """Record failed proxy usage."""
        if "proxy_success_rates" not in self.metrics:
            self.metrics["proxy_success_rates"] = {}
        
        if proxy_name not in self.metrics["proxy_success_rates"]:
            self.metrics["proxy_success_rates"][proxy_name] = {"success": 0, "total": 0}
        
        self.metrics["proxy_success_rates"][proxy_name]["total"] += 1
    
    def record_strategy_success(self, strategy_name: str) -> None:
        """Record successful strategy usage."""
        if "strategy_success_rates" not in self.metrics:
            self.metrics["strategy_success_rates"] = {}
        
        if strategy_name not in self.metrics["strategy_success_rates"]:
            self.metrics["strategy_success_rates"][strategy_name] = {"success": 0, "total": 0}
        
        self.metrics["strategy_success_rates"][strategy_name]["success"] += 1
        self.metrics["strategy_success_rates"][strategy_name]["total"] += 1
    
    def record_strategy_failure(self, strategy_name: str) -> None:
        """Record failed strategy usage."""
        if "strategy_success_rates" not in self.metrics:
            self.metrics["strategy_success_rates"] = {}
        
        if strategy_name not in self.metrics["strategy_success_rates"]:
            self.metrics["strategy_success_rates"][strategy_name] = {"success": 0, "total": 0}
        
        self.metrics["strategy_success_rates"][strategy_name]["total"] += 1
    
    def get_average_response_time(self) -> float:
        """Get average response time in milliseconds."""
        if not self.request_times:
            return 0.0
        return sum(self.request_times) / len(self.request_times)
    
    def get_success_rate(self) -> float:
        """Get overall success rate as percentage."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100
    
    def get_proxy_success_rates(self) -> Dict[str, float]:
        """Get success rate for each proxy."""
        rates = {}
        if "proxy_success_rates" in self.metrics:
            for proxy_name, counts in self.metrics["proxy_success_rates"].items():
                if counts["total"] > 0:
                    rates[proxy_name] = (counts["success"] / counts["total"]) * 100
        return rates
    
    def get_strategy_success_rates(self) -> Dict[str, float]:
        """Get success rate for each strategy."""
        rates = {}
        if "strategy_success_rates" in self.metrics:
            for strategy_name, counts in self.metrics["strategy_success_rates"].items():
                if counts["total"] > 0:
                    rates[strategy_name] = (counts["success"] / counts["total"]) * 100
        return rates
    
    def get_metrics_summary(self) -> Dict:
        """Get summary of all metrics."""
        uptime_seconds = time.time() - self.start_time
        
        return {
            "uptime_seconds": uptime_seconds,
            "total_requests": self.success_count + self.failure_count,
            "successful_requests": self.success_count,
            "failed_requests": self.failure_count,
            "bot_detection_count": self.bot_detection_count,
            "success_rate_percent": self.get_success_rate(),
            "average_response_time_ms": self.get_average_response_time(),
            "proxy_success_rates": self.get_proxy_success_rates(),
            "strategy_success_rates": self.get_strategy_success_rates(),
        }
    
    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics = {}
        self.request_times = []
        self.success_count = 0
        self.failure_count = 0
        self.bot_detection_count = 0
        self.start_time = time.time()
        logger.info("Metrics reset")
