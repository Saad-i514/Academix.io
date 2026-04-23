"""Proxy management infrastructure for advanced bypass system."""

import logging
import random
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger("Academix.AdvancedBypass")


@dataclass
class ProxyInstance:
    """Represents a single proxy instance."""
    proxy_id: str
    provider: str
    ip_address: str
    port: int
    region: str
    is_active: bool = True
    success_count: int = 0
    failure_count: int = 0
    last_used_time: float = 0.0
    last_health_check: float = 0.0
    consecutive_failures: int = 0
    
    def get_success_rate(self) -> float:
        """Calculate success rate for this proxy."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100
    
    def get_proxy_url(self) -> str:
        """Get proxy URL."""
        return f"http://{self.ip_address}:{self.port}"
    
    def mark_success(self) -> None:
        """Mark proxy as successfully used."""
        self.success_count += 1
        self.consecutive_failures = 0
        self.last_used_time = time.time()
    
    def mark_failure(self) -> None:
        """Mark proxy as failed."""
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_used_time = time.time()
    
    def is_healthy(self, max_consecutive_failures: int = 5) -> bool:
        """Check if proxy is healthy."""
        if not self.is_active:
            return False
        if self.consecutive_failures >= max_consecutive_failures:
            return False
        return True


class ProxyRotationStrategy(Enum):
    """Proxy rotation strategies."""
    ROUND_ROBIN = "round_robin"
    RANDOM = "random"
    PRIORITY = "priority"
    LEAST_USED = "least_used"
    BEST_PERFORMING = "best_performing"


class ProxyManager:
    """Manages proxy pool and rotation."""
    
    def __init__(self, min_pool_size: int = 10, rotation_strategy: str = "round_robin"):
        """Initialize proxy manager.
        
        Args:
            min_pool_size: Minimum number of proxies to maintain.
            rotation_strategy: Strategy for proxy rotation.
        """
        self.min_pool_size = min_pool_size
        self.rotation_strategy = ProxyRotationStrategy(rotation_strategy)
        self.proxy_pool: Dict[str, ProxyInstance] = {}
        self.current_proxy_index = 0
        self.regions = ["US", "EU", "ASIA"]
        self.region_index = 0
    
    def add_proxy(self, proxy_id: str, provider: str, ip_address: str, 
                  port: int, region: str) -> ProxyInstance:
        """Add a proxy to the pool.
        
        Args:
            proxy_id: Unique identifier for the proxy.
            provider: Proxy provider name.
            ip_address: IP address of the proxy.
            port: Port number of the proxy.
            region: Geographic region of the proxy.
            
        Returns:
            ProxyInstance object.
        """
        proxy = ProxyInstance(
            proxy_id=proxy_id,
            provider=provider,
            ip_address=ip_address,
            port=port,
            region=region,
        )
        self.proxy_pool[proxy_id] = proxy
        logger.info(f"Added proxy {proxy_id} ({region})")
        return proxy
    
    def remove_proxy(self, proxy_id: str) -> bool:
        """Remove a proxy from the pool.
        
        Args:
            proxy_id: ID of proxy to remove.
            
        Returns:
            True if removed, False if not found.
        """
        if proxy_id in self.proxy_pool:
            del self.proxy_pool[proxy_id]
            logger.info(f"Removed proxy {proxy_id}")
            return True
        return False
    
    def get_next_proxy(self) -> Optional[ProxyInstance]:
        """Get next proxy based on rotation strategy.
        
        Returns:
            ProxyInstance or None if no healthy proxies available.
        """
        healthy_proxies = self.get_healthy_proxies()
        
        if not healthy_proxies:
            logger.warning("No healthy proxies available")
            return None
        
        if self.rotation_strategy == ProxyRotationStrategy.ROUND_ROBIN:
            proxy = healthy_proxies[self.current_proxy_index % len(healthy_proxies)]
            self.current_proxy_index += 1
        
        elif self.rotation_strategy == ProxyRotationStrategy.RANDOM:
            proxy = random.choice(healthy_proxies)
        
        elif self.rotation_strategy == ProxyRotationStrategy.PRIORITY:
            # Sort by region priority and success rate
            proxy = sorted(
                healthy_proxies,
                key=lambda p: (-self._get_region_priority(p.region), -p.get_success_rate())
            )[0]
        
        elif self.rotation_strategy == ProxyRotationStrategy.LEAST_USED:
            # Use proxy with least usage
            proxy = min(healthy_proxies, key=lambda p: p.success_count + p.failure_count)
        
        elif self.rotation_strategy == ProxyRotationStrategy.BEST_PERFORMING:
            # Use proxy with best success rate
            proxy = max(healthy_proxies, key=lambda p: p.get_success_rate())
        
        else:
            proxy = random.choice(healthy_proxies)
        
        logger.debug(f"Selected proxy {proxy.proxy_id} ({proxy.region})")
        return proxy
    
    def get_healthy_proxies(self) -> List[ProxyInstance]:
        """Get list of all healthy proxies.
        
        Returns:
            List of healthy ProxyInstance objects.
        """
        return [p for p in self.proxy_pool.values() if p.is_healthy()]
    
    def get_proxy_by_id(self, proxy_id: str) -> Optional[ProxyInstance]:
        """Get proxy by ID.
        
        Args:
            proxy_id: ID of proxy to retrieve.
            
        Returns:
            ProxyInstance or None if not found.
        """
        return self.proxy_pool.get(proxy_id)
    
    def mark_proxy_success(self, proxy_id: str) -> None:
        """Mark proxy as successfully used.
        
        Args:
            proxy_id: ID of proxy to mark.
        """
        proxy = self.get_proxy_by_id(proxy_id)
        if proxy:
            proxy.mark_success()
    
    def mark_proxy_failure(self, proxy_id: str) -> None:
        """Mark proxy as failed.
        
        Args:
            proxy_id: ID of proxy to mark.
        """
        proxy = self.get_proxy_by_id(proxy_id)
        if proxy:
            proxy.mark_failure()
    
    def get_pool_statistics(self) -> Dict:
        """Get statistics about the proxy pool.
        
        Returns:
            Dictionary with pool statistics.
        """
        total_proxies = len(self.proxy_pool)
        healthy_proxies = len(self.get_healthy_proxies())
        
        success_rates = {}
        for proxy_id, proxy in self.proxy_pool.items():
            success_rates[proxy_id] = {
                "success_rate": proxy.get_success_rate(),
                "success_count": proxy.success_count,
                "failure_count": proxy.failure_count,
                "region": proxy.region,
                "is_healthy": proxy.is_healthy(),
            }
        
        return {
            "total_proxies": total_proxies,
            "healthy_proxies": healthy_proxies,
            "pool_health_percent": (healthy_proxies / total_proxies * 100) if total_proxies > 0 else 0,
            "proxy_details": success_rates,
        }
    
    def get_geographic_distribution(self) -> Dict[str, int]:
        """Get distribution of proxies by region.
        
        Returns:
            Dictionary with region counts.
        """
        distribution = {}
        for proxy in self.proxy_pool.values():
            distribution[proxy.region] = distribution.get(proxy.region, 0) + 1
        return distribution
    
    def rotate_geographic_region(self) -> str:
        """Get next geographic region in rotation.
        
        Returns:
            Region name.
        """
        region = self.regions[self.region_index % len(self.regions)]
        self.region_index += 1
        return region
    
    def get_proxies_by_region(self, region: str) -> List[ProxyInstance]:
        """Get all proxies in a specific region.
        
        Args:
            region: Region name.
            
        Returns:
            List of ProxyInstance objects in the region.
        """
        return [p for p in self.proxy_pool.values() if p.region == region]
    
    def deactivate_proxy(self, proxy_id: str) -> bool:
        """Deactivate a proxy.
        
        Args:
            proxy_id: ID of proxy to deactivate.
            
        Returns:
            True if deactivated, False if not found.
        """
        proxy = self.get_proxy_by_id(proxy_id)
        if proxy:
            proxy.is_active = False
            logger.warning(f"Deactivated proxy {proxy_id}")
            return True
        return False
    
    def reactivate_proxy(self, proxy_id: str) -> bool:
        """Reactivate a proxy.
        
        Args:
            proxy_id: ID of proxy to reactivate.
            
        Returns:
            True if reactivated, False if not found.
        """
        proxy = self.get_proxy_by_id(proxy_id)
        if proxy:
            proxy.is_active = True
            proxy.consecutive_failures = 0
            logger.info(f"Reactivated proxy {proxy_id}")
            return True
        return False
    
    def _get_region_priority(self, region: str) -> int:
        """Get priority for a region (higher = better).
        
        Args:
            region: Region name.
            
        Returns:
            Priority value.
        """
        priority_map = {"US": 3, "EU": 2, "ASIA": 1}
        return priority_map.get(region, 0)
    
    def get_pool_size(self) -> int:
        """Get current pool size.
        
        Returns:
            Number of proxies in pool.
        """
        return len(self.proxy_pool)
    
    def is_pool_sufficient(self) -> bool:
        """Check if pool size meets minimum requirement.
        
        Returns:
            True if pool is sufficient, False otherwise.
        """
        return len(self.get_healthy_proxies()) >= self.min_pool_size
