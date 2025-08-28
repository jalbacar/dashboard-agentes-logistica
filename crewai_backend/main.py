# crewai_backend/main.py
import json
import os
from typing import List, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

try:
    from langchain_openai import ChatOpenAI
    from langchain_ollama import ChatOllama
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

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

async def llm_optimize_routes(deliveries_data: List[Dict], fleet_data: List[Dict], llm) -> Dict:
    """
    Usa LLM para optimizar rutas de manera más inteligente.
    """
    prompt = f"""
    Eres un experto en optimización logística. Optimiza la asignación de estas entregas a vehículos:

    ENTREGAS: {json.dumps(deliveries_data)}
    VEHÍCULOS: {json.dumps(fleet_data)}

    REGLAS:
    1. Ningún vehículo puede exceder su capacidad
    2. Minimiza el número de vehículos usados
    3. Distribuye eficientemente las entregas

    Responde SOLO con un JSON válido con esta estructura:
    {{
        "optimizedRoutes": [
            {{
                "routeId": "RUTA-X",
                "vehicleId": "id_vehiculo",
                "stops": [lista_de_entregas],
                "totalWeight": peso_total
            }}
        ],
        "unassignedDeliveries": [entregas_no_asignadas]
    }}
    """
    
    try:
        response = await llm.ainvoke(prompt)
        result_text = response.content if hasattr(response, 'content') else str(response)
        
        # Extraer JSON del texto
        import re
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            raise ValueError("No se encontró JSON válido en la respuesta")
            
    except Exception as e:
        print(f"Error con LLM: {e}")
        # Fallback al algoritmo básico - agregar marca para identificarlo
        result = route_optimization_tool(deliveries_data, fleet_data)
        result["_internal_fallback"] = True  # Marca interna
        return result

# Configurar LLM si está disponible
llm = None
if LLM_AVAILABLE:
    try:
        llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
        
        if llm_provider == "ollama":
            ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
            ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            llm = ChatOllama(
                model=ollama_model,
                base_url=ollama_base_url,
                temperature=0.1
            )
        else:
            # Default a OpenAI
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.1,
                api_key=os.getenv("OPENAI_API_KEY", "sk-fake-key-for-demo")
            )
    except Exception as e:
        print(f"Error configurando LLM: {e}")
        LLM_AVAILABLE = False

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
    title="AI Logistics Optimization API",
    description="API para optimización de rutas logísticas usando LLM (OpenAI/Ollama)",
    version="3.0.0"
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
    """Optimiza rutas usando LLM (OpenAI/Ollama) o algoritmo básico."""
    try:
        print("Iniciando optimización...")
        
        deliveries_data = [d.dict() for d in request.deliveries]
        fleet_data = [v.dict() for v in request.fleet]
        
        # Verificar si podemos usar LLM
        can_use_llm = False
        if LLM_AVAILABLE and llm:
            llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
            if llm_provider == "ollama":
                can_use_llm = True  # Ollama no necesita API key
            elif os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-fake-key-for-demo":
                can_use_llm = True
        
        if can_use_llm:
            try:
                print(f"Usando LLM ({os.getenv('LLM_PROVIDER', 'openai')}) para optimización...")
                result = await llm_optimize_routes(deliveries_data, fleet_data, llm)
                
                # Verificar si el resultado viene del LLM o del fallback interno
                if result.get("_internal_fallback"):
                    # Si llm_optimize_routes usó fallback interno
                    result.pop("_internal_fallback", None)  # Remover marca interna
                    result["optimization_method"] = "basic_algorithm_after_llm_error"
                    result["llm_used"] = False
                    result["message"] = f"LLM ({os.getenv('LLM_PROVIDER', 'openai')}) falló. Usando algoritmo básico."
                else:
                    # Si llm_optimize_routes devolvió resultado del LLM
                    result["optimization_method"] = f"llm_{os.getenv('LLM_PROVIDER', 'openai')}"
                    result["llm_used"] = True
                    result["message"] = f"Optimización realizada con {os.getenv('LLM_PROVIDER', 'openai').upper()}"
                
                return result
                    
            except Exception as e:
                print(f"Error con LLM: {e}")
                # Fallback explícito
                result = route_optimization_tool(deliveries_data, fleet_data)
                result["optimization_method"] = "basic_algorithm_after_llm_exception"
                result["llm_used"] = False
                result["message"] = f"Excepción en LLM ({os.getenv('LLM_PROVIDER', 'openai')}). Usando algoritmo básico."
                return result
        
        # Fallback al algoritmo básico
        print("Usando algoritmo básico...")
        result = route_optimization_tool(deliveries_data, fleet_data)
        result["optimization_method"] = "basic_algorithm"
        result["llm_used"] = False
        result["message"] = "Optimización realizada con algoritmo básico"
        return result
            
    except Exception as e:
        print(f"Error general: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/")
def read_root():
    return {
        "message": "AI Logistics API está activo",
        "status": "healthy",
        "version": "3.0.0",
        "llm_available": LLM_AVAILABLE,
        "supported_providers": ["openai", "ollama"]
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "ai-logistics"}

@app.get("/llm-status")
def llm_status():
    """Verificar el estado del LLM y configuración."""
    llm_provider = os.getenv("LLM_PROVIDER", "openai").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    has_valid_openai_key = openai_key and openai_key != "sk-fake-key-for-demo" and len(openai_key) > 10
    
    can_use_llm = False
    llm_info = {}
    
    if LLM_AVAILABLE:
        if llm_provider == "ollama":
            can_use_llm = True
            llm_info = {
                "provider": "ollama",
                "model": os.getenv("OLLAMA_MODEL", "llama3.2"),
                "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            }
        elif has_valid_openai_key:
            can_use_llm = True
            llm_info = {
                "provider": "openai",
                "model": "gpt-3.5-turbo"
            }
    
    return {
        "llm_available": LLM_AVAILABLE,
        "llm_provider": llm_provider,
        "llm_info": llm_info,
        "openai_key_configured": has_valid_openai_key,
        "will_use_llm": can_use_llm,
        "fallback_method": "basic_algorithm",
        "message": f"LLM listo con {llm_provider}" if can_use_llm else "Usando algoritmo básico"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)