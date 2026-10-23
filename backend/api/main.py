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
