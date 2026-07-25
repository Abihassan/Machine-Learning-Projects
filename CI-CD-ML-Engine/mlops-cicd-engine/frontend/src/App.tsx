import { HashRouter, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import PipelineDetail from "./pages/PipelineDetail";
import ModelRegistry from "./pages/ModelRegistry";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <HashRouter>
      <div className="min-h-screen flex bg-base">
        <Sidebar />
        <main className="flex-1 px-8 py-8 max-w-6xl">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/runs/:runId" element={<PipelineDetail />} />
            <Route path="/models" element={<ModelRegistry />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </HashRouter>
  );
}
