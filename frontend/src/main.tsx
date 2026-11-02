import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import "./style.css";
type Experiment = { id:number; name:string; accuracy:number; latency_ms:number; created_at:string };
type Case = { prompt:string; expected:string };
function App() {
  const [items,setItems]=useState<Experiment[]>([]);
  const [name,setName]=useState("Baseline comparison");
  const [strategy,setStrategy]=useState("echo");
  const [cases,setCases]=useState('[{"prompt":"hello","expected":"hello"},{"prompt":"WORLD","expected":"WORLD"}]');
  const [message,setMessage]=useState("");
  const refresh=async()=>{try{const r=await fetch("/api/experiments");if(!r.ok)throw Error("Could not load experiments");setItems(await r.json());}catch(e){setMessage(String(e));}};
  useEffect(()=>{void refresh();},[]);
  async function submit(e:React.FormEvent) {
    e.preventDefault();setMessage("");
    try {
      const parsed:Case[]=JSON.parse(cases);
      const r=await fetch("/api/experiments",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name,strategy,cases:parsed})});
      if(!r.ok)throw Error(await r.text());
      const data=await r.json();setMessage("Experiment #"+data.id+" completed");await refresh();
    } catch(e){setMessage("Error: "+String(e));}
  }
  return <main><header><span className="eyebrow">MODEL EVALUATION LAB</span><h1>AgentBench</h1><p>Compare deterministic strategies and inspect accuracy, latency and experiment history.</p></header>
    <section className="grid"><article><h2>Run evaluation</h2><form onSubmit={submit}><label>Name<input value={name} onChange={e=>setName(e.target.value)} required/></label><label>Strategy<select value={strategy} onChange={e=>setStrategy(e.target.value)}><option value="echo">Echo</option><option value="lowercase">Lowercase</option><option value="reverse">Reverse</option></select></label><label>Test cases (JSON)<textarea rows={9} value={cases} onChange={e=>setCases(e.target.value)}/></label><button>Run benchmark</button></form><p role="status">{message}</p></article>
    <article><h2>Experiment history</h2><div className="table"><table><thead><tr><th>Name</th><th>Accuracy</th><th>Avg latency</th></tr></thead><tbody>{items.map(x=><tr key={x.id}><td>{x.name}</td><td>{Math.round(x.accuracy*100)}%</td><td>{x.latency_ms.toFixed(3)} ms</td></tr>)}</tbody></table></div>{items.length===0&&<p>No experiments yet.</p>}</article></section><footer>Baseline demo — no real LLM provider is connected yet.</footer></main>;
}
createRoot(document.getElementById("root")!).render(<React.StrictMode><App/></React.StrictMode>);
