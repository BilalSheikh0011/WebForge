import React, { useState, useEffect } from "react";
import {
  LayoutDashboard,
  Hammer,
  Play,
  CheckCircle2,
  AlertCircle,
  Bug,
  Sparkles,
  GitBranch,
  FileCode,
  FileSpreadsheet,
  FileText,
  LogOut,
  Plus,
  Trash2,
  RefreshCw,
  Copy,
  Check,
  ArrowRight,
  ShieldCheck,
  Zap,
  Terminal,
  Layers,
  Activity,
  UserCheck,
  LogIn,
  ChevronRight,
  Lock,
  Mail,
  User,
  Sliders,
  Globe,
  Database,
  Cpu,
  Server,
  Eye,
  CheckCircle,
  XCircle,
  HelpCircle,
  Wrench,
  Video,
  UserPlus
} from "lucide-react";

const API_BASE = "http://localhost:8000";

const ACTION_TYPES = [
  "navigate", "click", "dblclick", "fill", "clear", "select",
  "hover", "scroll", "press", "assert_text_equals", "assert_text_contains",
  "assert_visible", "assert_hidden", "assert_url_equals", "assert_title", "wait"
];
const SELECTOR_TYPES = ["", "id", "css", "xpath", "name", "link", "aria"];

const DEFAULT_STEPS = [
  { order: 1, action: "navigate", selector_type: "", selector: "", value: "https://leatherlaneatelier.store", expected: "" },
  { order: 2, action: "wait", selector_type: "", selector: "", value: "2000", expected: "" },
  { order: 3, action: "assert_visible", selector_type: "css", selector: "body", value: "", expected: "" }
];

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("wf_token") || "");
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("wf_user");
    return saved ? JSON.parse(saved) : null;
  });

  // UI Navigation
  const [activeTab, setActiveTab] = useState("dashboard");
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isRegister, setIsRegister] = useState(false);
  const [copiedScript, setCopiedScript] = useState(false);
  const [hoveredRun, setHoveredRun] = useState(null);

  // Authentication Fields
  const [authEmail, setAuthEmail] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authName, setAuthName] = useState("");
  const [authError, setAuthError] = useState("");

  // User-Scoped Workspace States
  const [defects, setDefects] = useState([]);
  const [testCode, setTestCode] = useState("TC-001");
  const [testName, setTestName] = useState("New Storefront Functional Test");
  const [priority, setPriority] = useState("Critical");
  const [testType, setTestType] = useState("Functional");
  const [targetUrl, setTargetUrl] = useState("https://leatherlaneatelier.store");
  const [steps, setSteps] = useState(DEFAULT_STEPS);
  const [runResults, setRunResults] = useState(null);
  const [trendRuns, setTrendRuns] = useState([]);

  // Synthetic Generator State
  const [syntheticPayload, setSyntheticPayload] = useState("");
  const [selectedGenType, setSelectedGenType] = useState("boundary_string");

  // Execution & UI State
  const [isRunning, setIsRunning] = useState(false);
  const [selectedProof, setSelectedProof] = useState(null);
  const [previewScript, setPreviewScript] = useState("");
  const [activePlaybackIndex, setActivePlaybackIndex] = useState(0);

  // AI DOM Analyzer State
  const [aiUrl, setAiUrl] = useState("https://leatherlaneatelier.store");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState([]);

  // Load user-specific workspace data
  useEffect(() => {
    if (token && user?.email) {
      localStorage.setItem("wf_token", token);
      localStorage.setItem("wf_user", JSON.stringify(user));

      const userWorkspaceKey = `wf_workspace_${user.email.toLowerCase()}`;
      const savedWorkspace = localStorage.getItem(userWorkspaceKey);

      if (savedWorkspace) {
        try {
          const parsed = JSON.parse(savedWorkspace);
          setTestCode(parsed.testCode || "TC-001");
          setTestName(parsed.testName || "New Storefront Functional Test");
          setPriority(parsed.priority || "Critical");
          setTestType(parsed.testType || "Functional");
          setTargetUrl(parsed.targetUrl || "https://leatherlaneatelier.store");
          setSteps(parsed.steps || DEFAULT_STEPS);
          setRunResults(parsed.runResults || null);
          setTrendRuns(parsed.trendRuns || []);
          setDefects(parsed.defects || []);
        } catch (e) {
          resetUserWorkspace();
        }
      } else {
        resetUserWorkspace();
      }
    } else {
      localStorage.removeItem("wf_token");
      localStorage.removeItem("wf_user");
    }
  }, [token, user?.email]);

  const resetUserWorkspace = () => {
    setTestCode("TC-001");
    setTestName("New Storefront Functional Test");
    setPriority("Critical");
    setTestType("Functional");
    setTargetUrl("https://leatherlaneatelier.store");
    setSteps(DEFAULT_STEPS);
    setRunResults(null);
    setTrendRuns([]);
    setDefects([]);
  };

  // Persist workspace changes per user
  useEffect(() => {
    if (user?.email) {
      const userWorkspaceKey = `wf_workspace_${user.email.toLowerCase()}`;
      const workspaceData = {
        testCode,
        testName,
        priority,
        testType,
        targetUrl,
        steps,
        runResults,
        trendRuns,
        defects
      };
      localStorage.setItem(userWorkspaceKey, JSON.stringify(workspaceData));
    }
  }, [user?.email, testCode, testName, priority, testType, targetUrl, steps, runResults, trendRuns, defects]);

  useEffect(() => {
    if (runResults && runResults.step_results && runResults.step_results.length > 0) {
      setActivePlaybackIndex(0);
    }
  }, [runResults]);

  // Dynamic Playwright Preview
  useEffect(() => {
    let script = `# Generated by WebForge Automation Pipeline\nfrom playwright.sync_api import sync_playwright\n\n`;
    script += `def run():\n    with sync_playwright() as pw:\n        browser = pw.chromium.launch(headless=True)\n`;
    script += `        context = browser.new_context(viewport={'width': 1366, 'height': 768})\n        page = context.new_page()\n`;

    steps.forEach((s) => {
      if (s.action === "navigate") script += `        page.goto("${s.value}")\n`;
      else if (s.action === "fill") script += `        page.locator("${s.selector}").fill("${s.value}")\n`;
      else if (s.action === "click") script += `        page.locator("${s.selector}").click()\n`;
      else if (s.action === "wait") script += `        page.wait_for_timeout(${parseInt(s.value) || 2000})\n`;
      else if (s.action.startsWith("assert_")) script += `        # Validate ${s.action} on ${s.selector || "URL"}\n`;
    });
    script += `        browser.close()\n\nif __name__ == '__main__':\n    run()`;
    setPreviewScript(script);
  }, [steps, testName]);

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthError("");
    const endpoint = isRegister ? "/auth/register" : "/auth/login";

    const payload = isRegister
      ? { email: authEmail, password: authPassword, name: authName }
      : { email: authEmail, password: authPassword };

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || (isRegister ? "Registration failed" : "Sign in failed"));

      setToken(data.access_token);
      setUser(data.user || { name: authName || "Tester", email: authEmail, role: "Tester" });
      setShowAuthModal(false);
      setAuthPassword("");
    } catch (err) {
      setAuthError(err.message);
    }
  };

  const handleSignOut = () => {
    setToken("");
    setUser(null);
    resetUserWorkspace();
  };

  const addStep = () => {
    setSteps([...steps, { order: steps.length + 1, action: "click", selector_type: "css", selector: "", value: "", expected: "" }]);
  };

  const updateStep = (index, field, val) => {
    const updated = [...steps];
    updated[index][field] = val;
    setSteps(updated);
  };

  const deleteStep = (index) => {
    setSteps(steps.filter((_, i) => i !== index).map((s, idx) => ({ ...s, order: idx + 1 })));
  };

  const fetchSyntheticPayload = async () => {
    try {
      const res = await fetch(`${API_BASE}/data-generator/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payload_type: selectedGenType, length: 255 })
      });
      const data = await res.json();
      setSyntheticPayload(data.payload || "");
    } catch (err) {
      alert("Data generator error: " + err.message);
    }
  };

  const runTest = async () => {
    setIsRunning(true);
    setActiveTab("results");

    const payload = {
      test_case_id: 1,
      base_url: targetUrl,
      stop_on_fail: true,
      steps: steps
    };

    try {
      const res = await fetch(`${API_BASE}/runs/execute`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Execution failed");
      setRunResults(data);

      const passRate = data.overall_status === "PASS" ? 100 : (data.overall_status === "FLAKY" ? 90 : 75);
      const newRunEntry = {
        id: trendRuns.length + 1,
        val: passRate,
        status: data.overall_status,
        ms: `${data.duration_ms || 1800}ms`
      };
      setTrendRuns(prev => [...prev.slice(-9), newRunEntry]);
    } catch (err) {
      alert("Execution error: " + err.message);
    } finally {
      setIsRunning(false);
    }
  };

  // Resilient, non-hanging AI DOM scan with URL synchronization
  const runAiAnalysis = async () => {
    setAiLoading(true);
    setAiSuggestions([]);

    const cleanUrl = aiUrl.trim() || "https://leatherlaneatelier.store";
    // Sync the active workspace target URL so the Dashboard header updates
    setTargetUrl(cleanUrl);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);

    try {
      const res = await fetch(`${API_BASE}/ai/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: cleanUrl }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (!res.ok) {
        throw new Error(`Server returned status ${res.status}`);
      }
      const data = await res.json();
      setAiSuggestions(data.suggestions || []);
    } catch (err) {
      if (err.name === "AbortError") {
        alert("AI scan request timed out. Please ensure your backend is running on port 8000.");
      } else {
        alert("AI scan error: " + err.message);
      }
    } finally {
      setAiLoading(false);
    }
  };

  const applyAiSuggestion = (sug) => {
    setTestName(sug.title);
    setPriority(sug.priority || "High");
    setTestType(sug.type || "Functional");
    // Ensure the active workspace target URL matches the scanned website
    setTargetUrl(aiUrl.trim() || "https://leatherlaneatelier.store");
    if (sug.steps && sug.steps.length > 0) setSteps(sug.steps);
    setActiveTab("builder");
  };

  const logDefectFromStep = async (step) => {
    const formattedCode = `DEF-${String(defects.length + 1).padStart(3, "0")}`;

    const newDefectItem = {
      code: formattedCode,
      title: `Step ${step.index} Failed: ${step.action}`,
      description: step.error || "Automated assertion discrepancy detected",
      severity: "Major",
      status: "Open",
      screenshot_b64: step.screenshot_b64
    };

    try {
      await fetch(`${API_BASE}/defects`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: newDefectItem.title,
          description: newDefectItem.description,
          severity: "Major",
          test_case_id: 1,
          step_index: step.index,
          screenshot_b64: step.screenshot_b64,
          user_id: user?.id
        })
      });
    } catch (e) {
      // Local fallback persists state cleanly per user
    }

    setDefects(prev => [...prev, newDefectItem]);
    alert("Defect logged into tracker!");
  };

  // ==========================================
  // UNAUTHENTICATED LANDING VIEW
  // ==========================================
  if (!token) {
    return (
      <div className="min-h-screen bg-[#070b13] text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-slate-950">
        <header className="h-20 border-b border-slate-800/60 bg-[#070b13]/80 backdrop-blur-xl px-8 flex items-center justify-between sticky top-0 z-40">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-400 to-cyan-500 flex items-center justify-center font-black text-slate-950 text-base shadow-lg shadow-emerald-500/20">
              WF
            </div>
            <div>
              <span className="font-extrabold tracking-tight text-white text-xl">WebForge</span>
              <span className="text-[10px] text-emerald-400 font-mono block -mt-1 tracking-wider uppercase font-semibold">
                Autonomous QA Platform
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => {
                setIsRegister(false);
                setAuthError("");
                setShowAuthModal(true);
              }}
              className="text-xs font-semibold text-slate-300 hover:text-white transition px-4 py-2 cursor-pointer flex items-center gap-1.5"
            >
              <LogIn size={14} className="text-emerald-400" /> Sign In
            </button>
            <button
              onClick={() => {
                setIsRegister(true);
                setAuthError("");
                setShowAuthModal(true);
              }}
              className="text-xs font-bold bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 text-slate-950 px-5 py-2.5 rounded-xl transition shadow-lg shadow-emerald-500/20 cursor-pointer flex items-center gap-1.5"
            >
              <UserPlus size={14} /> Sign Up
            </button>
          </div>
        </header>

        <section className="pt-24 pb-20 px-6 max-w-4xl mx-auto text-center flex-1 flex flex-col justify-center items-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-emerald-400 text-xs font-mono mb-6">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" /> Automated Functional Web Testing Platform
          </div>
          <h1 className="text-4xl md:text-6xl font-black text-white leading-tight">
            High-Precision Web Test Automation
          </h1>
          <p className="mt-4 text-base text-slate-400 max-w-xl">
            Isolated user workspaces, self-healing Playwright execution, and real-time regression telemetry.
          </p>

          <div className="mt-8 flex items-center gap-4">
            <button
              onClick={() => {
                setIsRegister(false);
                setAuthError("");
                setShowAuthModal(true);
              }}
              className="px-8 py-3.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-xl text-sm transition shadow-xl shadow-emerald-500/20 flex items-center gap-2 cursor-pointer"
            >
              Sign In to Console <ArrowRight size={16} />
            </button>
            <button
              onClick={() => {
                setIsRegister(true);
                setAuthError("");
                setShowAuthModal(true);
              }}
              className="px-7 py-3.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 font-semibold rounded-xl text-sm transition cursor-pointer flex items-center gap-2"
            >
              Create New Tester Account
            </button>
          </div>
        </section>

        {showAuthModal && (
          <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
            <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative">
              <button
                onClick={() => setShowAuthModal(false)}
                className="absolute top-5 right-5 text-slate-400 hover:text-white cursor-pointer font-bold"
              >
                ✕
              </button>

              <div className="flex items-center gap-2 p-1 bg-slate-950 rounded-xl border border-slate-800 mb-6">
                <button
                  type="button"
                  onClick={() => { setIsRegister(false); setAuthError(""); }}
                  className={`flex-1 py-2 text-xs font-bold rounded-lg transition cursor-pointer flex items-center justify-center gap-1.5 ${
                    !isRegister ? "bg-emerald-500 text-slate-950 shadow-md" : "text-slate-400 hover:text-white"
                  }`}
                >
                  <LogIn size={13} /> Sign In
                </button>
                <button
                  type="button"
                  onClick={() => { setIsRegister(true); setAuthError(""); }}
                  className={`flex-1 py-2 text-xs font-bold rounded-lg transition cursor-pointer flex items-center justify-center gap-1.5 ${
                    isRegister ? "bg-emerald-500 text-slate-950 shadow-md" : "text-slate-400 hover:text-white"
                  }`}
                >
                  <UserPlus size={13} /> Sign Up
                </button>
              </div>

              <div>
                <h3 className="text-lg font-bold text-white">
                  {isRegister ? "Create Tester Account" : "Sign In to Workspace"}
                </h3>
                <p className="text-xs text-slate-400 mt-0.5 mb-4">
                  {isRegister
                    ? "Register a fresh workspace as a QA Tester"
                    : "Enter your credentials to load your personal workspace"}
                </p>
              </div>

              {authError && (
                <div className="p-3 mb-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-400 flex items-center gap-2">
                  <AlertCircle size={14} className="shrink-0" /> {authError}
                </div>
              )}

              <form onSubmit={handleAuth} className="space-y-4">
                {isRegister && (
                  <div>
                    <label className="text-xs text-slate-400 font-medium block mb-1">Full Name</label>
                    <div className="relative">
                      <User size={14} className="absolute left-3 top-3 text-slate-500" />
                      <input
                        type="text"
                        value={authName}
                        onChange={(e) => setAuthName(e.target.value)}
                        placeholder="e.g. Bilal Arif"
                        required
                        className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                      />
                    </div>
                  </div>
                )}

                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Email Address</label>
                  <div className="relative">
                    <Mail size={14} className="absolute left-3 top-3 text-slate-500" />
                    <input
                      type="email"
                      value={authEmail}
                      onChange={(e) => setAuthEmail(e.target.value)}
                      placeholder="e.g. user@webforge.io"
                      required
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="text-xs text-slate-400 font-medium block mb-1">Password</label>
                  <div className="relative">
                    <Lock size={14} className="absolute left-3 top-3 text-slate-500" />
                    <input
                      type="password"
                      value={authPassword}
                      onChange={(e) => setAuthPassword(e.target.value)}
                      placeholder="Enter password"
                      required
                      className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2.5 text-xs text-white focus:border-emerald-500 focus:outline-none"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 text-slate-950 font-bold rounded-xl text-xs transition cursor-pointer shadow-lg shadow-emerald-500/20"
                >
                  {isRegister ? "Register New Tester Account" : "Sign In to WebForge"}
                </button>
              </form>

              <div className="mt-5 text-center">
                <button
                  type="button"
                  onClick={() => {
                    setIsRegister(!isRegister);
                    setAuthError("");
                  }}
                  className="text-xs text-slate-400 hover:text-emerald-400 cursor-pointer transition font-medium"
                >
                  {isRegister ? "Already registered? Sign In" : "Need an account? Sign Up as Tester"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  const currentPlaybackStep = (runResults && runResults.step_results && runResults.step_results[activePlaybackIndex]) || null;
  const failedSteps = runResults ? runResults.step_results.filter(s => s.status === "FAIL") : [];

  const displayHealth = trendRuns.length > 0
    ? `${Math.round(trendRuns.filter(r => r.status === "PASS").length / trendRuns.length * 100)}%`
    : (runResults ? (runResults.overall_status === "PASS" ? "100%" : "0%") : "100%");

  return (
    <div className="min-h-screen bg-[#070b13] text-slate-100 flex flex-col font-sans selection:bg-emerald-500 selection:text-slate-950">
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[260px] bg-emerald-500/5 blur-[120px] pointer-events-none -z-10" />

      {/* Modern Command Bar */}
      <header className="h-16 border-b border-slate-800/80 bg-[#090e1b]/80 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-30 shadow-md">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center font-black text-slate-950 text-sm shadow-md shadow-emerald-500/20 ring-1 ring-white/10">
              WF
            </div>
            <span className="font-extrabold tracking-tight text-white text-base">WebForge</span>
          </div>

          <nav className="flex items-center gap-1 bg-slate-950/90 border border-slate-800/90 p-1 rounded-xl">
            <button
              onClick={() => setActiveTab("dashboard")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-2 ${
                activeTab === "dashboard"
                  ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <LayoutDashboard size={13} /> Dashboard
            </button>
            <button
              onClick={() => setActiveTab("builder")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-2 ${
                activeTab === "builder"
                  ? "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Hammer size={13} /> Test Builder
            </button>
            <button
              onClick={() => setActiveTab("results")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-2 ${
                activeTab === "results"
                  ? "bg-teal-500/15 text-teal-400 border border-teal-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Play size={13} /> Results
            </button>
            <button
              onClick={() => setActiveTab("ai")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-2 ${
                activeTab === "ai"
                  ? "bg-purple-500/15 text-purple-400 border border-purple-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Sparkles size={13} /> AI DOM Analyzer
            </button>
            <button
              onClick={() => setActiveTab("defects")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-2 ${
                activeTab === "defects"
                  ? "bg-rose-500/15 text-rose-400 border border-rose-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <Bug size={13} /> Defects
              {defects.length > 0 && (
                <span className="w-4 h-4 rounded-full bg-rose-500/20 text-rose-300 text-[10px] flex items-center justify-center font-mono font-bold">
                  {defects.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab("cicd")}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition cursor-pointer flex items-center gap-2 ${
                activeTab === "cicd"
                  ? "bg-amber-500/15 text-amber-400 border border-amber-500/30 shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              <GitBranch size={13} /> CI/CD Pipeline
            </button>
          </nav>
        </div>

        {/* User Badge */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-slate-800/80">
            <div className="w-7 h-7 rounded-lg bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-xs font-bold text-emerald-400 font-mono">
              {user?.name?.slice(0, 2).toUpperCase() || "TS"}
            </div>
            <div className="text-left">
              <div className="text-xs font-bold text-slate-200 leading-tight">{user?.name || "Tester"}</div>
              <div className="text-[10px] text-emerald-400 uppercase font-mono font-bold tracking-wider leading-none mt-0.5">
                Tester
              </div>
            </div>
          </div>
          <button
            onClick={handleSignOut}
            className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-900 rounded-lg transition cursor-pointer"
            title="Sign Out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </header>

      {/* Main Workspace Area */}
      <main className="flex-1 p-6 max-w-7xl mx-auto w-full space-y-6">

        {/* TAB 1: DASHBOARD */}
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            <div className="relative overflow-hidden bg-gradient-to-r from-slate-900/90 via-[#0e1628] to-slate-900/90 border border-slate-800/90 rounded-2xl p-5 shadow-xl flex items-center justify-between">
              <div className="flex items-center gap-4 z-10">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/25 flex items-center justify-center text-emerald-400 shadow-inner">
                  <Activity size={22} className="animate-pulse" />
                </div>
                <div>
                  <div className="flex items-center gap-2.5">
                    <h2 className="text-base font-bold text-white tracking-tight">
                      {user?.name ? `${user.name}'s QA Workspace` : "Quality Assurance Workspace"}
                    </h2>
                    <span className="flex items-center gap-1.5 text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/25 px-2 py-0.5 rounded-full font-mono font-bold">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" /> ACTIVE
                    </span>
                  </div>
                  <div className="flex items-center gap-3 text-xs text-slate-400 mt-1 font-mono">
                    <span className="flex items-center gap-1 text-slate-300">
                      <Globe size={12} className="text-cyan-400" /> {targetUrl}
                    </span>
                    <span className="text-slate-600">•</span>
                    <span className="text-slate-400 flex items-center gap-1">
                      <Cpu size={12} className="text-emerald-400" /> Headless Chromium (1366×768)
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3 z-10">
                <button
                  onClick={runTest}
                  disabled={isRunning}
                  className="px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 font-bold rounded-xl text-xs transition shadow-lg shadow-emerald-500/20 flex items-center gap-2 cursor-pointer disabled:opacity-50"
                >
                  {isRunning ? <RefreshCw size={13} className="animate-spin" /> : <Play size={13} fill="currentColor" />} 
                  Quick Execute Test
                </button>
              </div>
            </div>

            {/* KPI Stat Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="relative overflow-hidden bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 shadow-lg hover:border-emerald-500/40 transition group">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold">
                    Test Suite Health
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
                    <ShieldCheck size={16} />
                  </div>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-black text-emerald-400 font-mono tracking-tight">{displayHealth}</span>
                  <span className="text-[11px] text-emerald-500 font-bold font-mono">PASS RATE</span>
                </div>
                <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>{trendRuns.length} user executions</span>
                  <span className="text-emerald-400 font-bold">Workspace Scoped</span>
                </div>
              </div>

              <div className="relative overflow-hidden bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 shadow-lg hover:border-rose-500/40 transition group">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold">
                    Open Defects
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-rose-500/10 text-rose-400 flex items-center justify-center border border-rose-500/20">
                    <Bug size={16} />
                  </div>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-black text-rose-400 font-mono tracking-tight">{defects.length}</span>
                  <span className="text-xs text-rose-400 font-semibold">Tracked</span>
                </div>
                <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>Assigned to Tester</span>
                  <span className="text-rose-400 font-bold">{user?.name || "Tester"}</span>
                </div>
              </div>

              <div className="relative overflow-hidden bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 shadow-lg hover:border-cyan-500/40 transition group">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold">
                    Testing Scope
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center border border-cyan-500/20">
                    <Sliders size={16} />
                  </div>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-3xl font-black text-cyan-400 font-mono tracking-tight">6</span>
                  <span className="text-xs text-cyan-300 font-semibold">Methodologies</span>
                </div>
                <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                  <span>ISTQB Compliant</span>
                  <span className="text-cyan-400 font-bold">Functional & Boundary</span>
                </div>
              </div>

              <div className="relative overflow-hidden bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 shadow-lg hover:border-purple-500/40 transition group">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold">
                    Environment
                  </span>
                  <div className="w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400 flex items-center justify-center border border-purple-500/20">
                    <Globe size={16} />
                  </div>
                </div>
                <div className="mt-3 flex items-baseline gap-2">
                  <span className="text-2xl font-black text-purple-400 font-mono tracking-tight">Production</span>
                </div>
                <div className="mt-3 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono truncate">
                  <span className="truncate">{targetUrl}</span>
                  <span className="text-purple-400 font-bold shrink-0">Live</span>
                </div>
              </div>
            </div>

            {/* Regression Telemetry Chart */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-bold text-white tracking-tight">Workspace Regression History</h3>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded font-mono">
                      {trendRuns.length} Executions
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Continuous evaluation of regression passes recorded in your personal workspace.
                  </p>
                </div>
              </div>

              <div className="relative pt-6 pb-2 px-6 bg-slate-950/80 border border-slate-800/80 rounded-xl overflow-hidden min-h-[160px] flex items-end">
                {trendRuns.length === 0 ? (
                  <div className="w-full text-center py-10 text-slate-500 font-mono text-xs">
                    No execution runs recorded yet for this user. Run your first test in the Test Builder tab!
                  </div>
                ) : (
                  <div className="flex items-end justify-start gap-4 h-36 w-full">
                    {trendRuns.map((run) => (
                      <div
                        key={run.id}
                        onMouseEnter={() => setHoveredRun(run)}
                        onMouseLeave={() => setHoveredRun(null)}
                        className="flex flex-col items-center gap-2 h-full justify-end group cursor-pointer relative"
                      >
                        {hoveredRun?.id === run.id && (
                          <div className="absolute -top-10 bg-slate-900 border border-slate-700 text-slate-200 px-2 py-1 rounded-md text-[10px] font-mono shadow-xl z-20 whitespace-nowrap">
                            Run #{run.id}: <span className="text-emerald-400">{run.val}%</span> ({run.ms})
                          </div>
                        )}
                        <span className="text-[10px] font-mono text-slate-400">{run.val}%</span>
                        <div className="w-10 bg-slate-900 rounded-t-md overflow-hidden h-full flex items-end p-0.5 border border-slate-800">
                          <div
                            style={{ height: `${run.val}%` }}
                            className={`w-full rounded-t-sm transition-all duration-500 ${
                              run.status === "PASS"
                                ? "bg-gradient-to-t from-emerald-600 to-emerald-400"
                                : "bg-gradient-to-t from-rose-600 to-rose-400"
                            }`}
                          />
                        </div>
                        <span className="text-[10px] font-mono text-slate-500">R#{run.id}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: TEST BUILDER */}
        {activeTab === "builder" && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 space-y-6">
              <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <span className="bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 px-2.5 py-1 rounded text-xs font-mono font-bold">
                      {testCode}
                    </span>
                    <input
                      type="text"
                      value={testName}
                      onChange={(e) => setTestName(e.target.value)}
                      className="bg-transparent font-bold text-white text-base focus:outline-none border-b border-transparent focus:border-cyan-500 w-96"
                    />
                  </div>
                  <button
                    onClick={runTest}
                    disabled={isRunning}
                    className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-400 hover:from-emerald-400 hover:to-teal-300 text-slate-950 rounded-xl text-xs font-bold transition shadow-lg shadow-emerald-500/20 cursor-pointer"
                  >
                    {isRunning ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} fill="currentColor" />} Run Test
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-4 text-xs">
                  <div>
                    <label className="text-slate-400 block mb-1">Target Base URL</label>
                    <input
                      type="text"
                      value={targetUrl}
                      onChange={(e) => setTargetUrl(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 font-mono"
                    />
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Priority</label>
                    <select
                      value={priority}
                      onChange={(e) => setPriority(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200"
                    >
                      <option value="Critical">Critical</option>
                      <option value="High">High</option>
                      <option value="Medium">Medium</option>
                      <option value="Low">Low</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-slate-400 block mb-1">Test Type</label>
                    <select
                      value={testType}
                      onChange={(e) => setTestType(e.target.value)}
                      className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200"
                    >
                      <option value="Functional">Functional</option>
                      <option value="Smoke">Smoke</option>
                      <option value="Regression">Regression</option>
                      <option value="Boundary">Boundary Value</option>
                      <option value="Negative">Negative</option>
                      <option value="Integration">Integration</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Synthetic Boundary Generator */}
              <div className="p-4 bg-slate-900/70 border border-slate-800/80 rounded-2xl space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider font-mono">
                      Synthetic Boundary Generator
                    </span>
                    <span className="text-[10px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700">
                      Module 7.5
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <select 
                      value={selectedGenType} 
                      onChange={(e) => setSelectedGenType(e.target.value)}
                      className="px-2.5 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white"
                    >
                      <option value="boundary_string">255-Char Boundary String</option>
                      <option value="email_boundary">254-Char Max Email</option>
                      <option value="sql_injection">SQL Injection Attack Payload</option>
                      <option value="xss">XSS Script Injection Payload</option>
                    </select>
                    <button 
                      type="button"
                      onClick={fetchSyntheticPayload} 
                      className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 font-bold text-xs text-white rounded-lg cursor-pointer transition shadow-md"
                    >
                      Generate Payload
                    </button>
                  </div>
                </div>

                {syntheticPayload && (
                  <div className="flex items-center justify-between p-2.5 bg-slate-950 border border-indigo-500/30 rounded-lg text-xs font-mono">
                    <span className="truncate max-w-xl text-indigo-300">{syntheticPayload}</span>
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard.writeText(syntheticPayload);
                        alert("Payload copied! Paste it into any step input.");
                      }}
                      className="text-xs text-emerald-400 hover:underline cursor-pointer ml-3 font-sans shrink-0 font-semibold"
                    >
                      Copy to Clipboard
                    </button>
                  </div>
                )}
              </div>

              {/* Steps List */}
              <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-bold text-white">Defined Test Steps ({steps.length})</h2>
                  <button
                    onClick={addStep}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold cursor-pointer shadow-md"
                  >
                    <Plus size={14} /> Add Step
                  </button>
                </div>

                <div className="space-y-3">
                  {steps.map((st, idx) => (
                    <div key={idx} className="bg-slate-950/70 border border-slate-800/80 rounded-xl p-3 text-xs space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 font-mono text-cyan-400">
                          <span className="w-5 h-5 rounded-full bg-cyan-500/10 flex items-center justify-center text-[10px] font-bold">
                            {idx + 1}
                          </span>
                          <select
                            value={st.action}
                            onChange={(e) => updateStep(idx, "action", e.target.value)}
                            className="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-200"
                          >
                            {ACTION_TYPES.map((act) => <option key={act} value={act}>{act}</option>)}
                          </select>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <button onClick={() => deleteStep(idx)} className="text-slate-500 hover:text-rose-400 p-1 cursor-pointer">
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>

                      <div className="grid grid-cols-12 gap-2">
                        <div className="col-span-3">
                          <select
                            value={st.selector_type}
                            onChange={(e) => updateStep(idx, "selector_type", e.target.value)}
                            className="w-full bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-300"
                          >
                            {SELECTOR_TYPES.map((sel) => <option key={sel} value={sel}>{sel || "No Target"}</option>)}
                          </select>
                        </div>
                        <div className="col-span-4">
                          <input
                            type="text"
                            placeholder="Target Selector (e.g. body, button)"
                            value={st.selector}
                            onChange={(e) => updateStep(idx, "selector", e.target.value)}
                            className="w-full bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-200"
                          />
                        </div>
                        <div className="col-span-5">
                          <input
                            type="text"
                            placeholder="Input value or timeout ms"
                            value={st.value}
                            onChange={(e) => updateStep(idx, "value", e.target.value)}
                            className="w-full bg-slate-900 border border-slate-800 rounded px-2 py-1 text-slate-200"
                          />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Script Preview */}
            <div className="lg:col-span-4 space-y-6">
              <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 shadow-xl flex flex-col h-[580px]">
                <h3 className="text-xs font-bold text-slate-300 mb-3 flex items-center gap-1.5 uppercase tracking-wider font-mono">
                  <FileCode size={14} className="text-cyan-400" /> Playwright Script Preview
                </h3>
                <div className="flex-1 bg-slate-950 border border-slate-800 rounded-xl p-3 font-mono text-[11px] text-cyan-300 overflow-auto whitespace-pre leading-relaxed select-all">
                  {previewScript}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: EXECUTION RESULTS & VIEWSCREEN */}
        {activeTab === "results" && (
          <div className="space-y-6">
            <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-5 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Video size={18} className="text-cyan-400" /> Step-by-Step Execution Viewscreen & Telemetry
                </h2>
                <p className="text-xs text-slate-400 mt-1 font-mono">
                  Target: {targetUrl} | Headless Chromium 1366×768 Viewport
                </p>
              </div>
              {runResults && (
                <div className="flex items-center gap-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-bold font-mono ${
                    runResults.overall_status === "PASS"
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                      : runResults.overall_status === "FLAKY"
                      ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                      : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                  }`}>
                    {runResults.overall_status}
                  </span>
                  <a
                    href={`${API_BASE}/runs/${runResults.run_id}/report.pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs"
                  >
                    <FileText size={14} /> PDF
                  </a>
                  <a
                    href={`${API_BASE}/runs/${runResults.run_id}/report.xlsx`}
                    className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs"
                  >
                    <FileSpreadsheet size={14} /> Excel
                  </a>
                </div>
              )}
            </div>

            {/* STEP-BY-STEP VIEWSCREEN CINEMA SCREEN */}
            {runResults ? (
              <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6 shadow-2xl space-y-5">
                <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-1 rounded border border-cyan-500/20">
                      STEP #{activePlaybackIndex + 1} OF {runResults.step_results.length}
                    </span>
                    <span className="text-xs text-slate-300 font-mono">
                      Action: <span className="font-bold text-white uppercase">{currentPlaybackStep?.action}</span> ({currentPlaybackStep?.ms}ms)
                    </span>
                  </div>

                  {currentPlaybackStep?.screenshot_b64 && (
                    <button
                      onClick={() => setSelectedProof(currentPlaybackStep.screenshot_b64)}
                      className="text-xs text-cyan-400 hover:underline font-medium cursor-pointer flex items-center gap-1"
                    >
                      <Eye size={13} /> Fullscreen Snapshot
                    </button>
                  )}
                </div>

                <div className="flex justify-center items-center bg-slate-950 p-4 rounded-2xl border border-slate-800/80">
                  <div className="w-full max-w-4xl bg-slate-900 border-2 border-slate-700 rounded-xl overflow-hidden shadow-2xl">
                    <div className="flex items-center gap-1.5 py-2 px-3 bg-slate-950 border-b border-slate-800">
                      <span className="w-2.5 h-2.5 rounded-full bg-rose-500/80 inline-block" />
                      <span className="w-2.5 h-2.5 rounded-full bg-amber-500/80 inline-block" />
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500/80 inline-block" />
                      <span className="text-[10px] text-slate-400 font-mono ml-2 truncate">
                        Step #{currentPlaybackStep?.index}: {currentPlaybackStep?.action} — Output: {currentPlaybackStep?.actual || currentPlaybackStep?.error || "Done"}
                      </span>
                    </div>

                    <div className="bg-slate-950 flex justify-center items-center min-h-[380px] max-h-[480px] overflow-hidden">
                      {currentPlaybackStep?.screenshot_b64 ? (
                        <img
                          src={`data:image/png;base64,${currentPlaybackStep.screenshot_b64}`}
                          alt="Live Step State"
                          className="w-full h-auto object-cover object-top block"
                        />
                      ) : (
                        <div className="text-slate-600 font-mono text-xs flex flex-col items-center gap-2">
                          <Activity size={24} className="animate-spin text-slate-700" />
                          <span>No frame snapshot captured for this action</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 font-bold block">
                    Step Timeline (Click to view state at each step)
                  </span>
                  <div className="flex items-center gap-2 overflow-x-auto pb-2 pt-1">
                    {runResults.step_results.map((st, i) => (
                      <button
                        key={i}
                        onClick={() => setActivePlaybackIndex(i)}
                        className={`px-3.5 py-2 rounded-xl text-xs font-mono font-bold transition cursor-pointer shrink-0 flex items-center gap-2 border ${
                          activePlaybackIndex === i
                            ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-md ring-1 ring-cyan-500/30"
                            : "bg-slate-950/80 text-slate-400 border-slate-800 hover:text-white"
                        }`}
                      >
                        <span className={`w-2 h-2 rounded-full ${
                          st.status === 'PASS' ? 'bg-emerald-400' :
                          st.status === 'FLAKY' ? 'bg-amber-400' : 'bg-rose-500'
                        }`} />
                        <span>Step #{st.index}: {st.action}</span>
                        <span className="text-[10px] text-slate-500 font-normal">({st.ms}ms)</span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center text-slate-500 font-mono text-xs">
                No active test runs in this workspace. Run your suite in Test Builder to inspect viewscreen frames.
              </div>
            )}

            {/* ROOT CAUSE DIAGNOSTICS & REMEDIATION ADVICE */}
            {failedSteps.length > 0 && (
              <div className="bg-slate-900/90 border border-rose-500/40 rounded-2xl p-6 shadow-2xl space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2.5 text-rose-400 font-bold text-sm">
                    <AlertCircle size={20} />
                    <span>Root Cause Diagnostics & Remediation Advice</span>
                  </div>
                  <span className="text-xs font-mono bg-rose-500/10 text-rose-400 px-2.5 py-1 rounded-full border border-rose-500/20 font-bold">
                    {failedSteps.length} Step Failures Detected
                  </span>
                </div>

                <div className="space-y-4">
                  {failedSteps.map((fs, idx) => (
                    <div key={idx} className="bg-slate-950/80 border border-slate-800/90 rounded-xl p-5 space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="text-xs font-bold text-white flex items-center gap-2 font-mono">
                          <span className="w-6 h-6 rounded-lg bg-rose-500/20 text-rose-400 flex items-center justify-center">
                            #{fs.index}
                          </span>
                          <span>Failed Action: <span className="text-rose-400 font-bold uppercase">{fs.action}</span></span>
                        </div>
                        {fs.ms && <span className="text-[11px] font-mono text-slate-500">Execution time: {fs.ms}ms</span>}
                      </div>

                      <div className="p-4 bg-rose-500/10 border border-rose-500/25 rounded-xl space-y-1">
                        <div className="flex items-center gap-2 text-rose-400 font-bold text-xs">
                          <HelpCircle size={14} />
                          <span>Why the test failed (Root Cause):</span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed font-sans pl-5">
                          {fs.explanation || fs.error || "The browser encountered an unhandled DOM exception or assertion mismatch."}
                        </p>
                      </div>

                      <div className="p-4 bg-emerald-500/10 border border-emerald-500/25 rounded-xl space-y-1">
                        <div className="flex items-center gap-2 text-emerald-400 font-bold text-xs">
                          <Wrench size={14} />
                          <span>How to make it better (Recommended Fix):</span>
                        </div>
                        <p className="text-xs text-emerald-300/90 leading-relaxed font-sans pl-5 whitespace-pre-line">
                          {fs.suggestion || "Review element availability, add an explicit wait period, or loosen strict assertion constraints."}
                        </p>
                      </div>

                      <div className="flex items-center justify-end gap-3 pt-1">
                        {fs.screenshot_b64 && (
                          <button
                            onClick={() => setSelectedProof(fs.screenshot_b64)}
                            className="text-xs text-cyan-400 hover:underline font-mono cursor-pointer flex items-center gap-1"
                          >
                            <Eye size={13} /> View Proof Screenshot
                          </button>
                        )}
                        <button
                          onClick={() => logDefectFromStep(fs)}
                          className="px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 rounded-lg text-xs font-bold border border-rose-500/30 cursor-pointer flex items-center gap-1.5"
                        >
                          <Bug size={13} /> Log Defect to Tracker
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Results Table */}
            {runResults && (
              <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl overflow-hidden shadow-xl">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                    <tr>
                      <th className="py-3 px-4">#</th>
                      <th className="py-3 px-4">Action</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4">Duration</th>
                      <th className="py-3 px-4">Output / Error</th>
                      <th className="py-3 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {runResults.step_results.map((st, i) => (
                      <tr key={i} className={`hover:bg-slate-800/30 ${activePlaybackIndex === i ? 'bg-cyan-500/5' : ''}`}>
                        <td className="py-3 px-4 font-mono text-cyan-400">{st.index}</td>
                        <td className="py-3 px-4 font-medium text-white">{st.action}</td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                            st.status === "PASS" ? "bg-emerald-500/10 text-emerald-400" : 
                            st.status === "FLAKY" ? "bg-amber-500/10 text-amber-400" :
                            st.status === "FAIL" ? "bg-rose-500/10 text-rose-400" : "bg-slate-800 text-slate-400"
                          }`}>
                            {st.status}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono text-slate-400">{st.ms}ms</td>
                        <td className="py-3 px-4 max-w-md truncate">{st.error || st.actual || "Success"}</td>
                        <td className="py-3 px-4 text-right space-x-2">
                          <button onClick={() => setActivePlaybackIndex(i)} className="text-cyan-400 hover:underline cursor-pointer">
                            View on Screen
                          </button>
                          {st.status === "FAIL" && (
                            <button onClick={() => logDefectFromStep(st)} className="text-rose-400 hover:text-rose-300 font-semibold cursor-pointer ml-2">
                              Log Defect
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: AI DOM ANALYZER */}
        {activeTab === "ai" && (
          <div className="space-y-6">
            <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6 shadow-xl">
              <h2 className="text-base font-bold text-white flex items-center gap-2 mb-2">
                <Sparkles className="text-purple-400" size={18} /> AI DOM Analyzer & Generator
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Dissects target DOM hierarchies, finding input forms, search bars, and navigation flows to auto-generate structured test cases.
              </p>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={aiUrl}
                  onChange={(e) => setAiUrl(e.target.value)}
                  placeholder="https://leatherlaneatelier.store"
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 focus:outline-none focus:border-purple-500 font-mono"
                />
                <button
                  onClick={runAiAnalysis}
                  disabled={aiLoading}
                  className="px-6 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-xl text-sm font-semibold transition flex items-center gap-2 cursor-pointer disabled:opacity-50 shadow-md"
                >
                  {aiLoading ? <RefreshCw size={16} className="animate-spin" /> : <Sparkles size={16} />} Scan Page
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {aiSuggestions.map((sug, i) => (
                <div key={i} className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 hover:border-purple-500/40 transition">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20">
                      {sug.priority}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">{sug.type}</span>
                  </div>
                  <h3 className="text-sm font-bold text-white mb-2">{sug.title}</h3>
                  <button
                    onClick={() => applyAiSuggestion(sug)}
                    className="flex items-center gap-1.5 text-xs font-semibold text-purple-400 hover:text-purple-300 mt-2 cursor-pointer"
                  >
                    Load into Test Builder <ArrowRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: DEFECT TRACKER */}
        {activeTab === "defects" && (
          <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl overflow-hidden shadow-xl">
            <div className="p-6 border-b border-slate-800 flex items-center justify-between">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Bug className="text-rose-400" size={18} /> Logged Defects ({defects.length})
              </h2>
              <span className="text-xs text-slate-400 font-mono">
                Assigned to Tester: <span className="text-emerald-400 font-bold">{user?.name}</span>
              </span>
            </div>
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Code</th>
                  <th className="py-3 px-4">Title</th>
                  <th className="py-3 px-4">Severity</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Proof</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {defects.length > 0 ? (
                  defects.map((df, i) => (
                    <tr key={i} className="hover:bg-slate-800/30">
                      <td className="py-3 px-4 font-mono text-cyan-400 font-bold">{df.code}</td>
                      <td className="py-3 px-4 font-medium text-white">{df.title}</td>
                      <td className="py-3 px-4"><span className="text-rose-400 font-semibold">{df.severity}</span></td>
                      <td className="py-3 px-4">{df.status}</td>
                      <td className="py-3 px-4 text-right">
                        {df.screenshot_b64 && (
                          <button onClick={() => setSelectedProof(df.screenshot_b64)} className="text-cyan-400 hover:underline cursor-pointer">
                            View Proof
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="text-center py-12 text-slate-500 font-mono">
                      No defects logged for {user?.name || "this tester"} yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        {/* TAB 6: CI/CD PIPELINE */}
        {activeTab === "cicd" && (
          <div className="space-y-6">
            <div className="bg-slate-900/70 border border-slate-800/80 rounded-2xl p-6 shadow-xl">
              <h2 className="text-base font-bold text-white flex items-center gap-2 mb-2">
                <GitBranch className="text-amber-400" size={18} /> CI/CD Automation & GitHub Actions
              </h2>
              <p className="text-xs text-slate-400 mb-6">
                Trigger regression suites programmatically from pull requests and block deployments on test failures.
              </p>

              <div className="space-y-4">
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">GitHub Actions Workflow Template</label>
                  <pre className="bg-slate-950 border border-slate-800 p-4 rounded-xl text-xs font-mono text-amber-300/90 overflow-x-auto">
{`name: WebForge Automated Regression
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trigger WebForge Pipeline Suite
        run: |
          curl -X POST "${API_BASE}/api/run" \\
            -H "Content-Type: application/json" \\
            -d '{"project_id": 1, "suite_id": 1, "environment": "production"}'
`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Proof Modal */}
      {selectedProof && (
        <div className="fixed inset-0 z-50 bg-black/80 flex items-center justify-center p-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-4xl w-full p-6 relative">
            <button onClick={() => setSelectedProof(null)} className="absolute top-4 right-4 text-slate-400 hover:text-white cursor-pointer font-bold">✕</button>
            <h3 className="text-sm font-bold text-white mb-4">Screenshot Evidence Proof</h3>
            <div className="border border-slate-800 rounded-xl overflow-hidden max-h-[70vh] overflow-y-auto">
              <img src={`data:image/png;base64,${selectedProof}`} alt="Evidence" className="w-full object-contain" />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}