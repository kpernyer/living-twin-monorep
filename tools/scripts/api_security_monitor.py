#!/usr/bin/env python3
"""
Living Twin - API Key Security Monitor

Detects potential API key theft through anomaly detection:
- Sudden usage spikes
- Unusual geographic locations
- Abnormal request patterns
- Concurrent usage from multiple IPs
- Rate limit violations
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
import argparse
import logging
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Try to import required libraries
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis library not installed. Real-time monitoring limited.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: Requests library not installed. IP geolocation limited.")


class ThreatLevel(Enum):
    """Security threat levels"""
    CRITICAL = "critical"  # Definite compromise
    HIGH = "high"         # Likely compromise
    MEDIUM = "medium"     # Suspicious activity
    LOW = "low"           # Unusual but explainable
    NONE = "none"         # Normal activity


class SecurityAction(Enum):
    """Actions to take on security threats"""
    BLOCK_IMMEDIATELY = "block_immediately"
    ROTATE_KEY = "rotate_key"
    THROTTLE = "throttle"
    ALERT_ONLY = "alert_only"
    MONITOR = "monitor"


@dataclass
class UsagePattern:
    """Normal usage pattern baseline"""
    avg_requests_per_hour: float
    avg_requests_per_day: float
    peak_hour_requests: float
    typical_hours: List[int]  # Hours of day when usually active
    typical_ips: Set[str]
    typical_countries: Set[str]
    typical_user_agents: Set[str]
    max_concurrent_ips: int


@dataclass
class SecurityEvent:
    """Security event detected"""
    timestamp: datetime
    threat_level: ThreatLevel
    event_type: str
    description: str
    api_key_hash: str
    source_ip: Optional[str]
    country: Optional[str]
    requests_count: int
    recommended_action: SecurityAction
    evidence: Dict[str, Any]


class APISecurityMonitor:
    """Monitor API keys for potential theft and abuse"""
    
    def __init__(self, environment: str):
        self.environment = environment
        self.logger = self._setup_logging()
        self.redis_client = self._setup_redis() if REDIS_AVAILABLE else None
        self.usage_baselines = {}
        self.security_events = []
        
        # Security thresholds
        self.thresholds = {
            "spike_multiplier": 10,  # 10x normal usage
            "burst_requests": 100,   # 100 requests in 1 minute
            "max_ips_per_key": 3,    # Max concurrent IPs
            "geo_distance_km": 1000, # Suspicious if > 1000km apart
            "new_country_threshold": 0.8,  # 80% requests from new country
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger("APISecurityMonitor")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        # Also log to file for audit trail
        file_handler = logging.FileHandler(f"security_audit_{self.environment}.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def _setup_redis(self):
        """Set up Redis connection for real-time monitoring"""
        if not REDIS_AVAILABLE:
            return None
        
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            client = redis.from_url(redis_url, decode_responses=True)
            client.ping()
            return client
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}")
            return None
    
    def hash_api_key(self, api_key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()[:16]
    
    def track_request(self, api_key: str, ip: str, user_agent: str, 
                     endpoint: str, timestamp: Optional[datetime] = None):
        """Track an API request for pattern analysis"""
        if not self.redis_client:
            return
        
        timestamp = timestamp or datetime.now()
        key_hash = self.hash_api_key(api_key)
        
        # Store request data in Redis
        request_data = {
            "ip": ip,
            "user_agent": user_agent,
            "endpoint": endpoint,
            "timestamp": timestamp.isoformat()
        }
        
        # Track in various dimensions
        pipe = self.redis_client.pipeline()
        
        # Requests per minute
        minute_key = f"requests:{key_hash}:{timestamp.strftime('%Y%m%d%H%M')}"
        pipe.incr(minute_key)
        pipe.expire(minute_key, 3600)  # Keep for 1 hour
        
        # IPs per key
        ip_key = f"ips:{key_hash}:{timestamp.strftime('%Y%m%d%H')}"
        pipe.sadd(ip_key, ip)
        pipe.expire(ip_key, 86400)  # Keep for 1 day
        
        # Request log
        log_key = f"log:{key_hash}"
        pipe.lpush(log_key, json.dumps(request_data))
        pipe.ltrim(log_key, 0, 999)  # Keep last 1000 requests
        
        pipe.execute()
    
    def detect_usage_spike(self, api_key: str) -> Optional[SecurityEvent]:
        """Detect sudden spikes in API usage"""
        if not self.redis_client:
            return None
        
        key_hash = self.hash_api_key(api_key)
        now = datetime.now()
        
        # Get requests in last minute
        minute_key = f"requests:{key_hash}:{now.strftime('%Y%m%d%H%M')}"
        current_requests = int(self.redis_client.get(minute_key) or 0)
        
        # Get average requests per minute (baseline)
        baseline = self._get_baseline(key_hash)
        avg_per_minute = baseline.avg_requests_per_hour / 60 if baseline else 10
        
        # Check for spike
        if current_requests > max(self.thresholds["burst_requests"], 
                                  avg_per_minute * self.thresholds["spike_multiplier"]):
            return SecurityEvent(
                timestamp=now,
                threat_level=ThreatLevel.HIGH,
                event_type="usage_spike",
                description=f"Detected {current_requests} requests in 1 minute (normal: {avg_per_minute:.1f})",
                api_key_hash=key_hash,
                source_ip=None,
                country=None,
                requests_count=current_requests,
                recommended_action=SecurityAction.THROTTLE,
                evidence={
                    "current_rpm": current_requests,
                    "baseline_rpm": avg_per_minute,
                    "spike_factor": current_requests / max(avg_per_minute, 1)
                }
            )
        
        return None
    
    def detect_concurrent_usage(self, api_key: str) -> Optional[SecurityEvent]:
        """Detect API key being used from multiple IPs simultaneously"""
        if not self.redis_client:
            return None
        
        key_hash = self.hash_api_key(api_key)
        now = datetime.now()
        
        # Get unique IPs in last hour
        ip_key = f"ips:{key_hash}:{now.strftime('%Y%m%d%H')}"
        current_ips = self.redis_client.smembers(ip_key)
        
        if len(current_ips) > self.thresholds["max_ips_per_key"]:
            # Check if these IPs are geographically distributed
            countries = set()
            for ip in current_ips:
                country = self._get_ip_country(ip)
                if country:
                    countries.add(country)
            
            threat_level = ThreatLevel.CRITICAL if len(countries) > 2 else ThreatLevel.HIGH
            
            return SecurityEvent(
                timestamp=now,
                threat_level=threat_level,
                event_type="concurrent_usage",
                description=f"API key used from {len(current_ips)} different IPs in {len(countries)} countries",
                api_key_hash=key_hash,
                source_ip=", ".join(list(current_ips)[:5]),  # Show first 5 IPs
                country=", ".join(countries),
                requests_count=0,
                recommended_action=SecurityAction.BLOCK_IMMEDIATELY if threat_level == ThreatLevel.CRITICAL else SecurityAction.ROTATE_KEY,
                evidence={
                    "unique_ips": len(current_ips),
                    "ip_list": list(current_ips),
                    "countries": list(countries)
                }
            )
        
        return None
    
    def detect_geographic_anomaly(self, api_key: str, current_ip: str) -> Optional[SecurityEvent]:
        """Detect usage from unusual geographic locations"""
        if not REQUESTS_AVAILABLE:
            return None
        
        key_hash = self.hash_api_key(api_key)
        current_country = self._get_ip_country(current_ip)
        
        if not current_country:
            return None
        
        baseline = self._get_baseline(key_hash)
        if baseline and baseline.typical_countries:
            if current_country not in baseline.typical_countries:
                # Check recent usage pattern
                recent_countries = self._get_recent_countries(key_hash)
                new_country_ratio = recent_countries.get(current_country, 0) / sum(recent_countries.values()) if recent_countries else 1
                
                if new_country_ratio > self.thresholds["new_country_threshold"]:
                    return SecurityEvent(
                        timestamp=datetime.now(),
                        threat_level=ThreatLevel.HIGH,
                        event_type="geographic_anomaly",
                        description=f"Sudden usage from new country: {current_country} ({new_country_ratio*100:.1f}% of recent requests)",
                        api_key_hash=key_hash,
                        source_ip=current_ip,
                        country=current_country,
                        requests_count=recent_countries.get(current_country, 0),
                        recommended_action=SecurityAction.ROTATE_KEY,
                        evidence={
                            "new_country": current_country,
                            "typical_countries": list(baseline.typical_countries),
                            "recent_distribution": recent_countries
                        }
                    )
        
        return None
    
    def detect_pattern_anomaly(self, api_key: str, user_agent: str, 
                              endpoint: str, timestamp: datetime) -> Optional[SecurityEvent]:
        """Detect unusual usage patterns (time, user agent, endpoints)"""
        key_hash = self.hash_api_key(api_key)
        baseline = self._get_baseline(key_hash)
        
        if not baseline:
            return None
        
        anomalies = []
        
        # Check time anomaly
        current_hour = timestamp.hour
        if baseline.typical_hours and current_hour not in baseline.typical_hours:
            anomalies.append(f"Unusual time: {current_hour}:00 (typical: {baseline.typical_hours})")
        
        # Check user agent anomaly
        if baseline.typical_user_agents and user_agent not in baseline.typical_user_agents:
            anomalies.append(f"New user agent: {user_agent[:50]}")
        
        # Check for suspicious patterns
        suspicious_patterns = [
            "bot", "scraper", "crawler", "hack", "exploit",
            "sqlmap", "nikto", "burp", "metasploit"
        ]
        
        if any(pattern in user_agent.lower() for pattern in suspicious_patterns):
            anomalies.append(f"Suspicious user agent detected")
        
        if len(anomalies) >= 2:
            return SecurityEvent(
                timestamp=timestamp,
                threat_level=ThreatLevel.MEDIUM if len(anomalies) == 2 else ThreatLevel.HIGH,
                event_type="pattern_anomaly",
                description="; ".join(anomalies),
                api_key_hash=key_hash,
                source_ip=None,
                country=None,
                requests_count=0,
                recommended_action=SecurityAction.ALERT_ONLY if len(anomalies) == 2 else SecurityAction.THROTTLE,
                evidence={
                    "anomalies": anomalies,
                    "user_agent": user_agent,
                    "endpoint": endpoint,
                    "hour": current_hour
                }
            )
        
        return None
    
    def _get_ip_country(self, ip: str) -> Optional[str]:
        """Get country from IP address"""
        if not REQUESTS_AVAILABLE:
            return None
        
        # Cache check
        cache_key = f"ip_country:{ip}"
        if self.redis_client:
            cached = self.redis_client.get(cache_key)
            if cached:
                return cached
        
        try:
            # Use a free IP geolocation service
            response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
            if response.status_code == 200:
                data = response.json()
                country = data.get("country", "Unknown")
                
                # Cache result
                if self.redis_client:
                    self.redis_client.setex(cache_key, 86400, country)  # Cache for 1 day
                
                return country
        except Exception as e:
            self.logger.debug(f"Failed to get country for IP {ip}: {e}")
        
        return None
    
    def _get_baseline(self, key_hash: str) -> Optional[UsagePattern]:
        """Get baseline usage pattern for an API key"""
        # In production, this would load from a database
        # For now, return a mock baseline
        if key_hash not in self.usage_baselines:
            self.usage_baselines[key_hash] = UsagePattern(
                avg_requests_per_hour=100,
                avg_requests_per_day=2000,
                peak_hour_requests=500,
                typical_hours=list(range(8, 20)),  # 8 AM to 8 PM
                typical_ips={"192.168.1.1", "10.0.0.1"},
                typical_countries={"United States", "United Kingdom"},
                typical_user_agents={"MyApp/1.0", "Mozilla/5.0"},
                max_concurrent_ips=2
            )
        
        return self.usage_baselines.get(key_hash)
    
    def _get_recent_countries(self, key_hash: str) -> Dict[str, int]:
        """Get distribution of countries in recent requests"""
        if not self.redis_client:
            return {}
        
        countries = defaultdict(int)
        log_key = f"log:{key_hash}"
        recent_logs = self.redis_client.lrange(log_key, 0, 99)  # Last 100 requests
        
        for log_entry in recent_logs:
            try:
                data = json.loads(log_entry)
                ip = data.get("ip")
                if ip:
                    country = self._get_ip_country(ip)
                    if country:
                        countries[country] += 1
            except json.JSONDecodeError:
                continue
        
        return dict(countries)
    
    def check_all_threats(self, api_key: str, ip: str, user_agent: str, 
                         endpoint: str) -> List[SecurityEvent]:
        """Run all security checks for a request"""
        events = []
        timestamp = datetime.now()
        
        # Track the request first
        self.track_request(api_key, ip, user_agent, endpoint, timestamp)
        
        # Run all detections
        spike_event = self.detect_usage_spike(api_key)
        if spike_event:
            events.append(spike_event)
        
        concurrent_event = self.detect_concurrent_usage(api_key)
        if concurrent_event:
            events.append(concurrent_event)
        
        geo_event = self.detect_geographic_anomaly(api_key, ip)
        if geo_event:
            events.append(geo_event)
        
        pattern_event = self.detect_pattern_anomaly(api_key, user_agent, endpoint, timestamp)
        if pattern_event:
            events.append(pattern_event)
        
        # Log and handle events
        for event in events:
            self.handle_security_event(event)
        
        return events
    
    def handle_security_event(self, event: SecurityEvent):
        """Handle a security event based on threat level"""
        self.security_events.append(event)
        
        # Log the event
        self.logger.warning(f"SECURITY EVENT: {event.event_type} - {event.description}")
        
        # Take action based on recommendation
        if event.recommended_action == SecurityAction.BLOCK_IMMEDIATELY:
            self.block_api_key(event.api_key_hash)
            self.send_critical_alert(event)
        elif event.recommended_action == SecurityAction.ROTATE_KEY:
            self.initiate_key_rotation(event.api_key_hash)
            self.send_alert(event)
        elif event.recommended_action == SecurityAction.THROTTLE:
            self.apply_throttling(event.api_key_hash)
            self.send_alert(event)
        elif event.recommended_action == SecurityAction.ALERT_ONLY:
            self.send_alert(event)
    
    def block_api_key(self, key_hash: str):
        """Immediately block an API key"""
        self.logger.critical(f"BLOCKING API KEY: {key_hash}")
        
        if self.redis_client:
            # Add to blocklist
            self.redis_client.sadd("blocked_keys", key_hash)
            
            # Set expiry for automatic unblock after investigation
            block_key = f"blocked:{key_hash}"
            self.redis_client.setex(block_key, 3600, "blocked")  # Block for 1 hour
    
    def initiate_key_rotation(self, key_hash: str):
        """Initiate API key rotation"""
        self.logger.warning(f"INITIATING KEY ROTATION: {key_hash}")
        
        if self.redis_client:
            # Mark for rotation
            self.redis_client.sadd("keys_to_rotate", key_hash)
    
    def apply_throttling(self, key_hash: str):
        """Apply rate limiting to suspicious API key"""
        self.logger.warning(f"APPLYING THROTTLING: {key_hash}")
        
        if self.redis_client:
            # Reduce rate limit
            throttle_key = f"throttled:{key_hash}"
            self.redis_client.setex(throttle_key, 1800, "10")  # 10 requests per minute for 30 minutes
    
    def send_alert(self, event: SecurityEvent):
        """Send security alert"""
        subject = f"[{event.threat_level.value.upper()}] API Security Alert - {event.event_type}"
        
        body = f"""
        Security Event Detected
        =======================
        
        Time: {event.timestamp}
        Type: {event.event_type}
        Threat Level: {event.threat_level.value}
        Description: {event.description}
        
        API Key (hash): {event.api_key_hash}
        Source IP: {event.source_ip or 'N/A'}
        Country: {event.country or 'N/A'}
        
        Recommended Action: {event.recommended_action.value}
        
        Evidence:
        {json.dumps(event.evidence, indent=2)}
        
        Please investigate immediately.
        """
        
        self._send_email(subject, body)
        self._send_slack(subject, body)
    
    def send_critical_alert(self, event: SecurityEvent):
        """Send critical security alert with immediate notifications"""
        # Send regular alert
        self.send_alert(event)
        
        # Additional critical notifications
        self._send_sms(f"CRITICAL: API key compromised - {event.api_key_hash[:8]}... BLOCKED")
        self._trigger_pagerduty(event)
    
    def _send_email(self, subject: str, body: str):
        """Send email alert"""
        # Implementation would use SMTP or email service
        self.logger.info(f"EMAIL ALERT: {subject}")
    
    def _send_slack(self, subject: str, body: str):
        """Send Slack alert"""
        # Implementation would use Slack webhook
        self.logger.info(f"SLACK ALERT: {subject}")
    
    def _send_sms(self, message: str):
        """Send SMS for critical alerts"""
        # Implementation would use Twilio or similar
        self.logger.critical(f"SMS ALERT: {message}")
    
    def _trigger_pagerduty(self, event: SecurityEvent):
        """Trigger PagerDuty for critical incidents"""
        # Implementation would use PagerDuty API
        self.logger.critical(f"PAGERDUTY TRIGGERED: {event.event_type}")
    
    def generate_security_report(self) -> str:
        """Generate security report"""
        report = []
        report.append("=" * 70)
        report.append(f"API SECURITY REPORT - {self.environment.upper()}")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 70)
        report.append("")
        
        if not self.security_events:
            report.append("No security events detected.")
        else:
            # Group events by threat level
            by_level = defaultdict(list)
            for event in self.security_events:
                by_level[event.threat_level].append(event)
            
            for level in [ThreatLevel.CRITICAL, ThreatLevel.HIGH, 
                         ThreatLevel.MEDIUM, ThreatLevel.LOW]:
                events = by_level.get(level, [])
                if events:
                    report.append(f"\n{level.value.upper()} THREATS ({len(events)})")
                    report.append("-" * 40)
                    for event in events[:5]:  # Show first 5
                        report.append(f"• {event.timestamp.strftime('%H:%M:%S')} - {event.event_type}")
                        report.append(f"  {event.description}")
                        report.append(f"  Action: {event.recommended_action.value}")
                        report.append("")
        
        # Statistics
        if self.redis_client:
            report.append("\nCURRENT STATUS")
            report.append("-" * 40)
            blocked_keys = self.redis_client.scard("blocked_keys")
            throttled_keys = len([k for k in self.redis_client.keys("throttled:*")])
            report.append(f"Blocked API Keys: {blocked_keys}")
            report.append(f"Throttled API Keys: {throttled_keys}")
        
        report.append("\n" + "=" * 70)
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Monitor API keys for security threats")
    parser.add_argument("--environment", required=True,
                       choices=["production", "staging", "development", "test"],
                       help="Environment to monitor")
    parser.add_argument("--api-key", help="Specific API key to check")
    parser.add_argument("--simulate", action="store_true",
                       help="Simulate attack patterns for testing")
    parser.add_argument("--report", action="store_true",
                       help="Generate security report")
    parser.add_argument("--continuous", action="store_true",
                       help="Run continuous monitoring")
    
    args = parser.parse_args()
    
    monitor = APISecurityMonitor(args.environment)
    
    if args.simulate:
        # Simulate various attack patterns for testing
        print("Simulating attack patterns...")
        
        # Simulate usage spike
        test_key = "test-api-key-123"
        for _ in range(150):
            monitor.track_request(test_key, "192.168.1.100", "Bot/1.0", "/api/endpoint")
        
        # Simulate concurrent usage from multiple IPs
        for i in range(5):
            monitor.track_request(test_key, f"10.0.0.{i}", "Chrome/96.0", "/api/data")
        
        # Check for threats
        events = monitor.check_all_threats(test_key, "192.168.1.100", "Bot/1.0", "/api/endpoint")
        
        print(f"Detected {len(events)} security events")
        for event in events:
            print(f"  - {event.threat_level.value}: {event.event_type} - {event.description}")
    
    elif args.report:
        print(monitor.generate_security_report())
    
    elif args.continuous:
        print(f"Starting continuous monitoring for {args.environment} environment...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # In production, this would monitor actual API traffic
                # For now, just sleep and periodically check
                time.sleep(60)
                
                # Check for any flagged keys
                if monitor.redis_client:
                    blocked = monitor.redis_client.scard("blocked_keys")
                    if blocked > 0:
                        print(f"⚠️  {blocked} API keys currently blocked")
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
    
    else:
        if args.api_key:
            # Check specific API key
            events = monitor.check_all_threats(
                args.api_key, "0.0.0.0", "Unknown", "/api/check"
            )
            if events:
                print(f"Found {len(events)} security issues:")
                for event in events:
                    print(f"  - {event.threat_level.value}: {event.description}")
            else:
                print("No security issues detected")
        else:
            print("Please specify --api-key, --simulate, --report, or --continuous")


if __name__ == "__main__":
    main()
