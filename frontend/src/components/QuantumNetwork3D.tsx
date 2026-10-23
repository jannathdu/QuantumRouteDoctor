import { Canvas } from "@react-three/fiber";
import { OrbitControls, Text } from "@react-three/drei";
type Position = [number, number, number];
const nodes: { id: string; position: Position }[] = [{ id: "A", position: [-3, 0, 0] }, { id: "B", position: [0, 1.5, -1] }, { id: "C", position: [3, 0, 0] }, { id: "D", position: [0, -1.5, 1] }];
const links = [{ source: "A", target: "B", active: true }, { source: "B", target: "C", active: true }, { source: "A", target: "D", active: false }, { source: "D", target: "C", active: false }];
function QuantumNode({ id, position, selected, onSelect }: { id: string; position: Position; selected: boolean; onSelect: (id: string) => void }) { return <group position={position}><mesh onClick={(event) => { event.stopPropagation(); onSelect(id); }}><sphereGeometry args={[0.35, 32, 32]} /><meshStandardMaterial color={selected ? "#facc15" : "#00d9ff"} emissive={selected ? "#b45309" : "#0077aa"} emissiveIntensity={0.6} /></mesh><Text position={[0, 0.65, 0]} fontSize={0.35} color="white" anchorX="center" anchorY="middle">{id}</Text></group>; }
import * as THREE from "three";
function QuantumLink({ start, end, active }: { start: Position; end: Position; active: boolean }) { const a = new THREE.Vector3(...start); const b = new THREE.Vector3(...end); const direction = b.clone().sub(a); const middle = a.clone().add(b).multiplyScalar(0.5); const rotation = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,1,0), direction.clone().normalize()); return <mesh position={middle} quaternion={rotation}><cylinderGeometry args={[active ? 0.065 : 0.025, active ? 0.065 : 0.025, direction.length(), 12]} /><meshStandardMaterial color={active ? "#00ff99" : "#64748b"} emissive={active ? "#00aa66" : "#000000"} emissiveIntensity={active ? 0.8 : 0} /></mesh>; }
function NetworkScene({ selectedNode, onSelect }: { selectedNode: string | null; onSelect: (id: string) => void }) { return <>{nodes.map((node) => <QuantumNode key={node.id} id={node.id} position={node.position} selected={selectedNode === node.id} onSelect={onSelect} />)}{links.map((link) => { const start = nodes.find((n) => n.id === link.source); const end = nodes.find((n) => n.id === link.target); if (!start || !end) return null; return <QuantumLink key={`${link.source}-${link.target}`} start={start.position} end={end.position} active={link.active} />; })}</>; }
export default function QuantumNetwork3D() { const [selectedNode, setSelectedNode] = useState<string | null>(null); return <div style={{ width: "100%", height: "600px", background: "#050b18", borderRadius: "16px" }}><Canvas camera={{ position: [0, 2, 9], fov: 55 }}><ambientLight intensity={0.6} /><pointLight position={[4, 5, 5]} intensity={30} /><NetworkScene selectedNode={selectedNode} onSelect={setSelectedNode} /><OrbitControls enablePan enableZoom enableRotate /></Canvas><NodeInspector selectedNode={selectedNode} /></div>; }
import { useState } from "react";








import NodeInspector from "./NodeInspector";

