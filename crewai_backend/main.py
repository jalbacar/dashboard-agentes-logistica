# crewai_backend/main.py
import json
import os
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

try:
    from crewai import Agent, Task, Crew, Process
    from langchain_openai import ChatOpenAI
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

def route_optimization_tool(deliveries_data: List[Dict], fleet_data: List[Dict]) -> Dict:
    """
    Optimiza rutas de entrega basado en entregas y flota disponible.
    """
    if not deliveries_data or not fleet_data:
        return {
            "optimizedRoutes": [],
            "unassignedDeliveries": deliveries_data or []
        }

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

    return {
        "optimizedRoutes": optimized_routes,
        "unassignedDeliveries": remaining_deliveries
    }

# Configurar CrewAI si está disponible
if CREWAI_AVAILABLE:
    try:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY", "sk-fake-key-for-demo")
        )

        logistics_coordinator = Agent(
            role='Coordinador de Logística',
            goal='Optimizar la asignación de entregas a vehículos para maximizar eficiencia',
            backstory="""Eres un experto coordinador de logística con años de experiencia 
            en optimización de rutas y gestión de flotas.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

        route_analyst = Agent(
            role='Analista de Rutas',
            goal='Analizar y validar las rutas optimizadas propuestas',
            backstory="""Eres un analista especializado en validación de rutas logísticas.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )
    except Exception as e:
        print(f"Error configurando CrewAI: {e}")
        CREWAI_AVAILABLE = False

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
    """Optimiza rutas usando agentes de CrewAI o algoritmo básico."""
    try:
        print("Iniciando optimización...")
        
        deliveries_data = [d.dict() for d in request.deliveries]
        fleet_data = [v.dict() for v in request.fleet]
        
        if CREWAI_AVAILABLE and os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-fake-key-for-demo":
            try:
                print("Usando CrewAI para optimización...")
                
                # Crear tareas
                optimization_task = Task(
                    description=f"""
                    Optimiza la asignación de entregas a vehículos:
                    
                    Entregas: {json.dumps(deliveries_data)}
                    Flota: {json.dumps(fleet_data)}
                    
                    Asegúrate de que ningún vehículo exceda su capacidad.
                    Devuelve un JSON con rutas optimizadas.
                    """,
                    agent=logistics_coordinator,
                    expected_output="JSON con rutas optimizadas y entregas no asignadas"
                )
                
                analysis_task = Task(
                    description="Analiza las rutas optimizadas y valida que sean eficientes.",
                    agent=route_analyst,
                    expected_output="Análisis de validación de las rutas"
                )
                
                # Crear y ejecutar crew
                crew = Crew(
                    agents=[logistics_coordinator, route_analyst],
                    tasks=[optimization_task, analysis_task],
                    verbose=2,
                    process=Process.sequential
                )
                
                result = crew.kickoff()
                
                # Intentar usar resultado de CrewAI, sino usar algoritmo básico
                try:
                    if hasattr(optimization_task, 'output') and optimization_task.output:
                        crew_result = json.loads(optimization_task.output.raw)
                        crew_result["optimization_method"] = "crewai_agents"
                        crew_result["crewai_used"] = True
                        crew_result["message"] = "Optimización realizada con agentes de CrewAI"
                        crew_result["agents_used"] = ["Coordinador de Logística", "Analista de Rutas"]
                        return crew_result
                except Exception as parse_error:
                    print(f"Error parseando resultado de CrewAI: {parse_error}")
                    # Si CrewAI ejecutó pero no podemos parsear, usar algoritmo básico
                    result = route_optimization_tool(deliveries_data, fleet_data)
                    result["optimization_method"] = "basic_algorithm_after_crewai_error"
                    result["crewai_used"] = False
                    result["message"] = "CrewAI ejecutó pero hubo error en el resultado. Usando algoritmo básico."
                    return result
                    
            except Exception as e:
                print(f"Error con CrewAI: {e}")
        
        # Fallback al algoritmo básico
        print("Usando algoritmo básico...")
        result = route_optimization_tool(deliveries_data, fleet_data)
        result["optimization_method"] = "basic_algorithm"
        result["crewai_used"] = False
        result["message"] = "Optimización realizada con algoritmo básico"
        return result
            
    except Exception as e:
        print(f"Error general: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/")
def read_root():
    return {
        "message": "CrewAI Logistics API está activo",
        "status": "healthy",
        "version": "2.0.0",
        "crewai_available": CREWAI_AVAILABLE,
        "agents": ["Coordinador de Logística", "Analista de Rutas"] if CREWAI_AVAILABLE else []
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "crewai-logistics"}

@app.get("/crewai-status")
def crewai_status():
    """Verificar el estado de CrewAI y configuración."""
    openai_key = os.getenv("OPENAI_API_KEY", "")
    has_valid_key = openai_key and openai_key != "sk-fake-key-for-demo" and len(openai_key) > 10
    
    return {
        "crewai_available": CREWAI_AVAILABLE,
        "openai_key_configured": has_valid_key,
        "will_use_crewai": CREWAI_AVAILABLE and has_valid_key,
        "agents": ["Coordinador de Logística", "Analista de Rutas"] if CREWAI_AVAILABLE else [],
        "fallback_method": "basic_algorithm",
        "message": "CrewAI listo para usar" if (CREWAI_AVAILABLE and has_valid_key) else "Usando algoritmo básico"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)