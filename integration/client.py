import os
import platform
import socket

def get_api_url():
    """Get API URL based on platform"""
    env_url = os.getenv("APP_URL")
    if env_url:
        return env_url
    
    system = platform.system()
    
    # Check if running in container
    in_container = os.path.exists('/.dockerenv')
    
    if in_container:
        # Inside Docker container
        if system == "Linux":
            # Try host.docker.internal first (Linux with extra_hosts)
            try:
                socket.gethostbyname("host.docker.internal")
                return "http://host.docker.internal:30080"
            except:
                return "http://localhost:30080"
        elif system == "Windows" or system == "Darwin":
            return "http://host.docker.internal:30080"
    else:
        # Running on host
        return "http://localhost:30080"
    
    return "http://localhost:30080"

def get_prometheus_url():
    """Get Prometheus URL based on platform"""
    env_url = os.getenv("PROMETHEUS_URL")
    if env_url:
        return env_url
    
    system = platform.system()
    in_container = os.path.exists('/.dockerenv')
    
    if in_container:
        if system == "Linux":
            try:
                socket.gethostbyname("host.docker.internal")
                return "http://host.docker.internal:30900"
            except:
                return "http://localhost:30900"
        else:
            return "http://host.docker.internal:30900"
    else:
        return "http://localhost:30900"

# Use dynamic URLs
APP_URL = get_api_url()
PROMETHEUS_URL = get_prometheus_url()
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:30300")