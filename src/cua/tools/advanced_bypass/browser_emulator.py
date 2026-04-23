"""Advanced browser emulation for realistic YouTube access."""

import logging
import random
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("Academix.AdvancedBypass")


class BrowserType(Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"


@dataclass
class BrowserProfile:
    """Browser profile with realistic characteristics."""
    browser_type: BrowserType
    user_agent: str
    viewport_width: int
    viewport_height: int
    device_pixel_ratio: float
    platform: str
    languages: List[str]
    timezone: str
    webgl_vendor: str
    webgl_renderer: str
    
    def to_headers(self) -> Dict[str, str]:
        """Convert profile to HTTP headers."""
        return {
            "User-Agent": self.user_agent,
            "Accept-Language": ",".join(self.languages),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }


class BrowserEmulator:
    """Emulates realistic browser behavior for YouTube access."""
    
    def __init__(self):
        """Initialize browser emulator."""
        self.browser_profiles = self._create_browser_profiles()
        self.current_profile: Optional[BrowserProfile] = None
        self.profile_rotation_count = 0
    
    def _create_browser_profiles(self) -> Dict[BrowserType, List[BrowserProfile]]:
        """Create realistic browser profiles."""
        profiles = {
            BrowserType.CHROME: [
                BrowserProfile(
                    browser_type=BrowserType.CHROME,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport_width=1920,
                    viewport_height=1080,
                    device_pixel_ratio=1.0,
                    platform="Win32",
                    languages=["en-US", "en"],
                    timezone="America/New_York",
                    webgl_vendor="Google Inc.",
                    webgl_renderer="ANGLE (Intel HD Graphics 630)",
                ),
            ],
            BrowserType.FIREFOX: [
                BrowserProfile(
                    browser_type=BrowserType.FIREFOX,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
                    viewport_width=1920,
                    viewport_height=1080,
                    device_pixel_ratio=1.0,
                    platform="Win32",
                    languages=["en-US", "en"],
                    timezone="America/Chicago",
                    webgl_vendor="Mozilla",
                    webgl_renderer="WebGL 2.0 (OpenGL 4.6)",
                ),
            ],
            BrowserType.SAFARI: [
                BrowserProfile(
                    browser_type=BrowserType.SAFARI,
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
                    viewport_width=1440,
                    viewport_height=900,
                    device_pixel_ratio=2.0,
                    platform="MacIntel",
                    languages=["en-US", "en"],
                    timezone="America/Los_Angeles",
                    webgl_vendor="Apple Inc.",
                    webgl_renderer="Apple M1",
                ),
            ],
        }
        return profiles
    
    def get_random_profile(self) -> BrowserProfile:
        """Get a random browser profile."""
        all_profiles = []
        for profiles_list in self.browser_profiles.values():
            all_profiles.extend(profiles_list)
        
        profile = random.choice(all_profiles)
        self.current_profile = profile
        self.profile_rotation_count += 1
        logger.debug(f"Selected browser profile: {profile.browser_type.value}")
        return profile
    
    def get_profile_by_type(self, browser_type: BrowserType) -> BrowserProfile:
        """Get a profile for specific browser type."""
        profiles = self.browser_profiles.get(browser_type, [])
        if not profiles:
            return self.get_random_profile()
        
        profile = random.choice(profiles)
        self.current_profile = profile
        return profile
    
    def get_current_profile(self) -> Optional[BrowserProfile]:
        """Get currently active profile."""
        return self.current_profile
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for current profile."""
        if not self.current_profile:
            self.get_random_profile()
        
        return self.current_profile.to_headers()
    
    def simulate_mouse_movement(self) -> Dict:
        """Simulate realistic mouse movement pattern."""
        movements = []
        current_x, current_y = random.randint(0, 1920), random.randint(0, 1080)
        
        for _ in range(random.randint(5, 15)):
            new_x = current_x + random.randint(-100, 100)
            new_y = current_y + random.randint(-100, 100)
            movements.append({"x": new_x, "y": new_y})
            current_x, current_y = new_x, new_y
        
        return {"movements": movements}
    
    def simulate_typing_pattern(self, text: str) -> Dict:
        """Simulate realistic typing pattern."""
        typing_times = []
        for _ in range(len(text)):
            # Realistic typing speed: 50-150ms per character
            typing_times.append(random.uniform(0.05, 0.15))
        
        return {"typing_times": typing_times, "total_time": sum(typing_times)}
    
    def get_interaction_delay(self) -> float:
        """Get realistic interaction delay in seconds."""
        # Human-like delays: 2-8 seconds
        return random.uniform(2.0, 8.0)
    
    def get_page_load_delay(self) -> float:
        """Get realistic page load delay in seconds."""
        # Simulate page load time: 1-5 seconds
        return random.uniform(1.0, 5.0)
    
    def get_video_watch_pattern(self, video_duration_seconds: int) -> Dict:
        """Generate realistic video watching pattern."""
        pattern = {
            "watch_duration": random.uniform(0.3, 0.9) * video_duration_seconds,
            "pauses": random.randint(0, 5),
            "seeks": random.randint(0, 3),
            "volume_changes": random.randint(0, 2),
            "fullscreen_toggles": random.randint(0, 1),
        }
        return pattern
    
    def get_fingerprint_data(self) -> Dict:
        """Get browser fingerprint data."""
        if not self.current_profile:
            self.get_random_profile()
        
        return {
            "browser_type": self.current_profile.browser_type.value,
            "user_agent": self.current_profile.user_agent,
            "viewport": {
                "width": self.current_profile.viewport_width,
                "height": self.current_profile.viewport_height,
            },
            "device_pixel_ratio": self.current_profile.device_pixel_ratio,
            "platform": self.current_profile.platform,
            "languages": self.current_profile.languages,
            "timezone": self.current_profile.timezone,
            "webgl": {
                "vendor": self.current_profile.webgl_vendor,
                "renderer": self.current_profile.webgl_renderer,
            },
        }
