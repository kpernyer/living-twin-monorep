#!/usr/bin/env python3
"""
Living Twin - Cost Monitoring and Budget Control

This script monitors API usage costs across different environments and
implements budget controls to prevent overspending.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import argparse
import logging
from dataclasses import dataclass
from enum import Enum

# Try to import Google Cloud libraries
try:
    from google.cloud import billing_v1
    from google.cloud import monitoring_v3
    GCLOUD_AVAILABLE = True
except ImportError:
    GCLOUD_AVAILABLE = False
    print("Warning: Google Cloud libraries not installed. Some features will be limited.")

# Try to import OpenAI for usage tracking
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI library not installed. OpenAI cost tracking will be limited.")


class Environment(Enum):
    """Environment types"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TEST = "test"


class CostAction(Enum):
    """Actions to take when budget limits are reached"""
    THROTTLE = "throttle"
    BLOCK = "block"
    ALERT_ONLY = "alert-only"


@dataclass
class BudgetConfig:
    """Budget configuration for an environment"""
    environment: Environment
    monthly_limit: float
    alert_thresholds: List[int]
    cost_cap_action: CostAction
    

@dataclass
class ServiceCost:
    """Cost breakdown for a service"""
    service_name: str
    current_month_cost: float
    projected_month_cost: float
    daily_average: float
    last_24h_cost: float


class CostMonitor:
    """Monitor and control costs across environments"""
    
    def __init__(self, project_id: str, environment: str):
        self.project_id = project_id
        self.environment = Environment(environment)
        self.logger = self._setup_logging()
        self.budget_config = self._load_budget_config()
        
        if GCLOUD_AVAILABLE:
            self.billing_client = billing_v1.CloudBillingClient()
            self.monitoring_client = monitoring_v3.MetricServiceClient()
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration"""
        logger = logging.getLogger("CostMonitor")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _load_budget_config(self) -> BudgetConfig:
        """Load budget configuration from environment variables"""
        env_prefix = self.environment.value.upper()
        
        # Load from environment variables or use defaults
        configs = {
            Environment.PRODUCTION: BudgetConfig(
                environment=Environment.PRODUCTION,
                monthly_limit=float(os.getenv("PROD_MAX_MONTHLY_COST", "5000")),
                alert_thresholds=[50, 75, 90, 95],
                cost_cap_action=CostAction(os.getenv("PROD_COST_CAP_ACTION", "throttle"))
            ),
            Environment.STAGING: BudgetConfig(
                environment=Environment.STAGING,
                monthly_limit=float(os.getenv("STAGING_MAX_MONTHLY_COST", "500")),
                alert_thresholds=[75, 90],
                cost_cap_action=CostAction(os.getenv("STAGING_COST_CAP_ACTION", "throttle"))
            ),
            Environment.DEVELOPMENT: BudgetConfig(
                environment=Environment.DEVELOPMENT,
                monthly_limit=float(os.getenv("DEV_MAX_MONTHLY_COST", "100")),
                alert_thresholds=[90],
                cost_cap_action=CostAction(os.getenv("DEV_COST_CAP_ACTION", "alert-only"))
            ),
            Environment.TEST: BudgetConfig(
                environment=Environment.TEST,
                monthly_limit=float(os.getenv("TEST_MAX_MONTHLY_COST", "50")),
                alert_thresholds=[95],
                cost_cap_action=CostAction(os.getenv("TEST_COST_CAP_ACTION", "block"))
            )
        }
        
        return configs[self.environment]
    
    def get_openai_costs(self) -> ServiceCost:
        """Get OpenAI API usage costs"""
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI library not available")
            return ServiceCost(
                service_name="OpenAI",
                current_month_cost=0,
                projected_month_cost=0,
                daily_average=0,
                last_24h_cost=0
            )
        
        # This would typically connect to OpenAI's usage API
        # For now, we'll estimate based on token usage
        
        # Pricing estimates (as of 2024)
        pricing = {
            "gpt-4": {"prompt": 0.03, "completion": 0.06},  # per 1K tokens
            "gpt-3.5-turbo": {"prompt": 0.001, "completion": 0.002}
        }
        
        # In production, you would fetch actual usage from OpenAI API
        # This is a placeholder implementation
        estimated_daily_cost = {
            Environment.PRODUCTION: 66.67,  # ~$2000/month
            Environment.STAGING: 6.67,       # ~$200/month
            Environment.DEVELOPMENT: 1.67,   # ~$50/month
            Environment.TEST: 0.33          # ~$10/month
        }
        
        daily_cost = estimated_daily_cost.get(self.environment, 0)
        days_in_month = 30
        current_day = datetime.now().day
        
        return ServiceCost(
            service_name="OpenAI",
            current_month_cost=daily_cost * current_day,
            projected_month_cost=daily_cost * days_in_month,
            daily_average=daily_cost,
            last_24h_cost=daily_cost
        )
    
    def get_gcp_costs(self) -> ServiceCost:
        """Get Google Cloud Platform costs"""
        if not GCLOUD_AVAILABLE:
            self.logger.warning("Google Cloud libraries not available")
            return ServiceCost(
                service_name="GCP",
                current_month_cost=0,
                projected_month_cost=0,
                daily_average=0,
                last_24h_cost=0
            )
        
        # Query GCP billing data
        # This is a simplified implementation
        try:
            # In production, use actual billing API queries
            estimated_daily_cost = {
                Environment.PRODUCTION: 100,    # ~$3000/month
                Environment.STAGING: 10,        # ~$300/month
                Environment.DEVELOPMENT: 2,     # ~$60/month
                Environment.TEST: 1             # ~$30/month
            }
            
            daily_cost = estimated_daily_cost.get(self.environment, 0)
            days_in_month = 30
            current_day = datetime.now().day
            
            return ServiceCost(
                service_name="GCP",
                current_month_cost=daily_cost * current_day,
                projected_month_cost=daily_cost * days_in_month,
                daily_average=daily_cost,
                last_24h_cost=daily_cost
            )
        except Exception as e:
            self.logger.error(f"Error fetching GCP costs: {e}")
            return ServiceCost("GCP", 0, 0, 0, 0)
    
    def get_total_costs(self) -> Dict[str, Any]:
        """Get total costs across all services"""
        openai_costs = self.get_openai_costs()
        gcp_costs = self.get_gcp_costs()
        
        total_current = openai_costs.current_month_cost + gcp_costs.current_month_cost
        total_projected = openai_costs.projected_month_cost + gcp_costs.projected_month_cost
        
        return {
            "environment": self.environment.value,
            "timestamp": datetime.now().isoformat(),
            "budget_limit": self.budget_config.monthly_limit,
            "services": {
                "openai": {
                    "current_month": openai_costs.current_month_cost,
                    "projected_month": openai_costs.projected_month_cost,
                    "daily_average": openai_costs.daily_average,
                    "last_24h": openai_costs.last_24h_cost
                },
                "gcp": {
                    "current_month": gcp_costs.current_month_cost,
                    "projected_month": gcp_costs.projected_month_cost,
                    "daily_average": gcp_costs.daily_average,
                    "last_24h": gcp_costs.last_24h_cost
                }
            },
            "totals": {
                "current_month": total_current,
                "projected_month": total_projected,
                "budget_used_percent": (total_current / self.budget_config.monthly_limit) * 100,
                "projected_budget_percent": (total_projected / self.budget_config.monthly_limit) * 100
            }
        }
    
    def check_budget_alerts(self) -> List[Dict[str, Any]]:
        """Check if any budget thresholds are exceeded"""
        costs = self.get_total_costs()
        alerts = []
        
        budget_used_percent = costs["totals"]["budget_used_percent"]
        projected_percent = costs["totals"]["projected_budget_percent"]
        
        for threshold in self.budget_config.alert_thresholds:
            if budget_used_percent >= threshold:
                alerts.append({
                    "type": "current_usage",
                    "severity": "high" if threshold >= 90 else "medium",
                    "threshold": threshold,
                    "current_percent": budget_used_percent,
                    "message": f"Budget usage at {budget_used_percent:.1f}% (threshold: {threshold}%)"
                })
            
            if projected_percent >= threshold:
                alerts.append({
                    "type": "projected_usage",
                    "severity": "medium" if threshold >= 90 else "low",
                    "threshold": threshold,
                    "projected_percent": projected_percent,
                    "message": f"Projected usage at {projected_percent:.1f}% (threshold: {threshold}%)"
                })
        
        return alerts
    
    def should_throttle_requests(self) -> bool:
        """Check if requests should be throttled based on budget"""
        costs = self.get_total_costs()
        budget_used_percent = costs["totals"]["budget_used_percent"]
        
        if self.budget_config.cost_cap_action == CostAction.THROTTLE:
            # Throttle at 90% budget usage
            return budget_used_percent >= 90
        
        return False
    
    def should_block_requests(self) -> bool:
        """Check if requests should be blocked based on budget"""
        costs = self.get_total_costs()
        budget_used_percent = costs["totals"]["budget_used_percent"]
        
        if self.budget_config.cost_cap_action == CostAction.BLOCK:
            # Block at 100% budget usage
            return budget_used_percent >= 100
        
        return False
    
    def generate_cost_report(self) -> str:
        """Generate a formatted cost report"""
        costs = self.get_total_costs()
        alerts = self.check_budget_alerts()
        
        report = []
        report.append("=" * 70)
        report.append(f"COST REPORT - {self.environment.value.upper()} ENVIRONMENT")
        report.append(f"Generated: {costs['timestamp']}")
        report.append("=" * 70)
        report.append("")
        
        # Budget Summary
        report.append("BUDGET SUMMARY")
        report.append("-" * 40)
        report.append(f"Monthly Budget: ${costs['budget_limit']:,.2f}")
        report.append(f"Current Usage: ${costs['totals']['current_month']:,.2f} ({costs['totals']['budget_used_percent']:.1f}%)")
        report.append(f"Projected Usage: ${costs['totals']['projected_month']:,.2f} ({costs['totals']['projected_budget_percent']:.1f}%)")
        report.append("")
        
        # Service Breakdown
        report.append("SERVICE BREAKDOWN")
        report.append("-" * 40)
        for service, details in costs["services"].items():
            report.append(f"\n{service.upper()}")
            report.append(f"  Current Month: ${details['current_month']:,.2f}")
            report.append(f"  Projected Month: ${details['projected_month']:,.2f}")
            report.append(f"  Daily Average: ${details['daily_average']:,.2f}")
            report.append(f"  Last 24 Hours: ${details['last_24h']:,.2f}")
        report.append("")
        
        # Alerts
        if alerts:
            report.append("ALERTS")
            report.append("-" * 40)
            for alert in alerts:
                icon = "🔴" if alert["severity"] == "high" else "🟡" if alert["severity"] == "medium" else "🟢"
                report.append(f"{icon} {alert['message']}")
            report.append("")
        
        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 40)
        recommendations = self._generate_recommendations(costs, alerts)
        for rec in recommendations:
            report.append(f"• {rec}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def _generate_recommendations(self, costs: Dict, alerts: List) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        budget_used = costs["totals"]["budget_used_percent"]
        projected = costs["totals"]["projected_budget_percent"]
        
        if projected > 100:
            recommendations.append(f"Projected to exceed budget by {projected - 100:.1f}%. Consider reducing usage.")
        
        if self.environment == Environment.DEVELOPMENT:
            if costs["services"]["openai"]["current_month"] > 10:
                recommendations.append("Consider using local LLM (Ollama) for development to reduce OpenAI costs.")
        
        if self.environment == Environment.STAGING:
            recommendations.append("Consider scheduling automatic scale-down during off-hours.")
            recommendations.append("Use gpt-3.5-turbo instead of gpt-4 for staging tests.")
        
        if budget_used > 75:
            recommendations.append("Review and optimize expensive API calls.")
            recommendations.append("Consider implementing response caching.")
        
        if not recommendations:
            recommendations.append("Costs are within acceptable limits.")
        
        return recommendations
    
    def export_to_json(self, filepath: str = None) -> str:
        """Export cost report to JSON file"""
        costs = self.get_total_costs()
        alerts = self.check_budget_alerts()
        
        report_data = {
            "report": costs,
            "alerts": alerts,
            "recommendations": self._generate_recommendations(costs, alerts),
            "throttle_active": self.should_throttle_requests(),
            "block_active": self.should_block_requests()
        }
        
        if filepath:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
            self.logger.info(f"Report exported to {filepath}")
        
        return json.dumps(report_data, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Monitor Living Twin costs and budgets")
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--environment", required=True, 
                       choices=["production", "staging", "development", "test"],
                       help="Environment to monitor")
    parser.add_argument("--format", default="text", choices=["text", "json"],
                       help="Output format")
    parser.add_argument("--export", help="Export report to file")
    parser.add_argument("--check-alerts", action="store_true",
                       help="Check for budget alerts only")
    parser.add_argument("--check-throttle", action="store_true",
                       help="Check if throttling should be active")
    
    args = parser.parse_args()
    
    monitor = CostMonitor(args.project_id, args.environment)
    
    if args.check_throttle:
        should_throttle = monitor.should_throttle_requests()
        print(f"Throttle active: {should_throttle}")
        sys.exit(0 if not should_throttle else 1)
    
    if args.check_alerts:
        alerts = monitor.check_budget_alerts()
        if alerts:
            print(f"Found {len(alerts)} alert(s):")
            for alert in alerts:
                print(f"  - {alert['message']}")
            sys.exit(1)
        else:
            print("No budget alerts")
            sys.exit(0)
    
    if args.format == "json":
        output = monitor.export_to_json(args.export)
        if not args.export:
            print(output)
    else:
        report = monitor.generate_cost_report()
        print(report)
        
        if args.export:
            with open(args.export, 'w') as f:
                f.write(report)
            print(f"\nReport saved to {args.export}")


if __name__ == "__main__":
    main()
