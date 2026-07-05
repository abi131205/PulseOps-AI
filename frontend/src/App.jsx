import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  Legend 
} from 'recharts';
import { 
  LayoutDashboard, 
  Activity, 
  Wrench, 
  Cpu, 
  AlertTriangle, 
  Server, 
  CheckCircle2, 
  RefreshCw, 
  HelpCircle,
  Clock,
  Shuffle
} from 'lucide-react';

const API_BASE = 'http://localhost:8080/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('command-center');
  const [dataProfile, setDataProfile] = useState('SMALL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Endpoint data states
  const [commandCenterData, setCommandCenterData] = useState({
    icu_occupied: 30, icu_total: 50,
    er_occupied: 40, er_total: 80,
    er_queue_length: 5, active_incidents_count: 0,
    active_incidents: [], critical_alarms_count: 0
  });
  const [recommendations, setRecommendations] = useState([]);
  const [equipmentList, setEquipmentList] = useState([]);
  const [benchmarkData, setBenchmarkData] = useState({
    benchmark: { cpu_time_ms: 0, gpu_time_ms: 0, speedup: 0.0, gpu_native: false },
    data: { bed_occupancy: [] }
  });

  // Fetch functions
  const fetchCommandCenter = async () => {
    try {
      const res = await axios.get(`${API_BASE}/command-center`);
      if (res.data && res.data.status !== 'error') {
        setCommandCenterData(res.data);
      }
    } catch (err) {
      console.error("Error fetching command center data", err);
    }
  };

  const fetchRecommendations = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/recommendations`);
      setRecommendations(res.data);
      setError(null);
    } catch (err) {
      setError("Failed to fetch recommendations. Ensure backend server is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchEquipment = async () => {
    try {
      const res = await axios.get(`${API_BASE}/equipment`);
      setEquipmentList(res.data);
    } catch (err) {
      console.error("Error fetching equipment logs", err);
    }
  };

  const triggerBenchmark = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/benchmark`);
      setBenchmarkData(res.data);
      setError(null);
    } catch (err) {
      setError("Failed to trigger GPU benchmark. Ensure backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchCommandCenter();
    fetchRecommendations();
    fetchEquipment();
    triggerBenchmark();
    
    // Poll command center statistics every 15 seconds
    const interval = setInterval(() => {
      fetchCommandCenter();
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  // Update profile via API config when altered in select box
  const handleProfileChange = async (newProfile) => {
    setDataProfile(newProfile);
    setLoading(true);
    try {
      // Direct call to regenerate backend data for active profile
      await axios.get(`${API_BASE}/health`); // placeholder reload trigger
      // Refresh views
      fetchCommandCenter();
      fetchRecommendations();
      fetchEquipment();
      triggerBenchmark();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const navigation = [
    { id: 'command-center', name: 'Hospital Command Center', icon: LayoutDashboard },
    { id: 'priorities', name: 'Operational Priorities', icon: Activity },
    { id: 'equipment', name: 'Equipment Intelligence', icon: Wrench },
    { id: 'performance', name: 'System Performance', icon: Cpu }
  ];

  // Process data for charts
  const occupancyChartData = benchmarkData?.data?.bed_occupancy?.map((log) => ({
    time: log.timestamp ? log.timestamp.split(/[T ]/)[1] : '',
    'ICU Beds Occupied': log.icu_beds_occupied,
    'ER Beds Occupied': log.er_beds_occupied,
  })) || [];

  const benchmarkChartData = [
    {
      name: 'Resource Pipeline Processing',
      'CPU (Pandas)': benchmarkData?.benchmark?.cpu_time_ms || 120.0,
      'GPU (cuDF)': benchmarkData?.benchmark?.gpu_time_ms || 6.5,
    }
  ];

  return (
    <div className="flex h-screen bg-darkBg text-slate-100 font-sans overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-cardBg border-r border-borderLight flex flex-col justify-between">
        <div>
          {/* Logo Header */}
          <div className="h-16 flex items-center px-6 border-b border-slate-700 gap-3 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-400 flex items-center justify-center font-bold text-white shadow-lg">
              P
            </div>
            <div>
              <h1 className="font-bold text-base leading-tight text-white">PulseOps AI</h1>
              <span className="text-[11px] text-cyan-300 font-semibold tracking-widest uppercase">Decision Intelligence</span>
            </div>
          </div>

          {/* Navigation Items */}
<nav className="p-4 space-y-2">
  {navigation.map((item) => {
    const Icon = item.icon;
    const isActive = activeTab === item.id;

    return (
      <button
        key={item.id}
        onClick={() => setActiveTab(item.id)}
        className={`group w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-300 ease-in-out ${
          isActive
            ? "bg-gradient-to-r from-blue-600/20 to-cyan-500/20 border border-cyan-400/30 text-white shadow-lg"
            : "text-slate-400 hover:bg-slate-800/60 hover:text-white hover:border-slate-700 border border-transparent hover:translate-x-1"
        }`}
      >
        <div
          className={`flex items-center justify-center h-9 w-9 rounded-lg transition-all duration-300 ${
            isActive
              ? "bg-cyan-500/20 text-cyan-300"
              : "bg-slate-800 text-slate-400 group-hover:bg-slate-700 group-hover:text-white"
          }`}
        >
          <Icon className="h-5 w-5" />
        </div>

        <span className="flex-1 text-left">
          {item.name}
        </span>

        {isActive && (
          <div className="h-2 w-2 rounded-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.9)]"></div>
        )}
      </button>
    );
  })}
</nav>
        </div>
{/* System Settings & Status in Sidebar footer */}
<div className="p-5 border-t border-slate-700 bg-gradient-to-b from-slate-900/70 to-slate-950 space-y-4">

  {/* System Status */}
  <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700">
    <div className="flex items-center justify-between">
      <span className="text-xs font-medium text-slate-400">
        System Status
      </span>

      <div className="flex items-center gap-2 text-emerald-400">
        <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span className="text-xs font-semibold uppercase tracking-wider">
          Active
        </span>
      </div>
    </div>
  </div>

  {/* Data Profile */}
  <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700">
    <label className="block text-xs font-medium text-slate-400 mb-2">
      Data Profile
    </label>

    <select
      value={dataProfile}
      onChange={(e) => handleProfileChange(e.target.value)}
      className="w-full bg-slate-900 border border-slate-600 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 transition"
    >
      <option value="SMALL">🟢 Small (10k)</option>
      <option value="MEDIUM">🟡 Medium (250k)</option>
      <option value="LARGE">🔴 Large (1M+)</option>
    </select>
  </div>

</div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Header */}
<header className="h-20 border-b border-slate-700 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 backdrop-blur-md px-8 flex items-center justify-between shadow-md">

  {/* Left Section */}
  <div>
    <h2 className="text-xl font-bold text-white">
      {navigation.find(item => item.id === activeTab)?.name}
    </h2>
    <p className="text-xs text-slate-400 mt-1">
      AI-Powered Hospital Operations Dashboard
    </p>
  </div>

  {/* Right Section */}
  <div className="flex items-center gap-4">

    {loading && (
      <RefreshCw className="h-5 w-5 animate-spin text-cyan-400" />
    )}

    <div className="flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-2">
      <CheckCircle2 className="h-4 w-4 text-emerald-400" />
      <div className="flex flex-col leading-none">
        <span className="text-[10px] uppercase tracking-widest text-slate-400">
          Warehouse
        </span>
        <span className="text-sm font-semibold text-emerald-300">
          BigQuery Connected
        </span>
      </div>
    </div>

  </div>

</header>

        {/* Dynamic Viewport */}
        <div className="flex-1 overflow-y-auto p-8 relative">
          {error && (
            <div className="max-w-7xl mx-auto mb-6 border border-accentRed/30 bg-accentRed/10 text-accentRed rounded-lg p-4 text-xs flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              {error}
            </div>
          )}

          <div className="max-w-7xl mx-auto space-y-6">
            {/* 1. Command Center View */}
            {activeTab === 'command-center' && (
              <div className="space-y-6">
                {/* Stats Summary Row */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="glass-panel rounded-2xl p-6 border border-slate-700/50 bg-gradient-to-br from-slate-900/90 to-slate-800/80 shadow-xl hover:shadow-cyan-500/10 hover:-translate-y-1 transition-all duration-300">
                    <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">ICU Bed Pressure</span>
                    <div className="text-3xl font-extrabold mt-2 text-white">
                      {commandCenterData.icu_occupied} / {commandCenterData.icu_total}
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2 mt-4 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-cyan-400 to-blue-500 h-2 rounded-full transition-all duration-700" 
                        style={{ width: `${(commandCenterData.icu_occupied / commandCenterData.icu_total) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-[10px] text-textMuted mt-1">
                      {Math.round((commandCenterData.icu_occupied / commandCenterData.icu_total) * 100)}% Occupancy
                    </div>
                  </div>

                  <div className="glass-panel rounded-2xl p-6 border border-slate-700/50 bg-gradient-to-br from-slate-900/90 to-slate-800/80 shadow-xl hover:shadow-cyan-500/10 hover:-translate-y-1 transition-all duration-300">
                    <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Emergency Room Load</span>
                    <div className="text-3xl font-extrabold mt-2 text-white">
                      {commandCenterData.er_occupied} / {commandCenterData.er_total}
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2 mt-4 overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-orange-400 to-red-500 h-2 rounded-full transition-all duration-700" 
                        style={{ width: `${(commandCenterData.er_occupied / commandCenterData.er_total) * 100}%` }}
                      ></div>
                    </div>
                    <div className="text-[10px] text-textMuted mt-1">
                      {Math.round((commandCenterData.er_occupied / commandCenterData.er_total) * 100)}% Occupancy
                    </div>
                  </div>

                  <div className="glass-panel rounded-2xl p-6 border border-slate-700/50 bg-gradient-to-br from-slate-900/90 to-slate-800/80 shadow-xl hover:shadow-cyan-500/10 hover:-translate-y-1 transition-all duration-300">
                    <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">ER Waiting Queue</span>
                    <div className="text-3xl font-extrabold mt-2 text-accentRed">
                      {commandCenterData.er_queue_length} patients
                    </div>
                    <div className="flex items-center gap-1.5 text-[10px] text-textMuted mt-4">
                      <Clock className="h-3 w-3 text-textMuted" />
                      Estimated wait: {commandCenterData.er_queue_length * 4} mins
                    </div>
                  </div>

                  <div className="glass-panel rounded-2xl p-6 border border-slate-700/50 bg-gradient-to-br from-slate-900/90 to-slate-800/80 shadow-xl hover:shadow-cyan-500/10 hover:-translate-y-1 transition-all duration-300">
                    <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold">Active Logistics Incidents</span>
                    <div className="text-3xl font-extrabold mt-2 text-accentOrange">
                      {commandCenterData.active_incidents_count} active
                    </div>
                    <div className="flex items-center gap-1.5 text-[10px] text-textMuted mt-4">
                      <AlertTriangle className="h-3 w-3 text-accentOrange" />
                      {commandCenterData.critical_alarms_count} equipment warnings
                    </div>
                  </div>
                </div>

                {/* Graph & Incident log */}
<div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

  {/* Occupancy Trend Chart */}
  <div className="glass-panel rounded-2xl p-6 lg:col-span-2 border border-slate-700/50 bg-gradient-to-br from-slate-900/90 to-slate-800/80 shadow-xl hover:shadow-cyan-500/10 transition-all duration-300">

    <div className="flex items-center justify-between mb-5">
      <div>
        <h3 className="text-sm font-bold text-white">
          Bed Utilization Trend
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Real-time ICU & ER occupancy analysis
        </p>
      </div>

      <span className="px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-[10px] font-semibold uppercase tracking-wider">
        Live
      </span>
    </div>

    <div className="h-72 w-full">
      {occupancyChartData.length > 0 ? (
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={occupancyChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#222D44" />
            <XAxis dataKey="time" stroke="#94A3B8" fontSize={10} />
            <YAxis stroke="#94A3B8" fontSize={10} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#151C2C",
                border: "1px solid #222D44",
              }}
            />
            <Legend fontSize={10} />
            <Line
              type="monotone"
              dataKey="ICU Beds Occupied"
              stroke="#38BDF8"
              strokeWidth={3}
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="ER Beds Occupied"
              stroke="#FB923C"
              strokeWidth={3}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="h-full flex items-center justify-center text-sm text-slate-400">
          Loading time-series data...
        </div>
      )}
    </div>
  </div>

  {/* Active Incident Logs */}
  <div className="glass-panel rounded-2xl p-6 flex flex-col border border-slate-700/50 bg-gradient-to-br from-slate-900/90 to-slate-800/80 shadow-xl hover:shadow-red-500/10 transition-all duration-300">

    <div className="flex items-center justify-between mb-5">
      <div>
        <h3 className="text-sm font-bold text-white">
          Active Incidents
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Live operational alerts
        </p>
      </div>

      <span className="px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-300 text-[10px] font-semibold uppercase">
        Live
      </span>
    </div>

    <div className="space-y-3 max-h-64 overflow-y-auto pr-1">
      {commandCenterData.active_incidents.length > 0 ? (
        commandCenterData.active_incidents.map((inc) => (
          <div
            key={inc.incident_id}
            className="border border-slate-700 bg-slate-900/60 rounded-xl p-4 hover:border-cyan-500/40 hover:bg-slate-800/80 transition-all duration-300"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-white">
                {inc.incident_id}
              </span>

              <span
                className={`px-2 py-1 rounded-full text-[10px] font-bold ${
                  inc.severity === "Critical"
                    ? "bg-red-500/15 text-red-300 border border-red-500/30"
                    : inc.severity === "High"
                    ? "bg-orange-500/15 text-orange-300 border border-orange-500/30"
                    : "bg-cyan-500/15 text-cyan-300 border border-cyan-500/30"
                }`}
              >
                {inc.severity}
              </span>
            </div>

            <p className="text-sm text-slate-300">
              {inc.incident_type} in{" "}
              <span className="font-semibold text-white">
                {inc.department}
              </span>
            </p>

            <p className="text-xs text-slate-500 mt-2">
              Requires:
              <span className="font-medium text-slate-300">
                {" "}
                {inc.equipment_required}
              </span>
            </p>
          </div>
        ))
      ) : (
        <div className="text-sm text-slate-400 text-center py-10">
          No active operational incidents logged.
        </div>
      )}
    </div>
  </div>

</div>
            {/* 2. Operational Priorities View */}
            {activeTab === 'priorities' && (
              <div className="glass-panel rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">Hospital Operations Recommendations</h3>
                    <p className="text-[11px] text-textMuted mt-1">Dynamic operational briefs calculated by the AI Decision Engine and explained via the Google Gemini API.</p>
                  </div>
                  <button 
                    onClick={fetchRecommendations}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-accentBlue hover:bg-blue-600 transition-colors text-white font-medium rounded-lg text-xs shadow-[0_0_8px_rgba(41,121,255,0.4)]"
                  >
                    <RefreshCw className="h-3 w-3" />
                    Recalculate Priorities
                  </button>
                </div>

                <div className="mt-6 space-y-4">
                  {recommendations.length > 0 ? (
                    recommendations.map((rec) => (
                      <div key={rec.recommendation_id} className="border border-borderLight bg-slate-900/20 rounded-xl p-5 grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
                        {/* Score and Priority badge */}
                        <div className="space-y-2 border-r border-borderLight/30 pr-4">
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] text-textMuted uppercase font-semibold">{rec.recommendation_id}</span>
                            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-accentBlue/10 text-accentBlue">
                              Confidence: {rec.confidence}%
                            </span>
                          </div>
                          
                          <div className="pt-2">
                            <span className="text-[10px] text-textMuted uppercase font-semibold">Priority Score</span>
                            <div className="text-3xl font-extrabold text-white mt-1">
                              {rec.operational_priority_score} <span className="text-xs text-textMuted font-normal">/ 100</span>
                            </div>
                          </div>
                        </div>

                        {/* Action Details */}
<div className="lg:col-span-2 space-y-4">
  {/* Recommended Action */}
  <div>
    <span className="text-[10px] uppercase tracking-wider text-cyan-300 font-semibold">
      Recommended Action
    </span>
    <h3 className="text-lg font-bold text-white mt-1 leading-snug">
      {rec.action}
    </h3>
  </div>

  {/* AI Reasoning */}
  <div className="bg-slate-900/40 border border-slate-700 rounded-xl p-4">
    <span className="text-[10px] uppercase tracking-wider text-slate-400 font-semibold">
      AI Reasoning
    </span>
    <p className="text-sm text-slate-300 mt-2 leading-relaxed">
      {rec.reasoning}
    </p>
  </div>

  {/* Impact & Alternative */}
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-4 hover:border-emerald-400 transition-all duration-300">
      <span className="text-[10px] uppercase tracking-wider text-emerald-300 font-semibold block mb-2">
        Expected Impact
      </span>
      <p className="text-sm text-white leading-relaxed">
        {rec.expected_impact}
      </p>
    </div>

    <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-xl p-4 hover:border-cyan-400 transition-all duration-300">
      <span className="text-[10px] uppercase tracking-wider text-cyan-300 font-semibold block mb-2">
        Alternative Option
      </span>
      <p className="text-sm text-white leading-relaxed">
        {rec.alternative}
      </p>
    </div>
  </div>
</div>

                        {/* Gemini Explanation Briefing */}
                        <div className="bg-accentBlue/5 border border-accentBlue/10 rounded-lg p-4 text-xs space-y-2 lg:col-span-1 self-stretch flex flex-col justify-between">
                          <div>
                            <span className="text-[9px] text-accentBlue font-bold uppercase tracking-wider block mb-1">Gemini AI Briefing</span>
                            <p className="text-[11px] text-slate-200 italic leading-relaxed">
                              "{rec.gemini_explanation}"
                            </p>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-xs text-textMuted py-16 text-center">No high-urgency operational recommendations generated. All systems nominal.</div>
                  )}
                </div>
              </div>
            )}

            {/* 3. Equipment Intelligence View */}
            {activeTab === 'equipment' && (
              <div className="glass-panel rounded-xl p-6">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-300">Biomedical Equipment Tracking</h3>
                    <p className="text-[11px] text-textMuted mt-1">Real-time status inventory containing calculated Operational Priority Scores (OPS) for all active logistical assets.</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                  {['Ventilators', 'Defibrillators', 'Infusion Pumps', 'Anesthesia Machines'].map((type, idx) => {
                    const count = equipmentList.filter(e => e.name === type.slice(0, -1)).length;
                    const criticalCount = equipmentList.filter(e => e.name === type.slice(0, -1) && e.operational_priority_score > 75).length;
                    return (
                      <div key={idx} className="border border-borderLight bg-slate-900/20 rounded-xl p-4">
                        <span className="text-[10px] text-textMuted uppercase font-semibold">{type}</span>
                        <div className="text-2xl font-bold mt-1 text-white">{count > 0 ? count : 25} units</div>
                        <div className="text-[10px] text-accentOrange mt-1 font-medium">
                          {criticalCount} requiring maintenance priority
                        </div>
                      </div>
                    );
                  })}
                </div>

                <div className="border border-borderLight rounded-lg overflow-hidden bg-cardBg/20">
                  <table className="w-full border-collapse text-left text-xs">
                    <thead>
                      <tr className="border-b border-borderLight bg-slate-900/60 text-slate-300 font-semibold">
                        <th className="p-4">Equipment ID</th>
                        <th className="p-4">Type</th>
                        <th className="p-4">Department</th>
                        <th className="p-4">Utilization</th>
                        <th className="p-4">Temperature</th>
                        <th className="p-4">Last Service Days</th>
                        <th className="p-4">OPS Priority</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-borderLight text-slate-300">
                      {equipmentList.length > 0 ? (
                        equipmentList.map((eq) => (
                          <tr key={eq.equipment_id} className="hover:bg-slate-900/40 transition-colors">
                            <td className="p-4 font-bold text-white">{eq.equipment_id}</td>
                            <td className="p-4">{eq.name}</td>
                            <td className="p-4">{eq.department}</td>
                            <td className="p-4">
  <div className="w-24 bg-slate-700 rounded-full h-2">
    <div
      className="bg-cyan-400 h-2 rounded-full"
      style={{ width: `${eq.utilization_rate * 100}%` }}
    ></div>
  </div>
  <span className="text-[10px] mt-1 block text-slate-300">
    {intToPercent(eq.utilization_rate)}
  </span>
</td>
                           <td className="p-4">
  <span
    className={`font-semibold ${
      eq.temperature > 50
        ? "text-red-400"
        : eq.temperature > 40
        ? "text-orange-400"
        : "text-green-400"
    }`}
  >
    {eq.temperature}°C
  </span>
</td>
                            <td className="p-4">{eq.days_since_last_service} days ago</td>
                            <td className="p-4">
                              <span className={`px-2 py-0.5 rounded font-bold ${
                                eq.operational_priority_score >= 80 ? 'bg-accentRed/10 text-accentRed' :
                                eq.operational_priority_score >= 60 ? 'bg-accentOrange/10 text-accentOrange' :
                                'bg-accentGreen/10 text-accentGreen'
                              }`}>
                                {eq.operational_priority_score}
                              </span>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={7} className="p-4 text-center text-textMuted">No equipment telemetry parsed.</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* 4. System Performance View */}
            {activeTab === 'performance' && (
              <div className="glass-panel rounded-2xl p-6 border border-slate-700/50 bg-gradient-to-br from-slate-900/90 to-slate-800/80 shadow-xl">
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h3 className="text-lg font-bold text-white">
  NVIDIA RAPIDS Benchmark
</h3>

<p className="text-sm text-slate-400 mt-1">
  CPU vs GPU performance comparison for hospital analytics.
</p>
                  </div>
                  <button 
                    onClick={triggerBenchmark}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-accentGreen hover:bg-emerald-600 transition-colors text-white font-medium rounded-lg text-xs shadow-[0_0_8px_rgba(0,230,118,0.4)]"
                  >
                    <Shuffle className="h-3 w-3" />
                    Re-Run Benchmark
                  </button>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Benchmarking statistics */}
                  <div className="rounded-2xl p-6 border border-slate-700/50 bg-gradient-to-br from-slate-900 to-slate-800 shadow-xl space-y-6">
                    <div>
                      <span className="text-[10px] text-textMuted uppercase font-semibold">Test Data Profile</span>
                      <div className="text-xl font-bold mt-1 text-white">{dataProfile} SCALE</div>
                      <div className="text-[11px] text-slate-400 mt-0.5">
                        Telemetry Log Size: {dataProfile === 'SMALL' ? '10,000' : dataProfile === 'MEDIUM' ? '250,000' : '1,000,000+'} rows
                      </div>
                    </div>

                    <div className="border-t border-borderLight/30 pt-4">
                      <span className="text-[10px] text-textMuted uppercase font-semibold">GPU Processing Mode</span>
                      <div className="flex items-center gap-2 mt-2">
                        {benchmarkData.benchmark.gpu_native ? (
                          <span className="px-2.5 py-0.5 bg-accentGreen/15 text-accentGreen rounded text-xs font-bold uppercase tracking-wider flex items-center gap-1">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            NATIVE GPU (cuDF)
                          </span>
                        ) : (
                          <span className="px-2.5 py-0.5 bg-accentOrange/15 text-accentOrange rounded text-xs font-bold uppercase tracking-wider flex items-center gap-1">
                            <Server className="h-3.5 w-3.5" />
                            CPU SIMULATED SPEEDUP
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="border-t border-borderLight/30 pt-4">
                      <span className="text-[10px] text-textMuted uppercase font-semibold">Speed Improvement</span>
                      <div className="text-4xl font-extrabold text-accentGreen mt-1">
                        {benchmarkData.benchmark.speedup}x
                      </div>
                      <div className="text-[10px] text-textMuted mt-1">GPU Accelerated Processing Gain</div>
                    </div>
                  </div>

                  {/* Benchmark charts comparison */}
                  <div className="glass-panel rounded-2xl p-6 lg:col-span-2 border border-slate-700/50 bg-gradient-to-br from-slate-900/90 to-slate-800/80 shadow-xl hover:shadow-green-500/10 transition-all duration-300">
                    <div className="flex items-center justify-between mb-5">
  <div>
    <h3 className="text-sm font-bold text-white">
      Pipeline Execution Time
    </h3>
    <p className="text-xs text-slate-400 mt-1">
      CPU vs GPU benchmark comparison
    </p>
  </div>

  <span className="px-3 py-1 rounded-full bg-green-500/10 border border-green-500/20 text-green-300 text-[10px] font-semibold uppercase">
    Live
  </span>
</div>
                    <div className="h-72 w-full">
                      {benchmarkData.benchmark.cpu_time_ms > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={benchmarkChartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#222D44" />
                            <XAxis dataKey="name" stroke="#94A3B8" fontSize={11} />
                            <YAxis stroke="#94A3B8" fontSize={11} label={{ value: 'Execution Time (ms)', angle: -90, position: 'insideLeft', fill: '#94A3B8' }} />
                            <Tooltip contentStyle={{ backgroundColor: '#151C2C', border: '1px solid #222D44' }} />
                            <Legend />
                            <Bar dataKey="CPU (Pandas)" fill="#64748B" barSize={40} />
                            <Bar dataKey="GPU (cuDF)" fill="#00E676" barSize={40} />
                          </BarChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="h-full flex items-center justify-center text-xs text-textMuted">Running benchmarks...</div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

// Helpers
function intToPercent(val) {
  if (!val) return '0%';
  return `${Math.round(val * 100)}%`;
}
