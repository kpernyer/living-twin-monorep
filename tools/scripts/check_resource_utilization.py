#!/usr/bin/env python3
"""
Living Twin - Resource Utilization and Cost Monitor

This script helps you understand:
1. Which Cloud resources are running and costing money
2. Current scaling configuration
3. Resource utilization vs cost
4. Recommendations for cost optimization
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import argparse

class ResourceMonitor:
    def __init__(self, project_id: str, environment: str = "dev"):
        self.project_id = project_id
        self.environment = environment
        
    def run_gcloud_command(self, command: List[str]) -> Dict[str, Any]:
        """Run a gcloud command and return JSON output"""
        try:
            result = subprocess.run(
                ["gcloud"] + command + ["--format=json", f"--project={self.project_id}"],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout) if result.stdout.strip() else {}
        except subprocess.CalledProcessError as e:
            print(f"Error running command: {' '.join(command)}")
            print(f"Error: {e.stderr}")
            return {}
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from command: {' '.join(command)}")
            return {}

    def check_cloud_run_services(self) -> Dict[str, Any]:
        """Check Cloud Run services and their scaling configuration"""
        print("🚀 CLOUD RUN SERVICES")
        print("=" * 50)
        
        services = self.run_gcloud_command([
            "run", "services", "list", "--region=europe-west1"
        ])
        
        service_details = {}
        
        for service in services:
            service_name = service.get("metadata", {}).get("name", "unknown")
            if self.environment not in service_name:
                continue
                
            # Get detailed service configuration
            detail = self.run_gcloud_command([
                "run", "services", "describe", service_name, "--region=europe-west1"
            ])
            
            spec = detail.get("spec", {})
            template = spec.get("template", {})
            metadata = template.get("metadata", {})
            annotations = metadata.get("annotations", {})
            container_spec = template.get("spec", {}).get("containers", [{}])[0]
            resources = container_spec.get("resources", {})
            
            # Extract scaling configuration
            min_instances = int(annotations.get("autoscaling.knative.dev/minScale", "0"))
            max_instances = int(annotations.get("autoscaling.knative.dev/maxScale", "100"))
            cpu_limit = resources.get("limits", {}).get("cpu", "1000m")
            memory_limit = resources.get("limits", {}).get("memory", "512Mi")
            
            # Get current status
            status = detail.get("status", {})
            url = status.get("url", "N/A")
            ready_condition = next(
                (c for c in status.get("conditions", []) if c.get("type") == "Ready"),
                {}
            )
            is_ready = ready_condition.get("status") == "True"
            
            service_details[service_name] = {
                "url": url,
                "ready": is_ready,
                "scaling": {
                    "min_instances": min_instances,
                    "max_instances": max_instances,
                    "cpu_limit": cpu_limit,
                    "memory_limit": memory_limit
                },
                "cost_impact": self._calculate_cloud_run_cost_impact(
                    min_instances, max_instances, cpu_limit, memory_limit
                )
            }
            
            print(f"📦 {service_name}")
            print(f"   Status: {'✅ Ready' if is_ready else '❌ Not Ready'}")
            print(f"   URL: {url}")
            print(f"   Scaling: {min_instances}-{max_instances} instances")
            print(f"   Resources: {cpu_limit} CPU, {memory_limit} memory")
            print(f"   💰 Cost Impact: {service_details[service_name]['cost_impact']}")
            print()
            
        return service_details

    def check_storage_buckets(self) -> Dict[str, Any]:
        """Check Cloud Storage buckets and their usage"""
        print("🗄️  CLOUD STORAGE BUCKETS")
        print("=" * 50)
        
        buckets = self.run_gcloud_command(["storage", "buckets", "list"])
        bucket_details = {}
        
        for bucket in buckets:
            bucket_name = bucket.get("name", "")
            if self.environment not in bucket_name:
                continue
                
            # Get bucket size (this is an approximation)
            try:
                size_result = subprocess.run([
                    "gcloud", "storage", "du", f"gs://{bucket_name}",
                    "--summarize", "--format=value(size)"
                ], capture_output=True, text=True)
                
                size_bytes = int(size_result.stdout.strip() or "0")
                size_gb = size_bytes / (1024**3)
                
                bucket_details[bucket_name] = {
                    "size_gb": round(size_gb, 2),
                    "monthly_cost_estimate": round(size_gb * 0.02, 2)  # ~$0.02/GB/month
                }
                
                print(f"🪣 {bucket_name}")
                print(f"   Size: {bucket_details[bucket_name]['size_gb']} GB")
                print(f"   💰 Est. Monthly Cost: ${bucket_details[bucket_name]['monthly_cost_estimate']}")
                print()
                
            except Exception as e:
                print(f"🪣 {bucket_name} (size check failed: {e})")
                bucket_details[bucket_name] = {"size_gb": 0, "monthly_cost_estimate": 0}
                
        return bucket_details

    def check_pubsub_topics(self) -> Dict[str, Any]:
        """Check Pub/Sub topics and subscriptions"""
        print("📨 PUB/SUB TOPICS & SUBSCRIPTIONS")
        print("=" * 50)
        
        topics = self.run_gcloud_command(["pubsub", "topics", "list"])
        topic_details = {}
        
        for topic in topics:
            topic_name = topic.get("name", "").split("/")[-1]
            if "living-twin" not in topic_name:
                continue
                
            # Get subscriptions for this topic
            subscriptions = self.run_gcloud_command([
                "pubsub", "subscriptions", "list", f"--filter=topic:{topic['name']}"
            ])
            
            topic_details[topic_name] = {
                "subscriptions": len(subscriptions),
                "cost_impact": "Low (pay-per-use)"
            }
            
            print(f"📬 {topic_name}")
            print(f"   Subscriptions: {len(subscriptions)}")
            print(f"   💰 Cost Impact: Pay-per-message (typically very low)")
            print()
            
        return topic_details

    def check_secrets(self) -> Dict[str, Any]:
        """Check Secret Manager secrets"""
        print("🔐 SECRET MANAGER")
        print("=" * 50)
        
        secrets = self.run_gcloud_command(["secrets", "list"])
        secret_details = {}
        
        secret_count = 0
        for secret in secrets:
            secret_name = secret.get("name", "").split("/")[-1]
            secret_count += 1
            
        secret_details = {
            "count": secret_count,
            "monthly_cost_estimate": secret_count * 0.06  # $0.06 per secret per month
        }
        
        print(f"🗝️  Total Secrets: {secret_count}")
        print(f"💰 Est. Monthly Cost: ${secret_details['monthly_cost_estimate']:.2f}")
        print()
        
        return secret_details

    def _calculate_cloud_run_cost_impact(self, min_instances: int, max_instances: int, 
                                       cpu_limit: str, memory_limit: str) -> str:
        """Calculate cost impact of Cloud Run service"""
        # Parse CPU (convert from millicores to cores)
        cpu_cores = float(cpu_limit.replace("m", "")) / 1000 if "m" in cpu_limit else float(cpu_limit)
        
        # Parse memory (convert to GB)
        memory_gb = float(memory_limit.replace("Mi", "")) / 1024 if "Mi" in memory_limit else \
                   float(memory_limit.replace("Gi", "")) if "Gi" in memory_limit else 0.5
        
        # Rough cost calculation (Cloud Run pricing varies by region)
        # CPU: ~$0.00002400 per vCPU-second
        # Memory: ~$0.00000250 per GB-second
        
        if min_instances == 0:
            return "💚 Low - Scales to zero when not used"
        else:
            monthly_seconds = 30 * 24 * 3600  # seconds in a month
            min_cpu_cost = min_instances * cpu_cores * 0.00002400 * monthly_seconds
            min_memory_cost = min_instances * memory_gb * 0.00000250 * monthly_seconds
            min_monthly_cost = min_cpu_cost + min_memory_cost
            
            if min_monthly_cost < 10:
                return f"💛 Medium - ~${min_monthly_cost:.2f}/month minimum"
            else:
                return f"🔴 High - ~${min_monthly_cost:.2f}/month minimum"

    def generate_cost_optimization_recommendations(self, service_details: Dict) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        for service_name, details in service_details.items():
            scaling = details.get("scaling", {})
            min_instances = scaling.get("min_instances", 0)
            
            if min_instances > 0:
                recommendations.append(
                    f"🔧 {service_name}: Consider setting min_instances to 0 for {self.environment} "
                    f"environment to enable scale-to-zero (currently {min_instances})"
                )
                
            max_instances = scaling.get("max_instances", 100)
            if max_instances > 20 and self.environment == "dev":
                recommendations.append(
                    f"🔧 {service_name}: Consider lowering max_instances for dev environment "
                    f"(currently {max_instances})"
                )
                
        return recommendations

    def show_scaling_configuration_locations(self):
        """Show where scaling is configured"""
        print("⚙️  SCALING CONFIGURATION LOCATIONS")
        print("=" * 50)
        print()
        print("📍 Terraform Configuration:")
        print("   File: packages/gcp_firebase/terraform/main.tf")
        print("   Section: locals.env_config")
        print()
        print("   Environment-specific settings:")
        print("   • dev: min_instances=0, max_instances=5")
        print("   • staging: min_instances=1, max_instances=10") 
        print("   • prod: min_instances=2, max_instances=50")
        print()
        print("📍 Cloud Run Module:")
        print("   File: packages/gcp_firebase/terraform/modules/cloud_run/main.tf")
        print("   Variables: min_instances, max_instances, cpu_limit, memory_limit")
        print()
        print("📍 Override Variables:")
        print("   File: packages/gcp_firebase/terraform/variables.tf")
        print("   Variables: api_min_instances, api_max_instances, worker_min_instances, worker_max_instances")
        print()
        print("🔧 To modify scaling:")
        print("   1. Edit packages/gcp_firebase/terraform/main.tf (locals.env_config)")
        print("   2. Or use terraform variables: -var='api_min_instances=0'")
        print("   3. Run: terraform plan -var-file=environments/{env}.tfvars")
        print("   4. Run: terraform apply")
        print()

def main():
    parser = argparse.ArgumentParser(description="Monitor Living Twin resource utilization and costs")
    parser.add_argument("--project-id", required=True, help="GCP Project ID")
    parser.add_argument("--environment", default="dev", help="Environment (dev/staging/prod)")
    parser.add_argument("--show-config", action="store_true", help="Show scaling configuration locations")
    
    args = parser.parse_args()
    
    monitor = ResourceMonitor(args.project_id, args.environment)
    
    print(f"🔍 LIVING TWIN RESOURCE MONITOR")
    print(f"Project: {args.project_id}")
    print(f"Environment: {args.environment}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Check all resources
    service_details = monitor.check_cloud_run_services()
    bucket_details = monitor.check_storage_buckets()
    topic_details = monitor.check_pubsub_topics()
    secret_details = monitor.check_secrets()
    
    # Generate recommendations
    recommendations = monitor.generate_cost_optimization_recommendations(service_details)
    
    if recommendations:
        print("💡 COST OPTIMIZATION RECOMMENDATIONS")
        print("=" * 50)
        for rec in recommendations:
            print(rec)
        print()
    
    # Show configuration locations
    if args.show_config:
        monitor.show_scaling_configuration_locations()
    
    print("✅ Resource monitoring complete!")
    print()
    print("💡 Tips:")
    print("   • Run with --show-config to see where scaling is configured")
    print("   • Use 'gcloud run services list' for real-time Cloud Run status")
    print("   • Check GCP Console > Billing for detailed cost breakdown")

if __name__ == "__main__":
    main()
