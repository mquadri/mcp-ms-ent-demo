# File: demos/mock_data_generator.py
"""
Mock Data Generator for Microsoft Enterprise MCP Servers
Generates realistic sample data for testing scenarios without Azure credentials
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
import string

class MockDataGenerator:
    """Generate mock data for testing scenarios"""
    
    @staticmethod
    def generate_alert_id() -> str:
        """Generate unique alert ID"""
        return f"alert-{random.randint(1000, 9999)}"
    
    @staticmethod
    def generate_ticket_id() -> int:
        """Generate DevOps ticket ID"""
        return random.randint(10000, 99999)
    
    @staticmethod
    def generate_build_id(day: int, build_num: int) -> str:
        """Generate build ID"""
        return f"build-{day:02d}-{build_num:02d}"
    
    @staticmethod
    def generate_alerts(count: int = 3) -> List[Dict[str, Any]]:
        """Generate mock alerts"""
        services = ["CheckoutService", "PaymentGateway", "NotificationService", "APIGateway", "AuthService"]
        severities = ["Critical", "Error", "Warning"]
        errors = [
            "Database connection timeout",
            "External API returning error codes",
            "Queue backing up with undelivered messages",
            "High CPU and memory usage",
            "Authentication failures increasing"
        ]
        
        alerts = []
        for i in range(count):
            alert = {
                "AlertId": f"alert-{i+1:03d}",
                "ServiceName": random.choice(services),
                "Severity": random.choice(severities),
                "Message": random.choice(errors),
                "AffectedResources": [f"resource-{j}" for j in range(random.randint(1, 3))],
                "ErrorCode": f"ERR_{random.randint(1000, 9999)}",
                "Timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 60))).isoformat(),
                "IncidentCount": random.randint(10, 500)
            }
            alerts.append(alert)
        
        return alerts
    
    @staticmethod
    def generate_error_logs(count: int = 5) -> List[Dict[str, Any]]:
        """Generate mock error logs"""
        services = ["CheckoutService", "PaymentGateway", "NotificationService"]
        messages = [
            "Database query timeout after 5000ms",
            "External API unreachable",
            "Connection pool exhausted",
            "Memory allocation failed",
            "Authentication service down"
        ]
        
        logs = []
        for i in range(count):
            log = {
                "level": random.choice(["ERROR", "WARN", "INFO"]),
                "service": random.choice(services),
                "message": random.choice(messages),
                "request_id": f"req-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                "user_id": f"user-{random.randint(1000, 9999)}",
                "timestamp": (datetime.utcnow() - timedelta(minutes=random.randint(1, 30))).isoformat()
            }
            logs.append(log)
        
        return logs
    
    @staticmethod
    def generate_sprint_metrics() -> Dict[str, Any]:
        """Generate mock sprint metrics"""
        return {
            "Sprint 24": {
                "start_date": (datetime.utcnow() - timedelta(days=14)).isoformat(),
                "end_date": datetime.utcnow().isoformat(),
                "total_work_items": random.randint(35, 50),
                "completed": random.randint(30, 45),
                "velocity_points": random.randint(140, 165),
                "planned_points": random.randint(150, 170),
                "completion_percentage": round(random.uniform(85, 98), 1),
                "test_pass_rate": round(random.uniform(93, 99), 1)
            }
        }
    
    @staticmethod
    def generate_build_logs(days: int = 30) -> List[Dict[str, Any]]:
        """Generate mock build logs"""
        builds = []
        
        for day in range(days):
            timestamp = datetime.utcnow() - timedelta(days=day)
            builds_per_day = random.randint(3, 6)
            
            for i in range(builds_per_day):
                build = {
                    "timestamp": timestamp.isoformat(),
                    "build_id": f"build-{day:02d}-{i:02d}",
                    "status": random.choices(["Success", "Failed"], weights=[85, 15])[0],
                    "duration_seconds": random.randint(180, 900),
                    "test_pass_rate": round(random.uniform(90, 99), 1),
                    "code_coverage_percent": round(random.uniform(80, 95), 1)
                }
                builds.append(build)
        
        return builds
    
    @staticmethod
    def generate_deployment_logs(days: int = 30) -> List[Dict[str, Any]]:
        """Generate mock deployment logs"""
        deployments = []
        
        for day in range(days):
            timestamp = datetime.utcnow() - timedelta(days=day)
            deploys_per_day = random.randint(1, 3)
            
            for i in range(deploys_per_day):
                deploy = {
                    "timestamp": timestamp.isoformat(),
                    "deployment_id": f"deploy-{day:02d}-{i:02d}",
                    "environment": random.choice(["Production", "Staging"]),
                    "status": random.choices(["Success", "Failed", "Rollback"], weights=[87, 8, 5])[0],
                    "duration_minutes": random.randint(5, 45)
                }
                deployments.append(deploy)
        
        return deployments
    
    @staticmethod
    def export_to_json(data: Dict, filename: str) -> str:
        """Export mock data to JSON file"""
        filepath = f"mock_data_{filename}.json"
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath


def main():
    """Generate and export all mock data"""
    
    print("🔄 Generating mock data...\n")
    
    generator = MockDataGenerator()
    
    # Scenario 1 data
    print("📊 Scenario 1: Incident Response")
    alerts = generator.generate_alerts(5)
    logs = generator.generate_error_logs(8)
    
    scenario_1_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "alerts": alerts,
        "logs": logs,
        "ticket_id": generator.generate_ticket_id(),
        "engineer": {
            "name": "Ahmed Hassan",
            "email": "ahmed.hassan@contoso.com"
        }
    }
    
    file_1 = generator.export_to_json(scenario_1_data, "scenario_1")
    print(f"   ✅ Generated: {file_1}")
    print(f"      - {len(alerts)} alerts")
    print(f"      - {len(logs)} error logs")
    print()
    
    # Scenario 5 data
    print("📈 Scenario 5: Velocity Analysis")
    sprints = generator.generate_sprint_metrics()
    builds = generator.generate_build_logs(30)
    deployments = generator.generate_deployment_logs(30)
    
    scenario_5_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "sprints": sprints,
        "builds": builds,
        "deployments": deployments,
        "summary": {
            "total_builds": len(builds),
            "total_deployments": len(deployments),
            "build_success_rate": f"{sum(1 for b in builds if b['status'] == 'Success') / len(builds) * 100:.1f}%"
        }
    }
    
    file_2 = generator.export_to_json(scenario_5_data, "scenario_5")
    print(f"   ✅ Generated: {file_2}")
    print(f"      - {len(builds)} build logs")
    print(f"      - {len(deployments)} deployment logs")
    print()
    
    print("="*70)
    print("✅ Mock data generation complete!")
    print("="*70)
    print(f"\nGenerated files:")
    print(f"  - {file_1}")
    print(f"  - {file_2}")


if __name__ == "__main__":
    main()