from fastapi import FastAPI
app = FastAPI(title="QuantumRoute Doctor API", version="0.1.0")
@app.get("/api/health")
def health_check(): return {"status": "ok", "service": "QuantumRoute Doctor API"}
from backend.core.network import create_quantum_network

@app.get("/api/network")
def get_network():
    graph = create_quantum_network(0.95, 0.05, 0.94, 0.06, 0.92, 0.08, 0.91, 0.09)
    nodes = [{"id": node} for node in graph.nodes()]
    links = [{"source": u, "target": v, **data} for u, v, data in graph.edges(data=True)]
    return {"nodes": nodes, "links": links, "data_source": "demo"}
from backend.core.fidelity_routing import find_fidelity_constrained_route
from fastapi import Query, HTTPException

@app.get("/api/routes")
def get_routes(source: str = "A", destination: str = "C", minimum_fidelity: float = Query(0.8, ge=0.25, le=1.0)):
    graph = create_quantum_network(0.95, 0.05, 0.94, 0.06, 0.92, 0.08, 0.91, 0.09)
    graph = create_quantum_network(0.95, 0.05, 0.94, 0.06, 0.92, 0.08, 0.91, 0.09)
    if source not in graph or destination not in graph or source == destination:
        raise HTTPException(status_code=422, detail="Invalid source or destination")
    result = find_fidelity_constrained_route(graph, source, destination, minimum_fidelity)
    result = find_fidelity_constrained_route(graph, source, destination, minimum_fidelity)
    return {"source": source, "destination": destination, "minimum_fidelity": minimum_fidelity, "algorithm": "fidelity_constrained", "feasible": result is not None, "selected_route": result["route"] if result else None, "end_to_end_fidelity": result["end_to_end_fidelity"] if result else None, "hop_count": result["hop_count"] if result else None, "data_source": "demo"}
    return {"source": source, "destination": destination, "minimum_fidelity": minimum_fidelity, "algorithm": "fidelity_constrained", "feasible": result is not None, "selected_route": result["route"] if result else None, "end_to_end_fidelity": result["end_to_end_fidelity"] if result else None, "hop_count": result["hop_count"] if result else None, "data_source": "demo"}
