#!/usr/bin/env python3
"""
Universal launcher for Kubernetes Lab
Works on Windows, Linux, and macOS
"""

import os
import sys
import platform
import subprocess
import time
import socket

class Colors:
    """Colors for terminal output"""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    
    @staticmethod
    def disable():
        """Disable colors on Windows if needed"""
        if platform.system() == "Windows":
            Colors.CYAN = ''
            Colors.GREEN = ''
            Colors.YELLOW = ''
            Colors.RED = ''
            Colors.RESET = ''

def print_color(text, color=Colors.CYAN):
    """Print colored text"""
    print(f"{color}{text}{Colors.RESET}")

def run_command(cmd, shell=False):
    """Run command and return result"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Check if Docker is running"""
    print_color("\n[1/7] Checking Docker...", Colors.YELLOW)
    success, stdout, stderr = run_command("docker info")
    if success:
        print_color("OK: Docker is running", Colors.GREEN)
        return True
    else:
        print_color("ERROR: Docker is not running!", Colors.RED)
        return False

def check_kubernetes():
    """Check if Kubernetes is available"""
    print_color("\n[2/7] Checking Kubernetes...", Colors.YELLOW)
    success, stdout, stderr = run_command("kubectl cluster-info")
    if success:
        print_color("OK: Kubernetes is working", Colors.GREEN)
        return True
    else:
        print_color("ERROR: Kubernetes is not available!", Colors.RED)
        if platform.system() == "Windows":
            print_color("Make sure Kubernetes is enabled in Docker Desktop", Colors.YELLOW)
        else:
            print_color("Run: minikube start or kind create cluster", Colors.YELLOW)
        return False

def get_docker_host():
    """Get Docker host address for different platforms"""
    system = platform.system()
    if system == "Windows":
        return "host.docker.internal"
    elif system == "Linux":
        # Check if running inside container
        if os.path.exists('/.dockerenv'):
            return "host.docker.internal"
        return "localhost"
    elif system == "Darwin":  # macOS
        return "host.docker.internal"
    else:
        return "localhost"

def build_app():
    """Build Docker image for app"""
    print_color("\n[3/7] Building myapp image...", Colors.YELLOW)
    success, stdout, stderr = run_command("docker build -t myapp:latest ./app")
    if success:
        print_color("OK: Image built", Colors.GREEN)
        return True
    else:
        print_color(f"ERROR: Failed to build image: {stderr}", Colors.RED)
        return False

def deploy_app():
    """Deploy app to Kubernetes"""
    print_color("\n[4/7] Deploying app to Kubernetes...", Colors.YELLOW)
    
    # Apply deployments
    run_command("kubectl apply -f ./k8s/app-deployment.yaml")
    run_command("kubectl apply -f ./k8s/app-service.yaml")
    
    # Wait for pods
    print_color("Waiting for myapp pods...", Colors.YELLOW)
    time.sleep(5)
    
    success, stdout, stderr = run_command("kubectl wait --for=condition=ready pod -l app=myapp --timeout=60s")
    if success:
        print_color("OK: App is running", Colors.GREEN)
        return True
    else:
        print_color("Warning: Pods may not be ready yet", Colors.YELLOW)
        return True

def install_monitoring():
    """Install Prometheus and Grafana"""
    print_color("\n[5/7] Installing Prometheus + Grafana...", Colors.YELLOW)
    
    # Check if already installed
    success, stdout, stderr = run_command("helm list -n monitoring")
    if "monitoring" in stdout:
        print_color("OK: Monitoring already installed", Colors.GREEN)
        return True
    
    # Add repo and install
    run_command("helm repo add prometheus-community https://prometheus-community.github.io/helm-charts")
    run_command("helm repo update")
    
    cmd = ('helm install monitoring prometheus-community/kube-prometheus-stack '
           '--namespace monitoring --create-namespace '
           '--set grafana.service.type=NodePort '
           '--set grafana.service.nodePort=30300 '
           '--set grafana.adminPassword=admin123 '
           '--set prometheus.service.type=NodePort '
           '--set prometheus.service.nodePort=30900')
    
    success, stdout, stderr = run_command(cmd)
    if success:
        print_color("Waiting for monitoring to start (120 seconds)...", Colors.YELLOW)
        time.sleep(120)
        print_color("OK: Monitoring installed", Colors.GREEN)
        return True
    else:
        print_color(f"Warning: {stderr}", Colors.YELLOW)
        return True

def create_servicemonitor():
    """Create ServiceMonitor for myapp"""
    print_color("\n[6/7] Creating ServiceMonitor...", Colors.YELLOW)
    
    # Delete old if exists
    run_command("kubectl delete servicemonitor myapp-monitor -n monitoring --ignore-not-found")
    
    sm_yaml = """
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp-monitor
  namespace: monitoring
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app: myapp
  endpoints:
  - port: http
    path: /metrics
    interval: 15s
  namespaceSelector:
    matchNames:
    - default
"""
    
    # Save to temp file
    with open("/tmp/servicemonitor.yaml", "w") as f:
        f.write(sm_yaml)
    
    success, stdout, stderr = run_command("kubectl apply -f /tmp/servicemonitor.yaml")
    if success:
        print_color("OK: ServiceMonitor created", Colors.GREEN)
        return True
    else:
        print_color(f"Warning: {stderr}", Colors.YELLOW)
        return True

def start_client():
    """Start integration client"""
    print_color("\n[7/7] Starting integration client...", Colors.YELLOW)
    
    # Update docker-compose with correct host
    docker_host = get_docker_host()
    
    # Read existing docker-compose
    with open("docker-compose.yml", "r") as f:
        compose_content = f.read()
    
    # Update environment variables
    compose_content = compose_content.replace(
        "APP_URL=http://localhost:30080",
        f"APP_URL=http://{docker_host}:30080"
    )
    compose_content = compose_content.replace(
        "PROMETHEUS_URL=http://localhost:30900",
        f"PROMETHEUS_URL=http://{docker_host}:30900"
    )
    
    with open("docker-compose.yml.tmp", "w") as f:
        f.write(compose_content)
    
    run_command("docker-compose down")
    run_command("docker-compose -f docker-compose.yml.tmp up -d")
    
    print_color("OK: Client started", Colors.GREEN)
    return True

def print_info():
    """Print access information"""
    docker_host = get_docker_host()
    
    print_color("\n" + "="*50, Colors.CYAN)
    print_color("READY! Access to services:", Colors.GREEN)
    print_color("="*50, Colors.CYAN)
    print_color(f"  API: http://localhost:30080", Colors.WHITE)
    print_color(f"  Prometheus: http://localhost:30900", Colors.WHITE)
    print_color(f"  Grafana: http://localhost:30300 (admin/admin123)", Colors.WHITE)
    print_color("="*50, Colors.CYAN)
    print_color("\nClient logs: docker-compose logs -f", Colors.YELLOW)
    print_color("Stop: docker-compose down", Colors.YELLOW)

def main():
    """Main function"""
    print_color("="*50, Colors.CYAN)
    print_color("Kubernetes Lab - Universal Launcher", Colors.CYAN)
    print_color("="*50, Colors.CYAN)
    print_color(f"Platform: {platform.system()} {platform.release()}", Colors.YELLOW)
    
    # Disable colors on Windows if needed
    if platform.system() == "Windows" and os.environ.get("NO_COLOR"):
        Colors.disable()
    
    # Run steps
    steps = [
        check_docker,
        check_kubernetes,
        build_app,
        deploy_app,
        install_monitoring,
        create_servicemonitor,
        start_client
    ]
    
    for step in steps:
        if not step():
            print_color("\nFAILED! Stopping...", Colors.RED)
            sys.exit(1)
    
    print_info()

if __name__ == "__main__":
    main()