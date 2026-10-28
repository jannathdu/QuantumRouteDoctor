import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
type Position = [number, number, number];
const nodeLayout: { id: string; position: Position }[] = [{ id: "A", position: [-3, 0, 0] }, { id: "B", position: [0, 1.5, -1] }, { id: "C", position: [3, 0, 0] }, { id: "D", position: [0, -1.5, 1] }];

function QuantumNode({ id, position, selected, onSelect }: { id: string; position: Position; selected: boolean; onSelect: (id: string) => void }) { return <group position={position}><mesh onClick={(event) => { event.stopPropagation(); onSelect(id); }}><sphereGeometry args={[0.35, 32, 32]} /><meshStandardMaterial color={selected ? "#facc15" : "#00d9ff"} emissive={selected ? "#b45309" : "#0077aa"} emissiveIntensity={0.6} /></mesh><Text position={[0, 0.65, 0]} fontSize={0.35} color="white" anchorX="center" anchorY="middle">{id}</Text></group>; }
import * as THREE from "three";
function QuantumLink({ start, end, active }: { start: Position; end: Position; active: boolean }) { const a = new THREE.Vector3(...start); const b = new THREE.Vector3(...end); const direction = b.clone().sub(a); const middle = a.clone().add(b).multiplyScalar(0.5); const rotation = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), direction.clone().normalize()); return <mesh position={middle} quaternion={rotation}><cylinderGeometry args={[active ? 0.065 : 0.025, active ? 0.065 : 0.025, direction.length(), 12]} /><meshStandardMaterial color={active ? "#00ff99" : "#64748b"} emissive={active ? "#00aa66" : "#000000"} emissiveIntensity={active ? 0.8 : 0} /></mesh>; }
function NetworkScene({ selectedNode, onSelect, nodes, links }: { selectedNode: string | null; onSelect: (id: string) => void; nodes: { id: string; position: Position }[]; links: { source: string; target: string; active: boolean }[] }) { return <>{nodes.map((node) => <QuantumNode key={node.id} id={node.id} position={node.position} selected={selectedNode === node.id} onSelect={onSelect} />)}{links.map((link) => { const start = nodes.find((n) => n.id === link.source); const end = nodes.find((n) => n.id === link.target); if (!start || !end) return null; return <QuantumLink key={`${link.source}-${link.target}`} start={start.position} end={end.position} active={link.active} />; })}</>; }
export default function QuantumNetwork3D() { const [selectedNode, setSelectedNode] = useState<string | null>(null); const [networkData, setNetworkData] = useState<NetworkResponse | null>(null); const [routeData, setRouteData] = useState<RouteResponse | TemporalRouteResponse | null>(null); const [comparisonData, setComparisonData] = useState<ComparisonResponse | null>(null); const [routeLoading, setRouteLoading] = useState(false); const [routeError, setRouteError] = useState<string | null>(null); const routeControllerRef = useRef<AbortController | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState<string | null>(null); useEffect(() => { let cancelled = false; fetchNetwork().then((data) => { if (!cancelled) setNetworkData(data); }).catch((err: unknown) => { if (!cancelled) setError(err instanceof Error ? err.message : "Network request failed"); }).finally(() => { if (!cancelled) setLoading(false); }); return () => { cancelled = true; }; }, []); useEffect(() => { const controller = new AbortController(); routeControllerRef.current = controller; fetchRoute("A", "C", 0.8, controller.signal).then((data) => { if (!controller.signal.aborted) setRouteData(data); }).catch((err: unknown) => { if (!controller.signal.aborted) setRouteError(err instanceof Error ? err.message : "Routing request failed"); }); return () => { controller.abort(); }; }, []); const apiLinks = (networkData?.links ?? []).map((link) => ({ source: link.source, target: link.target, active: Boolean(routeData?.feasible && routeData.selected_route?.some((node, i, path) => i < path.length - 1 && ((node === link.source && path[i + 1] === link.target) || (node === link.target && path[i + 1] === link.source)))) })); const apiNodes = (networkData?.nodes ?? []).map((node, index) => ({ id: node.id, position: nodeLayout.find((item) => item.id === node.id)?.position ?? [Math.cos(index) * 3, Math.sin(index) * 3, 0] as Position })); return <div style={{ width: "100%", height: "600px", background: "#050b18", borderRadius: "16px" }}><Canvas camera={{ position: [0, 2, 9], fov: 55 }}><ambientLight intensity={0.6} /><pointLight position={[4, 5, 5]} intensity={30} /><NetworkScene selectedNode={selectedNode} onSelect={setSelectedNode} nodes={apiNodes} links={apiLinks} /><OrbitControls enablePan enableZoom enableRotate /></Canvas><NetworkStatus data={networkData} loading={loading} error={error} /><NodeInspector selectedNode={selectedNode} networkData={networkData} /><RoutingControls calculating={routeLoading} nodeIds={(networkData?.nodes ?? []).map((node) => node.id)} onCalculate={(source, destination, minimumFidelity, algorithm, maximumAoi) => { routeControllerRef.current?.abort(); const controller = new AbortController(); routeControllerRef.current = controller; setRouteLoading(true); setRouteData(null); setComparisonData(null); setRouteError(null); const comparisonRequest = fetchComparison(source, destination, minimumFidelity, maximumAoi, controller.signal).then((data) => { if (!controller.signal.aborted) setComparisonData(data); }).catch((err: unknown) => { if (!controller.signal.aborted) setRouteError(err instanceof Error ? err.message : "Comparison request failed"); }); const routingRequest = (algorithm === "temporal" ? fetchTemporalRoute(source, destination, minimumFidelity, maximumAoi, 10, controller.signal) : fetchRoute(source, destination, minimumFidelity, controller.signal)).then((data) => { if (!controller.signal.aborted) setRouteData(data); }).catch((err: unknown) => { if (!controller.signal.aborted) setRouteError(err instanceof Error ? err.message : "Routing request failed"); }); Promise.allSettled([comparisonRequest, routingRequest]).then(() => { if (!controller.signal.aborted) setRouteLoading(false); }); }} />{routeError && <p role="alert" style={{ color: "#f87171", padding: 12 }}>Routing Error: {routeError}</p>}<RoutingResults route={routeData} /><ComparisonResults data={comparisonData} /><FidelityDecayPanel /><AoISweepPanel nodeIds={(networkData?.nodes ?? []).map((node) => node.id)} /></div>; }
import { useEffect, useRef, useState } from "react";








import NodeInspector from "./NodeInspector";

import { fetchNetwork } from "../api/network";
import type { NetworkResponse } from "../api/network";




import NetworkStatus from "./NetworkStatus";








import { fetchRoute } from "../api/routes";
import type { RouteResponse } from "../api/routes";



import RoutingResults from "./RoutingResults";



import RoutingControls from "./RoutingControls";




import { fetchTemporalRoute } from "../api/temporalRoutes";
import type { TemporalRouteResponse } from "../api/temporalRoutes";





import { fetchComparison } from "../api/comparison";
import type { ComparisonResponse } from "../api/comparison";
import ComparisonResults from "./ComparisonResults";
import FidelityDecayPanel from "./FidelityDecayPanel";
import AoISweepPanel from "./AoISweepPanel";
