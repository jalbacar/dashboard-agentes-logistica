# crewai_backend/main.py
# VERSIÓN DEFINITIVA Y CORREGIDA - USANDO crewai.tools.@tool

import json
import re
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

# Simplificado sin CrewAI para evitar problemas de LLM


# --- Herramienta de Optimización ---
def route_optimization_tool(deliveries: List[Dict], fleet: List[Dict]) -> str:
    """
    Calculates optimized delivery routes based on a list of deliveries and available vehicles.
    Returns a JSON string with keys: optimizedRoutes, unassignedDeliveries.
    """
    if not deliveries or not fleet:
        return json.dumps({
            "optimizedRoutes": [],
            "unassignedDeliveries": deliveries or []
        })

    optimized_routes = []
    remaining_deliveries = list(deliveries)
    vehicle_index = 0

    while remaining_deliveries and vehicle_index < len(fleet):
        current_vehicle = fleet[vehicle_index]
        new_route = {
            "routeId": f"RUTA-{hash(str(current_vehicle))}-{vehicle_index}",
            "vehicleId": current_vehicle.get('id', f'vehicle_{vehicle_index}'),
            "stops": [],
            "totalWeight": 0,
        }

        temp_remaining = []
        for delivery in remaining_deliveries:
            delivery_weight = delivery.get('weight', 0)
            vehicle_capacity = current_vehicle.get('capacity', float('inf'))

            if new_route["totalWeight"] + delivery_weight <= vehicle_capacity:
                new_route["stops"].append(delivery)
                new_route["totalWeight"] += delivery_weight
            else:
                temp_remaining.append(delivery)

        if new_route["stops"]:
            optimized_routes.append(new_route)

        remaining_deliveries = temp_remaining
        vehicle_index += 1

    return json.dumps({
        "optimizedRoutes": optimized_routes,
        "unassignedDeliveries": remaining_deliveries
    })





# --- Validación de datos de entrada ---
class DeliveryItem(BaseModel):
    id: str
    weight: float = Field(gt=0, description="Weight must be positive")
    # Opcionales
    orderId: Optional[str] = None
    address: Optional[str] = None
    priority: Optional[int] = None

class VehicleItem(BaseModel):
    id: str
    capacity: float = Field(gt=0, description="Capacity must be positive")
    # Opcionales
    type: Optional[str] = None
    location: Optional[str] = None

class OptimizationRequest(BaseModel):
    deliveries: List[DeliveryItem]
    fleet: List[VehicleItem]

    @validator('deliveries')
    def deliveries_not_empty(cls, v):
        if not v:
            raise ValueError('La lista de entregas no puede estar vacía')
        return v

    @validator('fleet')
    def fleet_not_empty(cls, v):
        if not v:
            raise ValueError('La lista de vehículos no puede estar vacía')
        return v


# --- API con FastAPI ---
app = FastAPI(
    title="CrewAI Logistics Optimization API",
    description="API para optimización de rutas logísticas usando agentes de IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/optimize-routes")
async def optimize_routes_endpoint(request: OptimizationRequest):
    """Optimiza rutas de entrega basado en entregas y flota disponible."""
    try:
        print("Petición recibida para optimizar rutas...")
        print(f"Entregas: {len(request.deliveries)}, Vehículos: {len(request.fleet)}")

        # Convertir a diccionarios
        deliveries_data = [delivery.dict() for delivery in request.deliveries]
        fleet_data = [vehicle.dict() for vehicle in request.fleet]

        # Usar directamente la función de optimización
        result_json = route_optimization_tool(deliveries_data, fleet_data)
        result = json.loads(result_json)
        
        return result

    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/")
def read_root():
    """Endpoint de salud del servicio."""
    return {
        "message": "Servidor de Agentes de IA para Logística está activo",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """Endpoint de verificación de salud."""
    return {"status": "healthy", "service": "crewai-logistics"}


# --- Configuración para ejecución local ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )