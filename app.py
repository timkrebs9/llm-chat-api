from fastapi import FastAPI, Depends, HTTPException, Security, status, Request
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import uvicorn
import os
import httpx
from datetime import datetime
import logging
from urllib.parse import urljoin
import json
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('api_gateway')

app = FastAPI(title="IoT Monitoring Platform API Gateway")

# Security setup
API_KEY = os.getenv("API_KEY", "your-default-api-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Service discovery - this would ideally use a service mesh or discovery service
# For now, we'll use environment variables or hardcoded values for demonstration
SERVICE_REGISTRY = {
    "device-registry": os.getenv("DEVICE_REGISTRY_SERVICE_URL", "http://device-registry-service:8001"),
    "telemetry": os.getenv("TELEMETRY_SERVICE_URL", "http://telemetry-service:8002"),
    "rules-engine": os.getenv("RULES_ENGINE_SERVICE_URL", "http://rules-engine-service:8003"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8004"),
    "dashboard": os.getenv("DASHBOARD_SERVICE_URL", "http://dashboard-service:8005"),
    "ingestion": os.getenv("INGESTION_SERVICE_URL", "http://ingestion-service:8006"),
    "ml": os.getenv("ML_SERVICE_URL", "http://ml-service:8007"),
}

# Circuit breaker configuration
CIRCUIT_BREAKER = {
    "failure_threshold": int(os.getenv("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")),
    "reset_timeout": int(os.getenv("CIRCUIT_BREAKER_RESET_TIMEOUT", "30")),
}

# Circuit breaker state
circuit_state = {service: {"failures": 0, "open": False, "last_failure": None} for service in SERVICE_REGISTRY}

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
    )

async def forward_request(service: str, path: str, method: str, headers: Dict, query_params: Dict = None, body: Dict = None) -> Dict[str, Any]:
    """
    Forward the request to the appropriate service with circuit breaker pattern
    """
    # Check if circuit is open for this service
    if circuit_state[service]["open"]:
        now = datetime.now()
        last_failure = circuit_state[service]["last_failure"]
        if last_failure and (now - last_failure).total_seconds() > CIRCUIT_BREAKER["reset_timeout"]:
            # Reset the circuit breaker
            circuit_state[service]["open"] = False
            circuit_state[service]["failures"] = 0
        else:
            # Circuit is open, return error
            raise HTTPException(status_code=503, detail=f"Service {service} is currently unavailable")
    
    service_url = SERVICE_REGISTRY.get(service)
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service {service} not found")
    
    url = urljoin(service_url, path)
    
    # Clean headers - remove host
    if "host" in headers:
        del headers["host"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=query_params,
                json=body,
                timeout=10.0
            )
            
            # Reset failures on success
            if response.status_code < 500:
                circuit_state[service]["failures"] = 0
                
            response.raise_for_status()
            return response.json()
    except Exception as e:
        # Increment failure count
        circuit_state[service]["failures"] += 1
        circuit_state[service]["last_failure"] = datetime.now()
        
        # Open circuit if failure threshold is reached
        if circuit_state[service]["failures"] >= CIRCUIT_BREAKER["failure_threshold"]:
            circuit_state[service]["open"] = True
            logger.error(f"Circuit breaker open for service {service}: {str(e)}")
        
        logger.error(f"Error forwarding request to {service}: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service {service} error: {str(e)}")

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to track requests across services"""
    correlation_id = request.headers.get("X-Correlation-ID", f"corr-{datetime.now().timestamp()}")
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response

# Basic routes
@app.get("/")
async def root():
    return {
        "message": "IoT Monitoring Platform API Gateway",
        "version": "1.0.0",
        "services": list(SERVICE_REGISTRY.keys())
    }

@app.get("/health")
async def health():
    health_data = {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    # Check each service health asynchronously
    services_health = {}
    async def check_service_health(service):
        try:
            health_url = urljoin(SERVICE_REGISTRY[service], "/health")
            async with httpx.AsyncClient() as client:
                response = await client.get(health_url, timeout=2.0)
                services_health[service] = "healthy" if response.status_code == 200 else "unhealthy"
        except:
            services_health[service] = "unreachable"
    
    # Gather health checks with timeout
    health_check_tasks = [check_service_health(service) for service in SERVICE_REGISTRY]
    await asyncio.gather(*health_check_tasks, return_exceptions=True)
    
    health_data["services"] = services_health
    return health_data

# Device registry routes
@app.get("/devices", dependencies=[Depends(get_api_key)])
async def list_devices(request: Request, limit: int = 100, offset: int = 0):
    return await forward_request(
        service="device-registry",
        path="/devices",
        method="GET",
        headers=dict(request.headers),
        query_params={"limit": limit, "offset": offset}
    )

@app.get("/devices/{device_id}", dependencies=[Depends(get_api_key)])
async def get_device(request: Request, device_id: str):
    return await forward_request(
        service="device-registry",
        path=f"/devices/{device_id}",
        method="GET",
        headers=dict(request.headers)
    )

@app.post("/devices", dependencies=[Depends(get_api_key)])
async def create_device(request: Request):
    body = await request.json()
    return await forward_request(
        service="device-registry",
        path="/devices",
        method="POST",
        headers=dict(request.headers),
        body=body
    )

# Telemetry routes
@app.get("/telemetry/{device_id}", dependencies=[Depends(get_api_key)])
async def get_telemetry(request: Request, device_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None):
    return await forward_request(
        service="telemetry",
        path=f"/telemetry/{device_id}",
        method="GET",
        headers=dict(request.headers),
        query_params={"start_time": start_time, "end_time": end_time}
    )

# Rules engine routes
@app.get("/rules", dependencies=[Depends(get_api_key)])
async def list_rules(request: Request):
    return await forward_request(
        service="rules-engine",
        path="/rules",
        method="GET",
        headers=dict(request.headers)
    )

@app.post("/rules", dependencies=[Depends(get_api_key)])
async def create_rule(request: Request):
    body = await request.json()
    return await forward_request(
        service="rules-engine",
        path="/rules",
        method="POST",
        headers=dict(request.headers),
        body=body
    )

# Alert/Notification routes
@app.get("/alerts", dependencies=[Depends(get_api_key)])
async def get_alerts(request: Request, limit: int = 100, offset: int = 0):
    return await forward_request(
        service="notification",
        path="/alerts",
        method="GET",
        headers=dict(request.headers),
        query_params={"limit": limit, "offset": offset}
    )

# Dashboard data routes
@app.get("/dashboard/summary", dependencies=[Depends(get_api_key)])
async def dashboard_summary(request: Request):
    return await forward_request(
        service="dashboard",
        path="/summary",
        method="GET",
        headers=dict(request.headers)
    )

# Ingestion endpoint for collectors
@app.post("/ingest", dependencies=[Depends(get_api_key)])
async def ingest_data(request: Request):
    body = await request.json()
    return await forward_request(
        service="ingestion",
        path="/data",
        method="POST",
        headers=dict(request.headers),
        body=body
    )

# ML service routes
@app.get("/anomalies/{device_id}", dependencies=[Depends(get_api_key)])
async def get_anomalies(request: Request, device_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None):
    return await forward_request(
        service="ml",
        path=f"/anomalies/{device_id}",
        method="GET",
        headers=dict(request.headers),
        query_params={"start_time": start_time, "end_time": end_time}
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)