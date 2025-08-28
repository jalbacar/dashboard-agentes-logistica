# crewai_backend/main.py
import json
import os
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_openai import ChatOpenAI

# Configurar LLM
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY", "sk-fake-key-for-demo")
)

@tool
def route_optimization_tool(deliveries: str, fleet: str) -> str:
    """
    Optimiza rutas de entrega basado en entregas y flota disponible.
    Args:
        deliveries: JSON string con lista de entregas
        fleet: JSON string con lista de vehículos
    Returns:
        JSON string con rutas optimizadas
    """
    try:
        deliveries_data = json.loads(deliveries)
        fleet_data = json.loads(fleet)
        
        if not deliveries_data or not fleet_data:
            return json.dumps({
                "optimizedRoutes": [],
                "unassignedDeliveries": deliveries_data or []
            })

        optimized_routes = []
        remaining_deliveries = list(deliveries_data)
        vehicle_index = 0

        while remaining_deliveries and vehicle_index < len(fleet_data):
            current_vehicle = fleet_data[vehicle_index]
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
    except Exception as e:
        return json.dumps({"error": str(e)})

# Crear agentes
logistics_coordinator = Agent(
    role='Coordinador de Logística',
    goal='Optimizar la asignación de entregas a vehículos para maximizar eficiencia',
    backstory="""Eres un experto coordinador de logística con años de experiencia 
    en optimización de rutas y gestión de flotas. Tu objetivo es encontrar la 
    mejor asignación de entregas considerando capacidades de vehículos.""",
    verbose=True,
    allow_delegation=False,
    llm=llm,
    tools=[route_optimization_tool]
)

route_analyst = Agent(
    role='Analista de Rutas',
    goal='Analizar y validar las rutas optimizadas propuestas',
    backstory="""Eres un analista especializado en validación de rutas logísticas.
    Tu trabajo es revisar las asignaciones propuestas y asegurar que cumplan
    con las restricciones de capacidad y eficiencia.""",
    verbose=True,
    allow_delegation=False,
    llm=llm
)

# Modelos Pydantic
class DeliveryItem(BaseModel):
    id: str
    weight: float = Field(gt=0, description="Weight must be positive")
    orderId: Optional[str] = None
    address: Optional[str] = None
    priority: Optional[int] = None

class VehicleItem(BaseModel):
    id: str
    capacity: float = Field(gt=0, description="Capacity must be positive")
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

# FastAPI App
app = FastAPI(
    title="CrewAI Logistics Optimization API",
    description="API para optimización de rutas logísticas usando agentes de IA",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/optimize-routes")
async def optimize_routes_endpoint(request: OptimizationRequest):
    """Optimiza rutas usando agentes de CrewAI."""
    try:
        print("Iniciando optimización con CrewAI...")
        
        deliveries_json = json.dumps([d.dict() for d in request.deliveries])
        fleet_json = json.dumps([v.dict() for v in request.fleet])
        
        # Crear tareas
        optimization_task = Task(
            description=f"""
            Optimiza la asignación de entregas a vehículos usando los siguientes datos:
            
            Entregas: {deliveries_json}
            Flota: {fleet_json}
            
            Usa la herramienta route_optimization_tool para calcular las rutas óptimas.
            Asegúrate de que ningún vehículo exceda su capacidad.
            """,
            agent=logistics_coordinator,
            expected_output="JSON con rutas optimizadas y entregas no asignadas"
        )
        
        analysis_task = Task(
            description="""
            Analiza las rutas optimizadas del coordinador y valida que:
            1. Ningún vehículo exceda su capacidad
            2. Todas las entregas estén consideradas
            3. La asignación sea eficiente
            
            Proporciona un resumen del análisis.
            """,
            agent=route_analyst,
            expected_output="Análisis de validación de las rutas optimizadas"
        )
        
        # Crear y ejecutar crew
        crew = Crew(
            agents=[logistics_coordinator, route_analyst],
            tasks=[optimization_task, analysis_task],
            verbose=2,
            process=Process.sequential
        )
        
        result = crew.kickoff()
        
        # Extraer resultado JSON del primer task
        optimization_result = optimization_task.output.raw
        
        try:
            # Intentar parsear como JSON
            parsed_result = json.loads(optimization_result)
            return parsed_result
        except json.JSONDecodeError:
            # Si no es JSON válido, usar resultado básico
            deliveries_data = [d.dict() for d in request.deliveries]
            fleet_data = [v.dict() for v in request.fleet]
            fallback_result = route_optimization_tool(deliveries_json, fleet_json)
            return json.loads(fallback_result)
            
    except Exception as e:
        print(f"Error en CrewAI: {str(e)}")
        # Fallback a algoritmo básico
        deliveries_data = [d.dict() for d in request.deliveries]
        fleet_data = [v.dict() for v in request.fleet]
        deliveries_json = json.dumps(deliveries_data)
        fleet_json = json.dumps(fleet_data)
        fallback_result = route_optimization_tool(deliveries_json, fleet_json)
        return json.loads(fallback_result)

@app.get("/")
def read_root():
    return {
        "message": "CrewAI Logistics API está activo",
        "status": "healthy",
        "version": "2.0.0",
        "agents": ["Coordinador de Logística", "Analista de Rutas"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "crewai-logistics"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)